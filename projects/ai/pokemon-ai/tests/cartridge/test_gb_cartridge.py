import os
import tempfile
import unittest

from src.cartridge.gb_cartridge import Cartridge


def _build_rom(
    title=b"TESTGAME",
    cartridge_type=0x00,
    rom_size_code=0x00,
    ram_size_code=0x00,
    destination=0x01,
    total_size=0x8000,
):
    """Build a minimal synthetic ROM with a valid header.

    Returns a bytearray of `total_size` bytes with the header region
    (0x0100-0x014F) populated. The header checksum at 0x014D is
    computed correctly so validate_header_checksum() passes.
    """
    rom = bytearray(total_size)

    # Entry point: NOP; JP 0x0150
    rom[0x0100] = 0x00  # NOP
    rom[0x0101] = 0xC3  # JP
    rom[0x0102] = 0x50  # low byte of 0x0150
    rom[0x0103] = 0x01  # high byte of 0x0150

    # Title (up to 16 bytes at 0x0134-0x0143)
    for i, b in enumerate(title[:16]):
        rom[0x0134 + i] = b

    rom[0x0147] = cartridge_type
    rom[0x0148] = rom_size_code
    rom[0x0149] = ram_size_code
    rom[0x014A] = destination

    # Compute header checksum over 0x0134-0x014C
    checksum = 0
    for addr in range(0x0134, 0x014D):
        checksum = (checksum - rom[addr] - 1) & 0xFF
    rom[0x014D] = checksum

    return bytes(rom)


def _write_temp_rom(rom_data):
    """Write ROM data to a temporary file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".gb")
    os.write(fd, rom_data)
    os.close(fd)
    return path


class TestCartridgeHeaderParsing(unittest.TestCase):
    """Test that the Cartridge class correctly parses header fields."""

    def setUp(self):
        self.rom_data = _build_rom(
            title=b"POKEMON RED",
            cartridge_type=0x13,
            rom_size_code=0x05,
            ram_size_code=0x03,
            destination=0x01,
        )
        self.rom_path = _write_temp_rom(self.rom_data)

    def tearDown(self):
        os.unlink(self.rom_path)

    def test_title_parsed(self):
        cart = Cartridge(self.rom_path)
        self.assertEqual(cart.title, "POKEMON RED")

    def test_title_null_bytes_stripped(self):
        """Title field is 16 bytes; trailing nulls should be stripped."""
        rom = _build_rom(title=b"SHORT\x00\x00\x00")
        path = _write_temp_rom(rom)
        try:
            cart = Cartridge(path)
            self.assertEqual(cart.title, "SHORT")
        finally:
            os.unlink(path)

    def test_cartridge_type(self):
        cart = Cartridge(self.rom_path)
        self.assertEqual(cart.cartridge_type, 0x13)

    def test_cartridge_type_name(self):
        cart = Cartridge(self.rom_path)
        self.assertEqual(cart.cartridge_type_name, "MBC3+RAM+BATTERY")

    def test_cartridge_type_name_unknown(self):
        rom = _build_rom(cartridge_type=0xFF)
        path = _write_temp_rom(rom)
        try:
            cart = Cartridge(path)
            self.assertEqual(cart.cartridge_type_name, "UNKNOWN (0xFF)")
        finally:
            os.unlink(path)

    def test_rom_size_code_and_derived_size(self):
        cart = Cartridge(self.rom_path)
        self.assertEqual(cart.rom_size_code, 0x05)
        # 32768 << 5 = 1,048,576 (1 MB)
        self.assertEqual(cart.rom_size, 1048576)

    def test_ram_size_code_and_derived_size(self):
        cart = Cartridge(self.rom_path)
        self.assertEqual(cart.ram_size_code, 0x03)
        self.assertEqual(cart.ram_size, 32768)

    def test_ram_size_no_ram(self):
        rom = _build_rom(ram_size_code=0x00)
        path = _write_temp_rom(rom)
        try:
            cart = Cartridge(path)
            self.assertEqual(cart.ram_size, 0)
        finally:
            os.unlink(path)

    def test_destination_code(self):
        cart = Cartridge(self.rom_path)
        self.assertEqual(cart.destination_code, 0x01)

    def test_cgb_flag(self):
        cart = Cartridge(self.rom_path)
        self.assertEqual(cart.cgb_flag, self.rom_data[0x0143])

    def test_entry_point(self):
        cart = Cartridge(self.rom_path)
        self.assertEqual(cart.entry_point, bytes([0x00, 0xC3, 0x50, 0x01]))

    def test_nintendo_logo(self):
        cart = Cartridge(self.rom_path)
        self.assertEqual(len(cart.nintendo_logo), 48)
        self.assertEqual(cart.nintendo_logo, bytes(48))  # all zeros in our synthetic ROM


class TestCartridgeReadAndSize(unittest.TestCase):
    """Test the read() and size() API."""

    def setUp(self):
        self.rom_data = _build_rom()
        # Put some known bytes at specific offsets
        data = bytearray(self.rom_data)
        data[0x0000] = 0xAB
        data[0x0001] = 0xCD
        data[0x7FFF] = 0xEF
        self.rom_data = bytes(data)
        self.rom_path = _write_temp_rom(self.rom_data)

    def tearDown(self):
        os.unlink(self.rom_path)

    def test_read_first_byte(self):
        cart = Cartridge(self.rom_path)
        self.assertEqual(cart.read(0x0000), 0xAB)

    def test_read_second_byte(self):
        cart = Cartridge(self.rom_path)
        self.assertEqual(cart.read(0x0001), 0xCD)

    def test_read_last_byte(self):
        cart = Cartridge(self.rom_path)
        self.assertEqual(cart.read(0x7FFF), 0xEF)

    def test_read_header_byte(self):
        cart = Cartridge(self.rom_path)
        # Entry point first byte is NOP (0x00)
        self.assertEqual(cart.read(0x0100), 0x00)

    def test_read_out_of_range_raises(self):
        cart = Cartridge(self.rom_path)
        with self.assertRaises(IndexError):
            cart.read(cart.size())

    def test_read_negative_address_raises(self):
        cart = Cartridge(self.rom_path)
        with self.assertRaises(IndexError):
            cart.read(-1)

    def test_size(self):
        cart = Cartridge(self.rom_path)
        self.assertEqual(cart.size(), 0x8000)


class TestCartridgeChecksum(unittest.TestCase):
    """Test header checksum validation."""

    def test_valid_checksum(self):
        rom = _build_rom(title=b"CHECKTEST")
        path = _write_temp_rom(rom)
        try:
            cart = Cartridge(path)
            self.assertTrue(cart.validate_header_checksum())
        finally:
            os.unlink(path)

    def test_invalid_checksum(self):
        """Corrupt a header byte after checksum was computed."""
        data = bytearray(_build_rom(title=b"BADCHECK"))
        # Corrupt a byte in the checksum range without recomputing
        data[0x0134] = (data[0x0134] + 1) & 0xFF
        path = _write_temp_rom(bytes(data))
        try:
            cart = Cartridge(path)
            self.assertFalse(cart.validate_header_checksum())
        finally:
            os.unlink(path)


class TestCartridgeErrors(unittest.TestCase):
    """Test error handling for invalid inputs."""

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            Cartridge("/nonexistent/path/to/rom.gb")

    def test_rom_too_small(self):
        """ROM smaller than 0x0150 bytes should raise ValueError."""
        data = bytes(0x014F)  # 1 byte too small
        path = _write_temp_rom(data)
        try:
            with self.assertRaises(ValueError):
                Cartridge(path)
        finally:
            os.unlink(path)

    def test_rom_exactly_minimum_size(self):
        """ROM of exactly 0x0150 bytes should load successfully."""
        data = bytearray(0x0150)
        # Compute valid checksum
        checksum = 0
        for addr in range(0x0134, 0x014D):
            checksum = (checksum - data[addr] - 1) & 0xFF
        data[0x014D] = checksum
        path = _write_temp_rom(bytes(data))
        try:
            cart = Cartridge(path)
            self.assertEqual(cart.size(), 0x0150)
        finally:
            os.unlink(path)


class TestCartridgeTypeLookup(unittest.TestCase):
    """Test cartridge type name resolution for common types."""

    def _make_cart_with_type(self, type_code):
        rom = _build_rom(cartridge_type=type_code)
        path = _write_temp_rom(rom)
        try:
            return Cartridge(path), path
        except Exception:
            os.unlink(path)
            raise

    def test_rom_only(self):
        cart, path = self._make_cart_with_type(0x00)
        try:
            self.assertEqual(cart.cartridge_type_name, "ROM ONLY")
        finally:
            os.unlink(path)

    def test_mbc1(self):
        cart, path = self._make_cart_with_type(0x01)
        try:
            self.assertEqual(cart.cartridge_type_name, "MBC1")
        finally:
            os.unlink(path)

    def test_mbc3_ram_battery(self):
        cart, path = self._make_cart_with_type(0x13)
        try:
            self.assertEqual(cart.cartridge_type_name, "MBC3+RAM+BATTERY")
        finally:
            os.unlink(path)

    def test_mbc5(self):
        cart, path = self._make_cart_with_type(0x19)
        try:
            self.assertEqual(cart.cartridge_type_name, "MBC5")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
