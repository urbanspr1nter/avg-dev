import os
import tempfile
import unittest

from src.cartridge.gb_cartridge import Cartridge, BATTERY_TYPES


def _build_rom(cartridge_type=0x13, ram_size_code=0x03):
    """Build a synthetic ROM with the given cartridge type and RAM size."""
    num_banks = 4
    bank_size = 0x4000
    rom = bytearray(num_banks * bank_size)

    rom[0x0100] = 0x00
    rom[0x0101] = 0xC3
    rom[0x0102] = 0x50
    rom[0x0103] = 0x01
    rom[0x0147] = cartridge_type
    rom[0x0148] = 0x01  # 64 KB (4 banks)
    rom[0x0149] = ram_size_code

    checksum = 0
    for addr in range(0x0134, 0x014D):
        checksum = (checksum - rom[addr] - 1) & 0xFF
    rom[0x014D] = checksum

    return bytes(rom)


def _write_temp_rom(rom_data):
    fd, path = tempfile.mkstemp(suffix=".gb")
    os.write(fd, rom_data)
    os.close(fd)
    return path


class TestHasBattery(unittest.TestCase):
    """Test has_battery property for various cartridge types."""

    def _make_cart(self, cartridge_type, ram_size_code=0x03):
        path = _write_temp_rom(_build_rom(cartridge_type, ram_size_code))
        self.addCleanup(os.unlink, path)
        return Cartridge(path)

    def test_mbc3_ram_battery(self):
        cart = self._make_cart(0x13)
        self.assertTrue(cart.has_battery)

    def test_mbc3_timer_ram_battery(self):
        cart = self._make_cart(0x10)
        self.assertTrue(cart.has_battery)

    def test_mbc3_timer_battery(self):
        cart = self._make_cart(0x0F, ram_size_code=0x00)
        self.assertTrue(cart.has_battery)

    def test_mbc1_ram_battery(self):
        cart = self._make_cart(0x03)
        self.assertTrue(cart.has_battery)

    def test_mbc3_no_battery(self):
        cart = self._make_cart(0x12)  # MBC3+RAM (no battery)
        self.assertFalse(cart.has_battery)

    def test_rom_only_no_battery(self):
        cart = self._make_cart(0x00, ram_size_code=0x00)
        self.assertFalse(cart.has_battery)

    def test_mbc1_no_battery(self):
        cart = self._make_cart(0x01, ram_size_code=0x00)
        self.assertFalse(cart.has_battery)


class TestSavPath(unittest.TestCase):
    """Test .sav path derivation from ROM path."""

    def test_sav_path_replaces_extension(self):
        path = _write_temp_rom(_build_rom())
        self.addCleanup(os.unlink, path)
        cart = Cartridge(path)
        expected = path.replace(".gb", ".sav")
        self.assertEqual(cart.sav_path, expected)


class TestSaveBattery(unittest.TestCase):
    """Test saving cartridge RAM to .sav file."""

    def test_save_creates_file(self):
        path = _write_temp_rom(_build_rom(0x13))
        self.addCleanup(os.unlink, path)
        cart = Cartridge(path)
        sav_path = cart.sav_path
        self.addCleanup(lambda: os.unlink(sav_path) if os.path.exists(sav_path) else None)

        # Write some data to RAM
        cart.write(0x0000, 0x0A)  # Enable RAM
        cart.write(0x4000, 0x00)  # Bank 0
        cart.write(0xA000, 0x42)
        cart.write(0xA001, 0xFF)

        result = cart.save_battery()
        self.assertTrue(result)
        self.assertTrue(os.path.exists(sav_path))

    def test_save_file_size_matches_ram(self):
        path = _write_temp_rom(_build_rom(0x13, ram_size_code=0x03))
        self.addCleanup(os.unlink, path)
        cart = Cartridge(path)
        sav_path = cart.sav_path
        self.addCleanup(lambda: os.unlink(sav_path) if os.path.exists(sav_path) else None)

        cart.save_battery()
        self.assertEqual(os.path.getsize(sav_path), 32768)  # 32 KB

    def test_save_contains_written_data(self):
        path = _write_temp_rom(_build_rom(0x13))
        self.addCleanup(os.unlink, path)
        cart = Cartridge(path)
        sav_path = cart.sav_path
        self.addCleanup(lambda: os.unlink(sav_path) if os.path.exists(sav_path) else None)

        cart.write(0x0000, 0x0A)
        cart.write(0x4000, 0x00)
        cart.write(0xA000, 0x42)
        cart.write(0xA001, 0xFF)

        cart.save_battery()

        with open(sav_path, "rb") as f:
            data = f.read()
        self.assertEqual(data[0], 0x42)
        self.assertEqual(data[1], 0xFF)

    def test_save_returns_false_without_battery(self):
        path = _write_temp_rom(_build_rom(0x12))  # MBC3+RAM, no battery
        self.addCleanup(os.unlink, path)
        cart = Cartridge(path)
        self.assertFalse(cart.save_battery())

    def test_save_returns_false_without_ram(self):
        path = _write_temp_rom(_build_rom(0x00, ram_size_code=0x00))
        self.addCleanup(os.unlink, path)
        cart = Cartridge(path)
        self.assertFalse(cart.save_battery())


class TestLoadBattery(unittest.TestCase):
    """Test loading cartridge RAM from .sav file."""

    def test_load_restores_data(self):
        path = _write_temp_rom(_build_rom(0x13))
        self.addCleanup(os.unlink, path)
        sav_path = path.replace(".gb", ".sav")
        self.addCleanup(lambda: os.unlink(sav_path) if os.path.exists(sav_path) else None)

        # Write data and save
        cart1 = Cartridge(path)
        cart1.write(0x0000, 0x0A)
        cart1.write(0x4000, 0x00)
        cart1.write(0xA000, 0x42)
        cart1.write(0xA005, 0xBE)
        cart1.save_battery()

        # Load into fresh cartridge
        cart2 = Cartridge(path)
        result = cart2.load_battery()
        self.assertTrue(result)

        cart2.write(0x0000, 0x0A)
        cart2.write(0x4000, 0x00)
        self.assertEqual(cart2.read(0xA000), 0x42)
        self.assertEqual(cart2.read(0xA005), 0xBE)

    def test_load_returns_false_when_no_file(self):
        path = _write_temp_rom(_build_rom(0x13))
        self.addCleanup(os.unlink, path)
        cart = Cartridge(path)
        self.assertFalse(cart.load_battery())

    def test_load_returns_false_without_battery(self):
        path = _write_temp_rom(_build_rom(0x12))
        self.addCleanup(os.unlink, path)
        cart = Cartridge(path)
        self.assertFalse(cart.load_battery())

    def test_load_preserves_across_banks(self):
        """Data written to multiple RAM banks persists through save/load."""
        path = _write_temp_rom(_build_rom(0x13, ram_size_code=0x03))
        self.addCleanup(os.unlink, path)
        sav_path = path.replace(".gb", ".sav")
        self.addCleanup(lambda: os.unlink(sav_path) if os.path.exists(sav_path) else None)

        cart1 = Cartridge(path)
        cart1.write(0x0000, 0x0A)

        cart1.write(0x4000, 0x00)
        cart1.write(0xA000, 0x11)
        cart1.write(0x4000, 0x01)
        cart1.write(0xA000, 0x22)
        cart1.write(0x4000, 0x02)
        cart1.write(0xA000, 0x33)
        cart1.write(0x4000, 0x03)
        cart1.write(0xA000, 0x44)

        cart1.save_battery()

        cart2 = Cartridge(path)
        cart2.load_battery()
        cart2.write(0x0000, 0x0A)

        cart2.write(0x4000, 0x00)
        self.assertEqual(cart2.read(0xA000), 0x11)
        cart2.write(0x4000, 0x01)
        self.assertEqual(cart2.read(0xA000), 0x22)
        cart2.write(0x4000, 0x02)
        self.assertEqual(cart2.read(0xA000), 0x33)
        cart2.write(0x4000, 0x03)
        self.assertEqual(cart2.read(0xA000), 0x44)

    def test_save_overwrites_existing(self):
        """Saving again overwrites the previous .sav file."""
        path = _write_temp_rom(_build_rom(0x13))
        self.addCleanup(os.unlink, path)
        sav_path = path.replace(".gb", ".sav")
        self.addCleanup(lambda: os.unlink(sav_path) if os.path.exists(sav_path) else None)

        cart = Cartridge(path)
        cart.write(0x0000, 0x0A)
        cart.write(0x4000, 0x00)

        cart.write(0xA000, 0x11)
        cart.save_battery()

        cart.write(0xA000, 0x22)
        cart.save_battery()

        cart2 = Cartridge(path)
        cart2.load_battery()
        cart2.write(0x0000, 0x0A)
        cart2.write(0x4000, 0x00)
        self.assertEqual(cart2.read(0xA000), 0x22)


if __name__ == "__main__":
    unittest.main()
