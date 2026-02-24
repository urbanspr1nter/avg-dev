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


class TestPPUFramebuffer(unittest.TestCase):
    """Framebuffer initialization and dimensions."""

    def setUp(self):
        self.ppu = PPU()

    def test_framebuffer_initialized_to_zeros(self):
        fb = self.ppu.get_framebuffer()
        for row in fb:
            for shade in row:
                self.assertEqual(shade, 0)

    def test_framebuffer_dimensions(self):
        fb = self.ppu.get_framebuffer()
        self.assertEqual(len(fb), 144)
        for row in fb:
            self.assertEqual(len(row), 160)


class _RenderTestBase(unittest.TestCase):
    """Base class that wires Memory + PPU and provides VRAM helpers."""

    def setUp(self):
        self.memory = Memory()
        self.ppu = PPU()
        self.memory.load_ppu(self.ppu)
        # Default LCDC: LCD on, BG on, unsigned tile data (bit 4),
        # tile map 0x9800 (bit 3 = 0)
        self.ppu._lcdc = 0x91  # 1001_0001

    def _write_tile(self, tile_addr, rows):
        """Write tile data at tile_addr.

        rows: list of 8 tuples (low_byte, high_byte).
        """
        for i, (lo, hi) in enumerate(rows):
            self.memory.memory[tile_addr + i * 2] = lo
            self.memory.memory[tile_addr + i * 2 + 1] = hi

    def _set_tile_map_entry(self, row, col, tile_index, base=0x9800):
        """Set tile map entry at (row, col) to tile_index."""
        self.memory.memory[base + row * 32 + col] = tile_index

    def _render_scanline(self, ly=0):
        """Force-render a specific scanline."""
        self.ppu._ly = ly
        self.ppu._render_scanline()


class TestPPUTileDecoding(_RenderTestBase):
    """Tile data decoding and palette application."""

    def test_solid_tile_renders_correct_shade(self):
        # Tile at index 0 → address 0x8000 (unsigned mode)
        # All pixels color index 3 → lo=0xFF, hi=0xFF
        solid_rows = [(0xFF, 0xFF)] * 8
        self._write_tile(0x8000, solid_rows)
        self._set_tile_map_entry(0, 0, 0)
        # BGP = 0xFC → color 3 maps to shade 3
        self.ppu._bgp = 0xFC
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        # First 8 pixels should be shade 3
        for px in range(8):
            self.assertEqual(fb[0][px], 3, f"pixel {px}")

    def test_alternating_tile_pattern(self):
        # lo=0xAA (10101010), hi=0x00 → color indices: 0,1,0,1,0,1,0,1
        alt_rows = [(0xAA, 0x00)] * 8
        self._write_tile(0x8000, alt_rows)
        self._set_tile_map_entry(0, 0, 0)
        # BGP = 0xE4 → identity palette (0→0, 1→1, 2→2, 3→3)
        self.ppu._bgp = 0xE4
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        for px in range(8):
            expected = 1 if (px % 2 == 0) else 0  # bit 7-0: 1,0,1,0,1,0,1,0
            self.assertEqual(fb[0][px], expected, f"pixel {px}")

    def test_palette_remapping(self):
        # Solid tile color index 3 (lo=0xFF, hi=0xFF)
        self._write_tile(0x8000, [(0xFF, 0xFF)] * 8)
        self._set_tile_map_entry(0, 0, 0)
        # BGP = 0x00 → all color indices map to shade 0
        self.ppu._bgp = 0x00
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        for px in range(8):
            self.assertEqual(fb[0][px], 0, f"pixel {px}")

        # Change palette: BGP = 0x54 → color 3 maps to shade 1
        # Binary: 01_01_01_00 → color 0→0, 1→1, 2→1, 3→1
        self.ppu._bgp = 0x54
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        for px in range(8):
            self.assertEqual(fb[0][px], 1, f"pixel {px}")


class TestPPUScrolling(_RenderTestBase):
    """SCX/SCY scroll offsets and wrapping."""

    def test_scx_offset(self):
        # Tile 0 at 0x8000: all color 0 (blank)
        self._write_tile(0x8000, [(0x00, 0x00)] * 8)
        # Tile 1 at 0x8010: all color 3 (solid)
        self._write_tile(0x8010, [(0xFF, 0xFF)] * 8)
        # Tile map: col 0 = tile 0, col 1 = tile 1
        self._set_tile_map_entry(0, 0, 0)
        self._set_tile_map_entry(0, 1, 1)
        self.ppu._bgp = 0xE4  # identity palette

        # No scroll → first 8 pixels from tile 0 (shade 0)
        self.ppu._scx = 0
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        for px in range(8):
            self.assertEqual(fb[0][px], 0, f"pixel {px}")

        # SCX = 8 → first 8 pixels now from tile 1 (shade 3)
        self.ppu._scx = 8
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        for px in range(8):
            self.assertEqual(fb[0][px], 3, f"pixel {px}")

    def test_scy_offset(self):
        # Tile 0: all color 0, Tile 1: all color 3
        self._write_tile(0x8000, [(0x00, 0x00)] * 8)
        self._write_tile(0x8010, [(0xFF, 0xFF)] * 8)
        # Row 0 = tile 0, Row 1 = tile 1
        self._set_tile_map_entry(0, 0, 0)
        self._set_tile_map_entry(1, 0, 1)
        self.ppu._bgp = 0xE4

        # SCY = 0, LY = 0 → tile row 0 → tile 0 → shade 0
        self.ppu._scy = 0
        self._render_scanline(0)
        self.assertEqual(self.ppu.get_framebuffer()[0][0], 0)

        # SCY = 8, LY = 0 → tile row 1 → tile 1 → shade 3
        self.ppu._scy = 8
        self._render_scanline(0)
        self.assertEqual(self.ppu.get_framebuffer()[0][0], 3)

    def test_scroll_wrapping(self):
        # Tile 1 at 0x8010: all color 3
        self._write_tile(0x8010, [(0xFF, 0xFF)] * 8)
        # Place tile 1 at tile map position (31, 31) — last row/col
        self._set_tile_map_entry(31, 31, 1)
        self.ppu._bgp = 0xE4

        # SCX = 248 (31*8), SCY = 248 → reads from tile map (31, 31)
        self.ppu._scx = 248
        self.ppu._scy = 248
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        for px in range(8):
            self.assertEqual(fb[0][px], 3, f"pixel {px}")


class TestPPUTileAddressing(_RenderTestBase):
    """LCDC bit 4 tile data addressing modes."""

    def test_unsigned_addressing_mode(self):
        # LCDC bit 4 = 1 (unsigned): tile 0 → 0x8000
        self.ppu._lcdc = 0x91  # bit 4 set
        self._write_tile(0x8000, [(0xFF, 0xFF)] * 8)
        self._set_tile_map_entry(0, 0, 0)
        self.ppu._bgp = 0xE4
        self._render_scanline(0)
        self.assertEqual(self.ppu.get_framebuffer()[0][0], 3)

    def test_signed_addressing_mode(self):
        # LCDC bit 4 = 0 (signed): tile index 0 → 0x9000
        self.ppu._lcdc = 0x81  # bit 4 clear
        self._write_tile(0x9000, [(0xFF, 0xFF)] * 8)
        self._set_tile_map_entry(0, 0, 0)
        self.ppu._bgp = 0xE4
        self._render_scanline(0)
        self.assertEqual(self.ppu.get_framebuffer()[0][0], 3)

    def test_signed_addressing_negative_index(self):
        # Tile index 128 (0x80) → signed = -128 → 0x9000 + (-128)*16 = 0x8800
        self.ppu._lcdc = 0x81  # bit 4 clear
        self._write_tile(0x8800, [(0xFF, 0xFF)] * 8)
        self._set_tile_map_entry(0, 0, 128)
        self.ppu._bgp = 0xE4
        self._render_scanline(0)
        self.assertEqual(self.ppu.get_framebuffer()[0][0], 3)


class TestPPURenderASCII(unittest.TestCase):
    """ASCII framebuffer rendering."""

    def setUp(self):
        self.ppu = PPU()

    def test_render_ascii_returns_string(self):
        result = self.ppu.render_ascii()
        self.assertIsInstance(result, str)
        lines = result.split("\n")
        self.assertEqual(len(lines), 144)
        for line in lines:
            self.assertEqual(len(line), 160)

    def test_render_ascii_shade_mapping(self):
        # Set specific shades and verify ASCII output
        self.ppu._framebuffer[0][0] = 0
        self.ppu._framebuffer[0][1] = 1
        self.ppu._framebuffer[0][2] = 2
        self.ppu._framebuffer[0][3] = 3
        result = self.ppu.render_ascii()
        first_line = result.split("\n")[0]
        self.assertEqual(first_line[0], " ")
        self.assertEqual(first_line[1], "░")
        self.assertEqual(first_line[2], "▒")
        self.assertEqual(first_line[3], "█")


class TestPPUWindowRendering(_RenderTestBase):
    """Window overlay rendering."""

    def setUp(self):
        super().setUp()
        # BG tile 0: all shade 0 (blank)
        self._write_tile(0x8000, [(0x00, 0x00)] * 8)
        # Window tile 1: all shade 3 (solid)
        self._write_tile(0x8010, [(0xFF, 0xFF)] * 8)
        # BG map: all tile 0
        for r in range(32):
            for c in range(32):
                self._set_tile_map_entry(r, c, 0, base=0x9800)
        # Window map: all tile 1 (at 0x9C00 — LCDC bit 6 default in these tests)
        for r in range(32):
            for c in range(32):
                self._set_tile_map_entry(r, c, 1, base=0x9C00)
        self.ppu._bgp = 0xE4  # identity palette

    def _enable_window(self, wy=0, wx=7):
        """Enable window with LCDC bit 5 and bit 6 (map at 0x9C00)."""
        # bit 7=LCD on, bit 5=window on, bit 6=window map 0x9C00, bit 4=unsigned, bit 0=BG on
        self.ppu._lcdc = 0xF1  # 1111_0001
        self.ppu._wy = wy
        self.ppu._wx = wx

    def test_window_disabled_by_lcdc_bit5(self):
        # LCDC bit 5 = 0, window should not render
        self.ppu._lcdc = 0x91  # bit 5 clear
        self.ppu._wy = 0
        self.ppu._wx = 7
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        # All pixels should be shade 0 (BG only)
        for px in range(160):
            self.assertEqual(fb[0][px], 0, f"pixel {px}")

    def test_window_basic_overlay(self):
        # WY=0, WX=7 → window covers entire screen
        self._enable_window(wy=0, wx=7)
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        # All pixels should be shade 3 (window tile)
        for px in range(160):
            self.assertEqual(fb[0][px], 3, f"pixel {px}")

    def test_window_partial_overlay(self):
        # WX=87 → window starts at pixel 80
        self._enable_window(wy=0, wx=87)
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        # Pixels 0-79: BG (shade 0)
        for px in range(80):
            self.assertEqual(fb[0][px], 0, f"pixel {px}")
        # Pixels 80-159: window (shade 3)
        for px in range(80, 160):
            self.assertEqual(fb[0][px], 3, f"pixel {px}")

    def test_window_wy_offset(self):
        # WY=4 → scanlines 0-3 show BG, scanline 4 shows window
        self._enable_window(wy=4, wx=7)
        for ly in range(4):
            self._render_scanline(ly)
            self.assertEqual(self.ppu.get_framebuffer()[ly][0], 0,
                             f"scanline {ly} should be BG")
        self._render_scanline(4)
        self.assertEqual(self.ppu.get_framebuffer()[4][0], 3,
                         "scanline 4 should be window")

    def test_window_line_counter_increments(self):
        # Window tile 2 at 0x8020: all shade 1 (lo=0xFF, hi=0x00 → color 1)
        self._write_tile(0x8020, [(0xFF, 0x00)] * 8)
        # Window map row 0 = tile 1 (shade 3), row 1 = tile 2 (shade 1)
        for c in range(32):
            self._set_tile_map_entry(0, c, 1, base=0x9C00)
            self._set_tile_map_entry(1, c, 2, base=0x9C00)
        self._enable_window(wy=0, wx=7)

        # Render 8 scanlines (tile row 0), then scanline 8 (tile row 1)
        for ly in range(8):
            self._render_scanline(ly)
            self.assertEqual(self.ppu.get_framebuffer()[ly][0], 3,
                             f"scanline {ly} should be shade 3 (tile row 0)")
        self._render_scanline(8)
        self.assertEqual(self.ppu.get_framebuffer()[8][0], 1,
                         "scanline 8 should be shade 1 (tile row 1)")

    def test_window_tile_map_lcdc_bit6(self):
        # Put different tile in 0x9800 window map
        # Window tile 2: all shade 1
        self._write_tile(0x8020, [(0xFF, 0x00)] * 8)
        for c in range(32):
            self._set_tile_map_entry(0, c, 2, base=0x9800)
        # LCDC bit 6 = 0 → window reads from 0x9800
        self.ppu._lcdc = 0xB1  # 1011_0001 (bit 6 clear, bit 5 set)
        self.ppu._wy = 0
        self.ppu._wx = 7
        self._render_scanline(0)
        self.assertEqual(self.ppu.get_framebuffer()[0][0], 1,
                         "should read tile 2 (shade 1) from 0x9800 map")

    def test_window_uses_same_tile_data_addressing(self):
        # Signed mode (LCDC bit 4 = 0): tile index 0 → 0x9000
        self._write_tile(0x9000, [(0xFF, 0xFF)] * 8)
        for c in range(32):
            self._set_tile_map_entry(0, c, 0, base=0x9C00)
        # LCDC: LCD on, window on, window map 0x9C00, bit 4 clear (signed)
        self.ppu._lcdc = 0xE1  # 1110_0001
        self.ppu._wy = 0
        self.ppu._wx = 7
        self._render_scanline(0)
        self.assertEqual(self.ppu.get_framebuffer()[0][0], 3,
                         "window should use signed tile data addressing")


if __name__ == '__main__':
    unittest.main()
