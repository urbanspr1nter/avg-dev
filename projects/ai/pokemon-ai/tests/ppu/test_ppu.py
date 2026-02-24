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


class TestPPUSpriteRendering(_RenderTestBase):
    """Sprite (OBJ) layer rendering."""

    def setUp(self):
        super().setUp()
        # Identity palette for BG
        self.ppu._bgp = 0xE4
        # Identity palettes for sprites
        self.ppu._obp0 = 0xE4
        self.ppu._obp1 = 0xE4
        # Enable sprites: LCDC bit 1
        self.ppu._lcdc |= 0x02  # 0x93

    def _write_sprite(self, index, y, x, tile, attrs=0):
        """Write a 4-byte OAM entry at the given sprite index (0-39)."""
        base = 0xFE00 + index * 4
        self.memory.memory[base] = y
        self.memory.memory[base + 1] = x
        self.memory.memory[base + 2] = tile
        self.memory.memory[base + 3] = attrs

    def test_sprites_disabled_by_lcdc_bit1(self):
        """When LCDC bit 1 = 0, sprites are not drawn."""
        self.ppu._lcdc &= ~0x02  # clear bit 1
        # Solid sprite tile at index 1
        self._write_tile(0x8010, [(0xFF, 0xFF)] * 8)
        self._write_sprite(0, y=16, x=8, tile=1)  # screen pos (0, 0)
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        for px in range(8):
            self.assertEqual(fb[0][px], 0, f"pixel {px} should be BG (shade 0)")

    def test_basic_sprite_8x8(self):
        """Single 8x8 sprite renders correct pixels."""
        # Tile 1: all color 3
        self._write_tile(0x8010, [(0xFF, 0xFF)] * 8)
        self._write_sprite(0, y=16, x=8, tile=1)  # screen (0, 0)
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        for px in range(8):
            self.assertEqual(fb[0][px], 3, f"pixel {px}")
        # Pixel 8 should be BG (shade 0)
        self.assertEqual(fb[0][8], 0)

    def test_sprite_transparency(self):
        """Color 0 pixels in sprite show BG underneath."""
        # BG tile 0: all color 1 → shade 1
        self._write_tile(0x8000, [(0xFF, 0x00)] * 8)
        self._set_tile_map_entry(0, 0, 0)
        # Sprite tile 1: alternating — lo=0xAA (10101010), hi=0x00 → colors 0,1,0,1...
        self._write_tile(0x8010, [(0xAA, 0x00)] * 8)
        self._write_sprite(0, y=16, x=8, tile=1)
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        for px in range(8):
            if px % 2 == 0:
                # Sprite color 1 → shade 1
                self.assertEqual(fb[0][px], 1, f"pixel {px} sprite")
            else:
                # Sprite color 0 (transparent) → BG color 1 → shade 1
                self.assertEqual(fb[0][px], 1, f"pixel {px} BG shows through")

    def test_sprite_palette_obp0_obp1(self):
        """Attr bit 4 selects OBP0 vs OBP1."""
        # OBP0: color 3 → shade 1.  0x54 = 01_01_01_00
        self.ppu._obp0 = 0x54
        # OBP1: color 3 → shade 2.  0xA4 = 10_10_01_00
        self.ppu._obp1 = 0xA4
        # Tile 1: all color 3
        self._write_tile(0x8010, [(0xFF, 0xFF)] * 8)

        # Sprite using OBP0 (attr bit 4 = 0)
        self._write_sprite(0, y=16, x=8, tile=1, attrs=0x00)
        self._render_scanline(0)
        self.assertEqual(self.ppu.get_framebuffer()[0][0], 1)

        # Sprite using OBP1 (attr bit 4 = 1)
        self._write_sprite(0, y=16, x=8, tile=1, attrs=0x10)
        self._render_scanline(0)
        self.assertEqual(self.ppu.get_framebuffer()[0][0], 2)

    def test_sprite_x_flip(self):
        """Attr bit 5 mirrors tile horizontally."""
        # Tile 1 row 0: lo=0x80 (10000000), hi=0x00 → pixel 0=color 1, rest=0
        self._write_tile(0x8010, [(0x80, 0x00)] * 8)

        # No flip: pixel 0 = shade 1, pixel 7 = shade 0
        self._write_sprite(0, y=16, x=8, tile=1, attrs=0x00)
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        self.assertEqual(fb[0][0], 1)
        self.assertEqual(fb[0][7], 0)

        # X-flip: pixel 0 = shade 0, pixel 7 = shade 1
        self._write_sprite(0, y=16, x=8, tile=1, attrs=0x20)
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        self.assertEqual(fb[0][0], 0)
        self.assertEqual(fb[0][7], 1)

    def test_sprite_y_flip(self):
        """Attr bit 6 mirrors tile vertically."""
        # Tile 1: row 0 = color 3, rows 1-7 = color 0
        rows = [(0xFF, 0xFF)] + [(0x00, 0x00)] * 7
        self._write_tile(0x8010, rows)

        # No flip: LY=0 → row 0 → shade 3
        self._write_sprite(0, y=16, x=8, tile=1, attrs=0x00)
        self._render_scanline(0)
        self.assertEqual(self.ppu.get_framebuffer()[0][0], 3)

        # No flip: LY=7 → row 7 → shade 0 (BG)
        self._render_scanline(7)
        self.assertEqual(self.ppu.get_framebuffer()[7][0], 0)

        # Y-flip: LY=0 → reads row 7 (color 0, transparent) → BG shade 0
        self._write_sprite(0, y=16, x=8, tile=1, attrs=0x40)
        self._render_scanline(0)
        self.assertEqual(self.ppu.get_framebuffer()[0][0], 0)

        # Y-flip: LY=7 → reads row 0 (color 3) → shade 3
        self._render_scanline(7)
        self.assertEqual(self.ppu.get_framebuffer()[7][0], 3)

    def test_sprite_8x16_mode(self):
        """LCDC bit 2 enables 8x16 sprites; tile index bit 0 masked."""
        self.ppu._lcdc |= 0x04  # 8x16 mode
        # Top tile (index 0): all color 1
        self._write_tile(0x8000, [(0xFF, 0x00)] * 8)
        # Bottom tile (index 1): all color 3
        self._write_tile(0x8010, [(0xFF, 0xFF)] * 8)
        # Sprite with tile index 1 → masked to 0 (top=0, bottom=1)
        self._write_sprite(0, y=16, x=8, tile=1)
        # LY=0 → top tile → color 1 → shade 1
        self._render_scanline(0)
        self.assertEqual(self.ppu.get_framebuffer()[0][0], 1)
        # LY=8 → bottom tile → color 3 → shade 3
        self._render_scanline(8)
        self.assertEqual(self.ppu.get_framebuffer()[8][0], 3)

    def test_sprite_8x16_y_flip(self):
        """8x16 mode with Y-flip swaps top and bottom tiles."""
        self.ppu._lcdc |= 0x04  # 8x16 mode
        # Top tile (index 0): all color 1
        self._write_tile(0x8000, [(0xFF, 0x00)] * 8)
        # Bottom tile (index 1): all color 3
        self._write_tile(0x8010, [(0xFF, 0xFF)] * 8)
        # Sprite with Y-flip
        self._write_sprite(0, y=16, x=8, tile=0, attrs=0x40)
        # LY=0 with Y-flip → row_in_sprite=15, flipped → reads bottom tile row 7 → color 3
        self._render_scanline(0)
        self.assertEqual(self.ppu.get_framebuffer()[0][0], 3)
        # LY=8 with Y-flip → row_in_sprite=8, flipped to 7 → reads top tile row 7 → color 1
        self._render_scanline(8)
        self.assertEqual(self.ppu.get_framebuffer()[8][0], 1)

    def test_sprite_bg_priority(self):
        """Attr bit 7: sprite hidden behind non-zero BG color."""
        # BG tile 0: all color 2 → shade 2
        self._write_tile(0x8000, [(0x00, 0xFF)] * 8)
        self._set_tile_map_entry(0, 0, 0)
        # Sprite tile 1: all color 3
        self._write_tile(0x8010, [(0xFF, 0xFF)] * 8)

        # Without BG priority → sprite wins
        self._write_sprite(0, y=16, x=8, tile=1, attrs=0x00)
        self._render_scanline(0)
        self.assertEqual(self.ppu.get_framebuffer()[0][0], 3)

        # With BG priority (bit 7) → BG color 2 (non-zero) hides sprite
        self._write_sprite(0, y=16, x=8, tile=1, attrs=0x80)
        self._render_scanline(0)
        self.assertEqual(self.ppu.get_framebuffer()[0][0], 2)

    def test_sprite_bg_priority_bg_color_zero(self):
        """BG priority sprite is visible where BG color index is 0."""
        # BG tile 0: all color 0
        self._write_tile(0x8000, [(0x00, 0x00)] * 8)
        self._set_tile_map_entry(0, 0, 0)
        # Sprite tile 1: all color 3
        self._write_tile(0x8010, [(0xFF, 0xFF)] * 8)
        # BG priority set, but BG color is 0 → sprite visible
        self._write_sprite(0, y=16, x=8, tile=1, attrs=0x80)
        self._render_scanline(0)
        self.assertEqual(self.ppu.get_framebuffer()[0][0], 3)

    def test_sprite_10_per_scanline_limit(self):
        """Only first 10 sprites on a scanline are drawn; 11th is dropped."""
        # Tile 1: all color 3
        self._write_tile(0x8010, [(0xFF, 0xFF)] * 8)
        # Place 11 sprites on LY=0, each at different X
        for i in range(11):
            self._write_sprite(i, y=16, x=8 + i * 8, tile=1)
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        # Sprites 0-9 (X pixels 0-79) should be drawn
        for px in range(80):
            self.assertEqual(fb[0][px], 3, f"pixel {px} should be sprite")
        # Sprite 10 (X pixels 80-87) should NOT be drawn
        for px in range(80, 88):
            self.assertEqual(fb[0][px], 0, f"pixel {px} should be BG (11th sprite dropped)")

    def test_sprite_priority_lower_x_wins(self):
        """Overlapping sprites: lower X has higher priority."""
        # Tile 1: all color 1 (shade 1)
        self._write_tile(0x8010, [(0xFF, 0x00)] * 8)
        # Tile 2: all color 3 (shade 3)
        self._write_tile(0x8020, [(0xFF, 0xFF)] * 8)
        # Sprite 0 (OAM 0) at X=12 (overlaps pixels 4-11), tile 2 (shade 3)
        self._write_sprite(0, y=16, x=12, tile=2)
        # Sprite 1 (OAM 1) at X=8 (overlaps pixels 0-7), tile 1 (shade 1)
        self._write_sprite(1, y=16, x=8, tile=1)
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        # Pixels 4-7 overlap: sprite 1 (X=8, lower) wins → shade 1
        for px in range(4, 8):
            self.assertEqual(fb[0][px], 1, f"pixel {px}: lower X wins")
        # Pixels 8-11: only sprite 0 → shade 3
        for px in range(8, 12):
            self.assertEqual(fb[0][px], 3, f"pixel {px}: only higher X sprite")

    def test_sprite_priority_same_x_lower_oam_wins(self):
        """Same X position: lower OAM index has priority."""
        # Tile 1: all color 1 (shade 1)
        self._write_tile(0x8010, [(0xFF, 0x00)] * 8)
        # Tile 2: all color 3 (shade 3)
        self._write_tile(0x8020, [(0xFF, 0xFF)] * 8)
        # OAM 0 at X=8, tile 1 (shade 1) — lower OAM index
        self._write_sprite(0, y=16, x=8, tile=1)
        # OAM 5 at X=8, tile 2 (shade 3) — higher OAM index
        self._write_sprite(5, y=16, x=8, tile=2)
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        # Lower OAM index (0) wins
        for px in range(8):
            self.assertEqual(fb[0][px], 1, f"pixel {px}: lower OAM wins")

    def test_sprite_offscreen_clipping(self):
        """Sprites partially off-screen are clipped, not skipped."""
        # Tile 1: all color 3
        self._write_tile(0x8010, [(0xFF, 0xFF)] * 8)
        # Sprite at X=4 → screen X = -4, pixels 0-3 visible (cols 4-7 of tile)
        self._write_sprite(0, y=16, x=4, tile=1)
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        for px in range(4):
            self.assertEqual(fb[0][px], 3, f"pixel {px} should show clipped sprite")
        # Right edge: sprite at X=161 → screen X=153, pixels 153-159 visible, cols 7+ clipped
        self._write_sprite(1, y=16, x=161, tile=1)
        self._render_scanline(0)
        fb = self.ppu.get_framebuffer()
        for px in range(153, 160):
            self.assertEqual(fb[0][px], 3, f"pixel {px}")


class TestPPUSTATInterrupts(unittest.TestCase):
    """STAT interrupt (IF bit 1) fires on rising edge of enabled conditions."""

    def setUp(self):
        self.memory = Memory()
        self.ppu = PPU()
        self.memory.load_ppu(self.ppu)
        self.memory.memory[0xFF0F] = 0x00  # Clear IF

    def _get_stat_irq(self):
        """Return IF bit 1 (STAT interrupt pending)."""
        return self.memory.memory[0xFF0F] & 0x02

    def _clear_if(self):
        self.memory.memory[0xFF0F] = 0x00

    def test_mode0_hblank_stat_interrupt(self):
        """STAT bit 3 set: entering H-Blank fires STAT interrupt."""
        self.ppu.write(0xFF41, 0x08)  # bit 3 = mode 0 select
        self.ppu.tick(252)  # reach mode 0
        self.assertTrue(self._get_stat_irq())

    def test_mode1_vblank_stat_interrupt(self):
        """STAT bit 4 set: entering V-Blank fires STAT interrupt."""
        self.ppu.write(0xFF41, 0x10)  # bit 4 = mode 1 select
        self.ppu.tick(144 * 456)  # reach LY=144, mode 1
        self.assertTrue(self._get_stat_irq())

    def test_mode2_oam_stat_interrupt(self):
        """STAT bit 5 set: entering OAM Scan fires STAT interrupt."""
        self.ppu.write(0xFF41, 0x20)  # bit 5 = mode 2 select
        # PPU starts in mode 2 at LY=0. The initial state has _stat_irq_line=False,
        # so the first _set_mode(2) call should trigger. Tick to next scanline.
        self._clear_if()
        self.ppu.tick(456)  # complete scanline 0, enter mode 2 at LY=1
        self.assertTrue(self._get_stat_irq())

    def test_lyc_stat_interrupt(self):
        """STAT bit 6 set: LY==LYC match fires STAT interrupt."""
        self.ppu.write(0xFF41, 0x40)  # bit 6 = LYC select
        self.ppu._lyc = 3
        self.ppu.tick(3 * 456)  # LY reaches 3
        self.assertTrue(self._get_stat_irq())

    def test_stat_interrupt_not_fired_when_disabled(self):
        """No STAT interrupt fires when bits 3-6 are all clear."""
        self.ppu.write(0xFF41, 0x00)  # all selects off
        self.ppu.tick(252)  # mode 0
        self.assertFalse(self._get_stat_irq())
        self.ppu.tick(204)  # mode 2
        self.assertFalse(self._get_stat_irq())
        self.ppu.tick(143 * 456)  # mode 1 (V-Blank)
        self.assertFalse(self._get_stat_irq())

    def test_mode0_stat_not_fired_without_bit3(self):
        """Only bit 4 set: entering mode 0 does NOT fire STAT interrupt."""
        self.ppu.write(0xFF41, 0x10)  # only V-Blank select
        self.ppu.tick(252)  # enter mode 0
        self.assertFalse(self._get_stat_irq())

    def test_lyc_stat_not_fired_without_bit6(self):
        """LYC match without bit 6 set does not fire STAT interrupt."""
        self.ppu.write(0xFF41, 0x08)  # only mode 0 select
        self.ppu._lyc = 1
        self._clear_if()
        # Tick past mode 0 on scanline 0 (will fire mode 0 interrupt), then clear
        self.ppu.tick(456)  # LY becomes 1 = LYC, but bit 6 not set
        self._clear_if()
        # We're now in mode 2 at LY=1. The LYC flag is set but bit 6 is not enabled.
        # Tick through to mode 3 — no STAT interrupt should fire from LYC.
        self.ppu.tick(80)  # mode 3
        self.assertFalse(self._get_stat_irq())

    def test_rising_edge_no_duplicate(self):
        """Mode 2 + LYC match on same scanline: only one interrupt fires."""
        self.ppu.write(0xFF41, 0x60)  # bits 5+6: mode 2 select + LYC select
        self.ppu._lyc = 1
        self._clear_if()
        self.ppu.tick(456)  # LY becomes 1, enter mode 2 AND LYC match
        # Only one STAT interrupt should have fired (rising edge)
        self.assertTrue(self._get_stat_irq())
        # Clear IF and verify no additional interrupt fires from the same state
        self._clear_if()
        self.ppu.tick(1)  # one more dot, still in mode 2 with LYC match
        self.assertFalse(self._get_stat_irq())

    def test_stat_irq_line_stays_high(self):
        """If line is already high from mode 2, LYC match doesn't re-trigger."""
        # Enable mode 2 interrupt only first
        self.ppu.write(0xFF41, 0x20)  # bit 5: mode 2 select
        self.ppu._lyc = 1
        self._clear_if()
        self.ppu.tick(456)  # enter mode 2 at LY=1 → fires
        self.assertTrue(self._get_stat_irq())
        self._clear_if()
        # Now also enable LYC select — line is already high from mode 2
        self.ppu.write(0xFF41, 0x60)  # bits 5+6
        # Still in mode 2 with LYC match — line was already high, no new interrupt
        self.assertFalse(self._get_stat_irq())

    def test_stat_interrupt_each_hblank(self):
        """STAT interrupt fires on each H-Blank entry across scanlines."""
        self.ppu.write(0xFF41, 0x08)  # bit 3: mode 0 select
        for ly in range(3):
            self._clear_if()
            # Tick to mode 0 on this scanline
            if ly == 0:
                self.ppu.tick(252)  # first scanline: 252 dots to mode 0
            else:
                self.ppu.tick(456 - 252)  # finish previous scanline
                self._clear_if()
                self.ppu.tick(252)  # next scanline to mode 0
            self.assertTrue(self._get_stat_irq(),
                            f"STAT interrupt should fire at H-Blank on scanline {ly}")

    def test_stat_interrupt_coexists_with_vblank(self):
        """Mode 1 STAT interrupt fires alongside V-Blank interrupt at LY=144."""
        self.ppu.write(0xFF41, 0x10)  # bit 4: mode 1 select
        self.ppu.tick(144 * 456)
        # Both IF bit 0 (V-Blank) and IF bit 1 (STAT) should be set
        self.assertTrue(self.memory.memory[0xFF0F] & 0x01, "V-Blank IF bit")
        self.assertTrue(self.memory.memory[0xFF0F] & 0x02, "STAT IF bit")

    def test_lyc_interrupt_at_ly0(self):
        """LYC=0: STAT interrupt fires when LY wraps back to 0."""
        self.ppu.write(0xFF41, 0x40)  # bit 6: LYC select
        self.ppu._lyc = 0
        # LY starts at 0 and LYC=0, but _stat_irq_line starts False.
        # The first _update_lyc_flag with mode transition should catch it.
        # Tick a full frame so LY wraps to 0.
        self._clear_if()
        self.ppu.tick(154 * 456)  # full frame, LY back to 0
        self.assertTrue(self._get_stat_irq())


class TestOAMDMA(unittest.TestCase):
    """OAM DMA transfer triggered by writing to 0xFF46."""

    def setUp(self):
        self.memory = Memory()
        self.ppu = PPU()
        self.memory.load_ppu(self.ppu)

    def test_dma_copies_160_bytes(self):
        """Writing 0xC0 to DMA copies 160 bytes from 0xC000 to OAM."""
        for i in range(160):
            self.memory.memory[0xC000 + i] = i & 0xFF
        self.ppu.write(0xFF46, 0xC0)
        for i in range(160):
            self.assertEqual(self.memory.memory[0xFE00 + i], i & 0xFF,
                             f"OAM byte {i}")

    def test_dma_from_different_source(self):
        """DMA copies from source_page * 0x100."""
        for i in range(160):
            self.memory.memory[0xD000 + i] = (0x80 + i) & 0xFF
        self.ppu.write(0xFF46, 0xD0)
        for i in range(160):
            self.assertEqual(self.memory.memory[0xFE00 + i], (0x80 + i) & 0xFF,
                             f"OAM byte {i}")

    def test_dma_register_readable(self):
        """DMA register reads back the written value."""
        self.ppu.write(0xFF46, 0xC0)
        self.assertEqual(self.ppu.read(0xFF46), 0xC0)

    def test_dma_preserves_oam_beyond_160(self):
        """DMA only copies 160 bytes; 0xFEA0+ unchanged."""
        self.memory.memory[0xFEA0] = 0x42
        self.ppu.write(0xFF46, 0xC0)
        self.assertEqual(self.memory.memory[0xFEA0], 0x42)

    def test_dma_without_memory_no_crash(self):
        """PPU without memory wired doesn't crash on DMA."""
        ppu = PPU()  # no memory
        ppu.write(0xFF46, 0xC0)  # should not raise


class TestVRAMOAMAccessRestrictions(unittest.TestCase):
    """VRAM/OAM access restrictions based on PPU mode."""

    def setUp(self):
        self.memory = Memory()
        self.ppu = PPU()
        self.memory.load_ppu(self.ppu)
        # Pre-fill VRAM and OAM with known values
        self.memory.memory[0x8000] = 0xAB
        self.memory.memory[0x9FFF] = 0xCD
        self.memory.memory[0xFE00] = 0x11
        self.memory.memory[0xFE9F] = 0x22

    def test_vram_read_returns_ff_during_mode3(self):
        self.ppu._mode = 3
        self.assertEqual(self.memory.get_value(0x8000), 0xFF)
        self.assertEqual(self.memory.get_value(0x9FFF), 0xFF)

    def test_vram_read_normal_outside_mode3(self):
        for mode in (0, 1, 2):
            self.ppu._mode = mode
            self.assertEqual(self.memory.get_value(0x8000), 0xAB,
                             f"mode {mode}")
            self.assertEqual(self.memory.get_value(0x9FFF), 0xCD,
                             f"mode {mode}")

    def test_vram_write_ignored_during_mode3(self):
        self.ppu._mode = 3
        self.memory.set_value(0x8000, 0xFF)
        # Verify underlying memory unchanged
        self.assertEqual(self.memory.memory[0x8000], 0xAB)

    def test_vram_write_normal_outside_mode3(self):
        for mode in (0, 1, 2):
            self.ppu._mode = mode
            self.memory.set_value(0x8000, 0x99)
            self.assertEqual(self.memory.memory[0x8000], 0x99)
            self.memory.memory[0x8000] = 0xAB  # restore

    def test_oam_read_returns_ff_during_mode2(self):
        self.ppu._mode = 2
        self.assertEqual(self.memory.get_value(0xFE00), 0xFF)
        self.assertEqual(self.memory.get_value(0xFE9F), 0xFF)

    def test_oam_read_returns_ff_during_mode3(self):
        self.ppu._mode = 3
        self.assertEqual(self.memory.get_value(0xFE00), 0xFF)
        self.assertEqual(self.memory.get_value(0xFE9F), 0xFF)

    def test_oam_read_normal_during_mode0_and_mode1(self):
        for mode in (0, 1):
            self.ppu._mode = mode
            self.assertEqual(self.memory.get_value(0xFE00), 0x11,
                             f"mode {mode}")
            self.assertEqual(self.memory.get_value(0xFE9F), 0x22,
                             f"mode {mode}")

    def test_oam_write_ignored_during_mode2_and_3(self):
        for mode in (2, 3):
            self.ppu._mode = mode
            self.memory.set_value(0xFE00, 0xFF)
            self.assertEqual(self.memory.memory[0xFE00], 0x11,
                             f"mode {mode}")

    def test_oam_write_normal_during_mode0_and_mode1(self):
        for mode in (0, 1):
            self.ppu._mode = mode
            self.memory.set_value(0xFE00, 0x99)
            self.assertEqual(self.memory.memory[0xFE00], 0x99)
            self.memory.memory[0xFE00] = 0x11  # restore

    def test_restrictions_without_ppu_no_effect(self):
        """Memory without PPU loaded has no restrictions."""
        mem = Memory()
        mem.memory[0x8000] = 0xAB
        mem.memory[0xFE00] = 0x11
        # No PPU → reads/writes always work
        self.assertEqual(mem.get_value(0x8000), 0xAB)
        self.assertEqual(mem.get_value(0xFE00), 0x11)
        mem.set_value(0x8000, 0x99)
        self.assertEqual(mem.memory[0x8000], 0x99)


if __name__ == '__main__':
    unittest.main()
