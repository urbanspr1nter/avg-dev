import unittest

from src.ppu.ppu import PPU
from src.memory.gb_memory import Memory


class TestPPUDefaults(unittest.TestCase):
    """Verify power-on default values for all PPU registers."""

    def setUp(self):
        self.ppu = PPU()

    def test_lcdc_default(self):
        self.assertEqual(self.ppu.read(0xFF40), 0x91)

    def test_stat_default(self):
        # Bit 7 always reads as 1, mode 2 at startup → 0x82
        self.assertEqual(self.ppu.read(0xFF41), 0x82)

    def test_scy_default(self):
        self.assertEqual(self.ppu.read(0xFF42), 0x00)

    def test_scx_default(self):
        self.assertEqual(self.ppu.read(0xFF43), 0x00)

    def test_ly_default(self):
        self.assertEqual(self.ppu.read(0xFF44), 0x00)

    def test_lyc_default(self):
        self.assertEqual(self.ppu.read(0xFF45), 0x00)

    def test_dma_default(self):
        self.assertEqual(self.ppu.read(0xFF46), 0x00)

    def test_bgp_default(self):
        self.assertEqual(self.ppu.read(0xFF47), 0xFC)

    def test_obp0_default(self):
        self.assertEqual(self.ppu.read(0xFF48), 0xFF)

    def test_obp1_default(self):
        self.assertEqual(self.ppu.read(0xFF49), 0xFF)

    def test_wy_default(self):
        self.assertEqual(self.ppu.read(0xFF4A), 0x00)

    def test_wx_default(self):
        self.assertEqual(self.ppu.read(0xFF4B), 0x00)


class TestPPUReadWrite(unittest.TestCase):
    """Read/write round-trip for all writable registers."""

    def setUp(self):
        self.ppu = PPU()

    def test_lcdc_readwrite(self):
        self.ppu.write(0xFF40, 0x55)
        self.assertEqual(self.ppu.read(0xFF40), 0x55)

    def test_scy_readwrite(self):
        self.ppu.write(0xFF42, 0xAB)
        self.assertEqual(self.ppu.read(0xFF42), 0xAB)

    def test_scx_readwrite(self):
        self.ppu.write(0xFF43, 0xCD)
        self.assertEqual(self.ppu.read(0xFF43), 0xCD)

    def test_lyc_readwrite(self):
        self.ppu.write(0xFF45, 0x90)
        self.assertEqual(self.ppu.read(0xFF45), 0x90)

    def test_dma_readwrite(self):
        self.ppu.write(0xFF46, 0xC0)
        self.assertEqual(self.ppu.read(0xFF46), 0xC0)

    def test_bgp_readwrite(self):
        self.ppu.write(0xFF47, 0xE4)
        self.assertEqual(self.ppu.read(0xFF47), 0xE4)

    def test_obp0_readwrite(self):
        self.ppu.write(0xFF48, 0xD2)
        self.assertEqual(self.ppu.read(0xFF48), 0xD2)

    def test_obp1_readwrite(self):
        self.ppu.write(0xFF49, 0x1C)
        self.assertEqual(self.ppu.read(0xFF49), 0x1C)

    def test_wy_readwrite(self):
        self.ppu.write(0xFF4A, 0x50)
        self.assertEqual(self.ppu.read(0xFF4A), 0x50)

    def test_wx_readwrite(self):
        self.ppu.write(0xFF4B, 0x07)
        self.assertEqual(self.ppu.read(0xFF4B), 0x07)

    def test_write_masks_to_8_bits(self):
        self.ppu.write(0xFF42, 0x1FF)
        self.assertEqual(self.ppu.read(0xFF42), 0xFF)


class TestPPUStatRegister(unittest.TestCase):
    """STAT (0xFF41) has special behavior: bits 0-2 read-only, bit 7 always 1."""

    def setUp(self):
        self.ppu = PPU()

    def test_stat_bit7_always_reads_1(self):
        self.ppu.write(0xFF41, 0x00)
        self.assertEqual(self.ppu.read(0xFF41) & 0x80, 0x80)

    def test_stat_writable_bits_3_to_6(self):
        self.ppu.write(0xFF41, 0x78)  # bits 3-6 all set
        self.assertEqual(self.ppu.read(0xFF41) & 0x78, 0x78)

    def test_stat_readonly_bits_0_to_2_not_writable(self):
        # Attempt to write bits 0-2 — they should remain unchanged (mode 2 at init)
        self.ppu.write(0xFF41, 0x07)  # try to set bits 0-2
        self.assertEqual(self.ppu.read(0xFF41) & 0x07, 0x02)

    def test_stat_preserves_readonly_bits(self):
        # Simulate hardware setting mode bits (bits 0-2) internally
        self.ppu._stat = 0x03  # mode 3
        self.ppu.write(0xFF41, 0x40)  # write bit 6
        # Bits 0-2 should be preserved, bit 6 written, bit 7 always 1
        self.assertEqual(self.ppu.read(0xFF41), 0x80 | 0x40 | 0x03)

    def test_stat_write_ignores_bit7(self):
        # Writing bit 7 has no effect (it always reads as 1 anyway)
        self.ppu.write(0xFF41, 0x80)
        # Bit 7 from read OR, mode 2 preserved in bits 0-1
        self.assertEqual(self.ppu.read(0xFF41), 0x82)


class TestPPULYRegister(unittest.TestCase):
    """LY (0xFF44) is read-only from CPU side; writing resets it to 0."""

    def setUp(self):
        self.ppu = PPU()

    def test_ly_read_only(self):
        # Set LY internally (as PPU hardware would)
        self.ppu._ly = 100
        self.assertEqual(self.ppu.read(0xFF44), 100)

    def test_ly_write_resets_to_zero(self):
        self.ppu._ly = 50
        self.ppu.write(0xFF44, 0xFF)  # any write resets to 0
        self.assertEqual(self.ppu.read(0xFF44), 0)


class TestPPUUnknownAddress(unittest.TestCase):
    """Reads from unmapped addresses return 0xFF."""

    def setUp(self):
        self.ppu = PPU()

    def test_read_out_of_range_returns_0xff(self):
        self.assertEqual(self.ppu.read(0xFF4C), 0xFF)


class TestPPUMemoryIntegration(unittest.TestCase):
    """CPU reads/writes to 0xFF40-0xFF4B are dispatched through the PPU."""

    def setUp(self):
        self.memory = Memory()
        self.ppu = PPU()
        self.memory.load_ppu(self.ppu)

    def test_memory_write_dispatches_to_ppu(self):
        self.memory.set_value(0xFF40, 0x55)
        self.assertEqual(self.ppu.read(0xFF40), 0x55)

    def test_memory_read_dispatches_to_ppu(self):
        self.ppu.write(0xFF47, 0xE4)
        self.assertEqual(self.memory.get_value(0xFF47), 0xE4)

    def test_memory_roundtrip_all_registers(self):
        addrs = list(range(0xFF40, 0xFF4C))
        for addr in addrs:
            if addr == 0xFF44:
                continue  # LY is read-only
            self.memory.set_value(addr, 0xAA)
            # STAT masks bits, so check only writable bits
            if addr == 0xFF41:
                self.assertEqual(self.memory.get_value(addr) & 0x78, 0x28)
            else:
                self.assertEqual(self.memory.get_value(addr), 0xAA,
                                 f"Round-trip failed for address {addr:#06X}")

    def test_memory_without_ppu_falls_through(self):
        """Without a PPU loaded, writes go to raw memory array."""
        mem = Memory()
        mem.set_value(0xFF40, 0x55)
        self.assertEqual(mem.memory[0xFF40], 0x55)


class TestPPUModeTiming(unittest.TestCase):
    """Mode state machine transitions at correct cycle thresholds."""

    def setUp(self):
        self.ppu = PPU()
        self.memory = Memory()
        self.memory.load_ppu(self.ppu)

    def test_starts_in_mode2(self):
        self.assertEqual(self.ppu._mode, 2)
        self.assertEqual(self.ppu.read(0xFF41) & 0x03, 2)

    def test_mode2_to_mode3_at_dot_80(self):
        self.ppu.tick(80)
        self.assertEqual(self.ppu._mode, 3)

    def test_stays_mode2_before_dot_80(self):
        self.ppu.tick(79)
        self.assertEqual(self.ppu._mode, 2)

    def test_mode3_to_mode0_at_dot_252(self):
        self.ppu.tick(252)
        self.assertEqual(self.ppu._mode, 0)

    def test_stays_mode3_before_dot_252(self):
        self.ppu.tick(251)
        self.assertEqual(self.ppu._mode, 3)

    def test_mode0_to_mode2_at_dot_456(self):
        """After 456 dots, LY increments and mode returns to 2."""
        self.ppu.tick(456)
        self.assertEqual(self.ppu._mode, 2)
        self.assertEqual(self.ppu._ly, 1)

    def test_full_visible_scanline_is_456_cycles(self):
        """One complete scanline = 456 T-cycles, LY advances by 1."""
        self.ppu.tick(456)
        self.assertEqual(self.ppu._ly, 1)
        self.assertEqual(self.ppu._dot, 0)

    def test_enters_vblank_at_ly_144(self):
        """After 144 visible scanlines, PPU enters V-Blank (mode 1)."""
        self.ppu.tick(144 * 456)
        self.assertEqual(self.ppu._ly, 144)
        self.assertEqual(self.ppu._mode, 1)

    def test_vblank_lasts_10_scanlines(self):
        """V-Blank spans scanlines 144-153 (10 scanlines)."""
        self.ppu.tick(144 * 456)  # Enter V-Blank
        for expected_ly in range(145, 154):
            self.ppu.tick(456)
            self.assertEqual(self.ppu._ly, expected_ly)
            self.assertEqual(self.ppu._mode, 1)

    def test_ly_wraps_to_0_after_153(self):
        """After scanline 153, LY wraps to 0 and mode returns to 2."""
        self.ppu.tick(154 * 456)  # Full frame
        self.assertEqual(self.ppu._ly, 0)
        self.assertEqual(self.ppu._mode, 2)

    def test_full_frame_is_70224_cycles(self):
        """One complete frame = 154 scanlines × 456 = 70,224 T-cycles."""
        self.ppu.tick(70224)
        self.assertEqual(self.ppu._ly, 0)
        self.assertEqual(self.ppu._dot, 0)
        self.assertEqual(self.ppu._mode, 2)

    def test_two_full_frames(self):
        """PPU correctly wraps across multiple frames."""
        self.ppu.tick(70224 * 2)
        self.assertEqual(self.ppu._ly, 0)
        self.assertEqual(self.ppu._dot, 0)

    def test_ly_advances_each_scanline(self):
        """LY increments by 1 for each 456-cycle scanline."""
        for expected_ly in range(10):
            self.assertEqual(self.ppu._ly, expected_ly)
            self.ppu.tick(456)


class TestPPUSTATMode(unittest.TestCase):
    """STAT register reflects current mode and LYC coincidence."""

    def setUp(self):
        self.ppu = PPU()

    def test_stat_reflects_mode_transitions(self):
        """STAT bits 0-1 match the current mode at each transition point."""
        # Mode 2 at start
        self.assertEqual(self.ppu.read(0xFF41) & 0x03, 2)
        # Mode 3 at dot 80
        self.ppu.tick(80)
        self.assertEqual(self.ppu.read(0xFF41) & 0x03, 3)
        # Mode 0 at dot 252
        self.ppu.tick(172)
        self.assertEqual(self.ppu.read(0xFF41) & 0x03, 0)
        # Mode 2 at dot 456 (next scanline)
        self.ppu.tick(204)
        self.assertEqual(self.ppu.read(0xFF41) & 0x03, 2)

    def test_stat_mode1_during_vblank(self):
        self.ppu.tick(144 * 456)
        self.assertEqual(self.ppu.read(0xFF41) & 0x03, 1)

    def test_lyc_coincidence_flag_set(self):
        """STAT bit 2 is set when LY == LYC."""
        self.ppu._lyc = 1
        self.ppu.tick(456)  # LY becomes 1
        self.assertTrue(self.ppu.read(0xFF41) & 0x04)

    def test_lyc_coincidence_flag_cleared(self):
        """STAT bit 2 is clear when LY != LYC."""
        self.ppu._lyc = 5
        self.ppu.tick(456)  # LY becomes 1, not 5
        self.assertFalse(self.ppu.read(0xFF41) & 0x04)

    def test_lyc_coincidence_at_ly0(self):
        """LYC match at LY=0 after frame wrap."""
        self.ppu._lyc = 0
        self.ppu.tick(154 * 456)  # Full frame, LY wraps to 0
        self.assertTrue(self.ppu.read(0xFF41) & 0x04)


class TestPPUVBlankInterrupt(unittest.TestCase):
    """V-Blank interrupt fires when entering scanline 144."""

    def setUp(self):
        self.memory = Memory()
        self.ppu = PPU()
        self.memory.load_ppu(self.ppu)
        # Clear IF register
        self.memory.memory[0xFF0F] = 0x00

    def test_vblank_sets_if_bit0(self):
        self.ppu.tick(144 * 456)  # Enter V-Blank
        self.assertEqual(self.memory.memory[0xFF0F] & 0x01, 0x01)

    def test_no_vblank_before_ly_144(self):
        self.ppu.tick(143 * 456)  # Just before V-Blank
        self.assertEqual(self.memory.memory[0xFF0F] & 0x01, 0x00)

    def test_vblank_fires_once_per_frame(self):
        """V-Blank interrupt fires once when entering mode 1, not every V-Blank scanline."""
        self.ppu.tick(144 * 456)  # Enter V-Blank
        self.memory.memory[0xFF0F] = 0x00  # Clear IF
        self.ppu.tick(456)  # Scanline 145
        # IF should NOT be set again (no new V-Blank entry)
        self.assertEqual(self.memory.memory[0xFF0F] & 0x01, 0x00)

    def test_vblank_fires_each_frame(self):
        """V-Blank interrupt fires once per frame (each time LY hits 144)."""
        self.ppu.tick(144 * 456)
        self.assertEqual(self.memory.memory[0xFF0F] & 0x01, 0x01)
        self.memory.memory[0xFF0F] = 0x00
        # Complete the rest of the frame + next 144 scanlines
        self.ppu.tick(10 * 456 + 144 * 456)
        self.assertEqual(self.memory.memory[0xFF0F] & 0x01, 0x01)


class TestPPULCDDisabled(unittest.TestCase):
    """When LCD is disabled (LCDC bit 7 = 0), PPU does not advance."""

    def setUp(self):
        self.ppu = PPU()

    def test_lcd_disabled_no_tick(self):
        self.ppu._lcdc = 0x00  # LCD off
        self.ppu.tick(1000)
        self.assertEqual(self.ppu._dot, 0)
        self.assertEqual(self.ppu._ly, 0)

    def test_lcd_reenabled_resumes(self):
        """PPU resumes ticking when LCD is re-enabled."""
        self.ppu._lcdc = 0x00  # LCD off
        self.ppu.tick(100)
        self.assertEqual(self.ppu._dot, 0)
        self.ppu._lcdc = 0x91  # LCD on
        self.ppu.tick(80)
        self.assertEqual(self.ppu._dot, 80)
        self.assertEqual(self.ppu._mode, 3)


class TestPPUCPUIntegration(unittest.TestCase):
    """CPU run loop ticks the PPU alongside the timer."""

    def setUp(self):
        from src.cpu.gb_cpu import CPU
        self.memory = Memory()
        self.cpu = CPU(memory=self.memory)
        self.ppu = PPU()
        self.memory.load_ppu(self.ppu)

    def test_cpu_ticks_ppu(self):
        """After CPU executes instructions, PPU dot counter has advanced."""
        # Write NOP (0x00) into memory — 4 T-cycles each
        self.memory.set_value(0x0000, 0x00)  # NOP
        self.memory.set_value(0x0001, 0x00)  # NOP
        self.memory.set_value(0x0002, 0x00)  # NOP
        self.cpu.run(max_cycles=12)  # 3 NOPs × 4 cycles = 12
        self.assertEqual(self.ppu._dot, 12)

    def test_cpu_ppu_mode_transition(self):
        """CPU executing enough NOPs causes PPU mode transition."""
        # Fill memory with NOPs
        for i in range(100):
            self.memory.set_value(i, 0x00)
        self.cpu.run(max_cycles=80)  # 20 NOPs × 4 = 80 cycles
        self.assertEqual(self.ppu._mode, 3)  # Should have transitioned to mode 3


if __name__ == '__main__':
    unittest.main()
