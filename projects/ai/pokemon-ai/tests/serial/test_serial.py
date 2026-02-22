import unittest

from src.serial.serial import Serial


class TestSerialRegisters(unittest.TestCase):
    """Test basic SB/SC register read/write."""

    def setUp(self):
        self.serial = Serial()

    def test_sb_default_zero(self):
        self.assertEqual(self.serial.read(0xFF01), 0x00)

    def test_sc_default_zero(self):
        self.assertEqual(self.serial.read(0xFF02), 0x00)

    def test_write_read_sb(self):
        self.serial.write(0xFF01, 0x42)
        self.assertEqual(self.serial.read(0xFF01), 0x42)

    def test_write_read_sc(self):
        self.serial.write(0xFF02, 0x03)
        self.assertEqual(self.serial.read(0xFF02), 0x03)

    def test_sb_masked_to_8_bits(self):
        self.serial.write(0xFF01, 0x1FF)
        self.assertEqual(self.serial.read(0xFF01), 0xFF)


class TestSerialTransfer(unittest.TestCase):
    """Test serial transfer capture (Blargg protocol)."""

    def setUp(self):
        self.serial = Serial()

    def test_transfer_captures_sb_byte(self):
        """Writing 0x81 to SC captures the current SB value."""
        self.serial.write(0xFF01, 0x48)  # 'H'
        self.serial.write(0xFF02, 0x81)  # Start transfer, internal clock
        self.assertEqual(self.serial.get_output_bytes(), [0x48])

    def test_transfer_clears_sc_bit7(self):
        """After transfer, SC bit 7 is cleared (transfer complete)."""
        self.serial.write(0xFF01, 0x41)
        self.serial.write(0xFF02, 0x81)
        self.assertEqual(self.serial.read(0xFF02), 0x01)  # bit 7 cleared

    def test_multiple_transfers(self):
        """Multiple transfers accumulate in the output buffer."""
        for char in b"OK":
            self.serial.write(0xFF01, char)
            self.serial.write(0xFF02, 0x81)
        self.assertEqual(self.serial.get_output(), "OK")

    def test_no_transfer_without_internal_clock(self):
        """SC=0x80 (no internal clock bit) should NOT trigger transfer."""
        self.serial.write(0xFF01, 0x41)
        self.serial.write(0xFF02, 0x80)  # Start but external clock
        self.assertEqual(self.serial.get_output_bytes(), [])

    def test_no_transfer_without_start_bit(self):
        """SC=0x01 (no start bit) should NOT trigger transfer."""
        self.serial.write(0xFF01, 0x41)
        self.serial.write(0xFF02, 0x01)  # Internal clock but no start
        self.assertEqual(self.serial.get_output_bytes(), [])

    def test_get_output_ascii(self):
        """get_output() returns proper ASCII string."""
        for char in b"Passed\n":
            self.serial.write(0xFF01, char)
            self.serial.write(0xFF02, 0x81)
        self.assertEqual(self.serial.get_output(), "Passed\n")

    def test_output_initially_empty(self):
        self.assertEqual(self.serial.get_output(), "")
        self.assertEqual(self.serial.get_output_bytes(), [])


class TestSerialMemoryIntegration(unittest.TestCase):
    """Test serial through the Memory dispatch."""

    def test_memory_dispatches_serial_reads(self):
        from src.memory.gb_memory import Memory
        mem = Memory()
        serial = Serial()
        mem.load_serial(serial)

        serial.write(0xFF01, 0x55)
        self.assertEqual(mem.get_value(0xFF01), 0x55)

    def test_memory_dispatches_serial_writes(self):
        from src.memory.gb_memory import Memory
        mem = Memory()
        serial = Serial()
        mem.load_serial(serial)

        mem.set_value(0xFF01, 0x48)
        mem.set_value(0xFF02, 0x81)
        self.assertEqual(serial.get_output(), "H")


if __name__ == "__main__":
    unittest.main()
