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
        # Bit 7 always reads as 1, rest is 0 → 0x80
        self.assertEqual(self.ppu.read(0xFF41), 0x80)

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
        # Attempt to write bits 0-2 — they should remain unchanged
        self.ppu.write(0xFF41, 0x07)  # try to set bits 0-2
        self.assertEqual(self.ppu.read(0xFF41) & 0x07, 0x00)

    def test_stat_preserves_readonly_bits(self):
        # Simulate hardware setting mode bits (bits 0-2) internally
        self.ppu._stat = 0x03  # mode 3
        self.ppu.write(0xFF41, 0x40)  # write bit 6
        # Bits 0-2 should be preserved, bit 6 written, bit 7 always 1
        self.assertEqual(self.ppu.read(0xFF41), 0x80 | 0x40 | 0x03)

    def test_stat_write_ignores_bit7(self):
        # Writing bit 7 has no effect (it always reads as 1 anyway)
        self.ppu.write(0xFF41, 0x80)
        # Only bit 7 from read OR, no writable bits set
        self.assertEqual(self.ppu.read(0xFF41), 0x80)


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


if __name__ == '__main__':
    unittest.main()
