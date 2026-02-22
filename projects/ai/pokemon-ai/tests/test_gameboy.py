import unittest
import os
import tempfile

from src.gameboy import GameBoy


class TestGameBoyInitialization(unittest.TestCase):
    """Verify that GameBoy wires all components correctly."""

    def test_all_components_exist(self):
        gb = GameBoy()
        self.assertIsNotNone(gb.memory)
        self.assertIsNotNone(gb.cpu)
        self.assertIsNotNone(gb.timer)
        self.assertIsNotNone(gb.serial)
        self.assertIsNone(gb.cartridge)

    def test_cpu_has_memory_reference(self):
        gb = GameBoy()
        self.assertIs(gb.cpu.memory, gb.memory)

    def test_memory_has_cpu_reference(self):
        gb = GameBoy()
        self.assertIs(gb.memory._cpu, gb.cpu)

    def test_cpu_has_timer_reference(self):
        gb = GameBoy()
        self.assertIs(gb.cpu._timer, gb.timer)

    def test_timer_has_memory_reference(self):
        gb = GameBoy()
        self.assertIs(gb.timer._memory, gb.memory)

    def test_memory_has_timer_reference(self):
        gb = GameBoy()
        self.assertIs(gb.memory._timer, gb.timer)

    def test_memory_has_serial_reference(self):
        gb = GameBoy()
        self.assertIs(gb.memory._serial, gb.serial)


class TestGameBoyTimer(unittest.TestCase):
    """Verify timer ticks through the GameBoy run loop."""

    def test_timer_ticks_during_run(self):
        gb = GameBoy()
        # Place a NOP at 0x0000 (4 T-cycles)
        gb.memory.memory[0x0000] = 0x00
        gb.cpu.registers.PC = 0x0000
        gb.run(max_cycles=4)
        self.assertEqual(gb.timer._internal_counter, 4)

    def test_timer_interrupt_fires(self):
        gb = GameBoy()
        # Enable timer at fastest rate (16 T-cycles per TIMA tick)
        gb.timer.write(0xFF07, 0x05)
        gb.timer.write(0xFF05, 0xFF)  # About to overflow
        gb.timer.write(0xFF06, 0x00)  # TMA = 0

        # Enable timer interrupt
        gb.cpu.interrupts.ime = True
        gb.memory.memory[0xFFFF] = 0x04  # IE: timer enabled

        # Fill with NOPs
        for i in range(0x100):
            gb.memory.memory[i] = 0x00

        gb.cpu.registers.PC = 0x0000
        gb.run(max_cycles=40)

        # Timer interrupt should have been serviced
        self.assertEqual(gb.memory.memory[0xFF0F] & 0x04, 0)
        self.assertGreaterEqual(gb.cpu.registers.PC, 0x0050)


class TestGameBoySerial(unittest.TestCase):
    """Verify serial output through the GameBoy memory bus."""

    def test_serial_output_via_memory(self):
        gb = GameBoy()
        gb.memory.set_value(0xFF01, 0x48)  # 'H'
        gb.memory.set_value(0xFF02, 0x81)  # Transfer
        self.assertEqual(gb.get_serial_output(), "H")

    def test_serial_multiple_chars(self):
        gb = GameBoy()
        for char in b"Hello":
            gb.memory.set_value(0xFF01, char)
            gb.memory.set_value(0xFF02, 0x81)
        self.assertEqual(gb.get_serial_output(), "Hello")


class TestGameBoyCartridge(unittest.TestCase):
    """Verify cartridge loading through GameBoy."""

    def _make_rom(self):
        """Create a minimal valid ROM in a temp file."""
        rom = bytearray(0x8000)  # 32KB
        rom[0x0134:0x0143] = b"TEST ROM\x00\x00\x00\x00\x00\x00\x00"
        rom[0x0147] = 0x00  # ROM ONLY
        rom[0x0148] = 0x00  # 32KB
        rom[0x0149] = 0x00  # No RAM
        # Compute header checksum
        checksum = 0
        for addr in range(0x0134, 0x014D):
            checksum = (checksum - rom[addr] - 1) & 0xFF
        rom[0x014D] = checksum
        # Put a known byte at 0x0150
        rom[0x0150] = 0x42
        fd, path = tempfile.mkstemp(suffix=".gb")
        os.write(fd, bytes(rom))
        os.close(fd)
        return path

    def test_load_cartridge(self):
        path = self._make_rom()
        try:
            gb = GameBoy()
            cart = gb.load_cartridge(path)
            self.assertIs(gb.cartridge, cart)
            self.assertEqual(cart.title, "TEST ROM")
            # ROM data is accessible through memory
            self.assertEqual(gb.memory.get_value(0x0150), 0x42)
        finally:
            os.unlink(path)

    def test_rom_writes_ignored_after_cartridge_load(self):
        path = self._make_rom()
        try:
            gb = GameBoy()
            gb.load_cartridge(path)
            original = gb.memory.get_value(0x0150)
            gb.memory.set_value(0x0150, 0xFF)  # Should be ignored
            self.assertEqual(gb.memory.get_value(0x0150), original)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
