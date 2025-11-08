import unittest
from src.memory.gb_memory import Memory

class TestGBMemory(unittest.TestCase):
    def setUp(self):
        self.mem = Memory()

    def test_initial_size_and_zeroed(self):
        # memory should be 65536 bytes all zero
        self.assertEqual(len(self.mem.memory), 0x10000)
        self.assertTrue(all(v == 0 for v in self.mem.memory))

    def test_set_get_value_basic(self):
        addr = 0x1234
        val = 0xAB
        self.mem.set_value(addr, val)
        self.assertEqual(self.mem.get_value(addr), val & 0xFF)

    def test_echo_ram_mapping(self):
        # write to echo area and read from mirrored address
        self.mem.set_value(0xE000, 0x55)
        self.assertEqual(self.mem.get_value(0xC000), 0x55)
        # reading back from E000 should give same value
        self.assertEqual(self.mem.get_value(0xE000), 0x55)

    def test_boundary_addresses(self):
        # Test writing and reading at the extremes of address space
        self.mem.set_value(0x0000, 0x01)
        self.mem.set_value(0xFFFF, 0xFF)
        self.assertEqual(self.mem.get_value(0x0000), 0x01)
        self.assertEqual(self.mem.get_value(0xFFFF), 0xFF)

    def test_multiple_writes_and_reads(self):
        # Write a sequence of values and verify
        for addr in range(0x100, 0x110):
            self.mem.set_value(addr, addr & 0xFF)
        for addr in range(0x100, 0x110):
            self.assertEqual(self.mem.get_value(addr), addr & 0xFF)

    def test_address_out_of_range(self):
        with self.assertRaises(ValueError):
            self.mem.set_value(0x10000, 0x01)
        with self.assertRaises(ValueError):
            self.mem.get_value(-1)

if __name__ == "__main__":
    unittest.main()
