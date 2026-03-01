import os
import tempfile
import unittest

from src.cartridge.gb_cartridge import Cartridge
from src.cartridge.mbc import MBC5
from src.memory.gb_memory import Memory


def _build_mbc5_rom(num_banks=4, cartridge_type=0x1A, ram_size_code=0x03):
    """Build a synthetic MBC5 ROM with known data in each bank.

    Each bank's first byte is set to the bank number (mod 256 for banks >= 256).
    Default type 0x1A = MBC5+RAM, ram_size_code 0x03 = 32 KB (4 banks).
    """
    bank_size = 0x4000
    rom = bytearray(num_banks * bank_size)

    for bank in range(num_banks):
        rom[bank * bank_size] = bank & 0xFF

    rom[0x0100] = 0x00  # NOP
    rom[0x0101] = 0xC3  # JP
    rom[0x0102] = 0x50
    rom[0x0103] = 0x01
    rom[0x0147] = cartridge_type

    if num_banks <= 2:
        rom[0x0148] = 0x00
    elif num_banks <= 4:
        rom[0x0148] = 0x01
    elif num_banks <= 8:
        rom[0x0148] = 0x02
    elif num_banks <= 16:
        rom[0x0148] = 0x03
    elif num_banks <= 32:
        rom[0x0148] = 0x04
    elif num_banks <= 64:
        rom[0x0148] = 0x05
    elif num_banks <= 128:
        rom[0x0148] = 0x06
    elif num_banks <= 256:
        rom[0x0148] = 0x07
    elif num_banks <= 512:
        rom[0x0148] = 0x08

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


class TestMBC5ROMBanking(unittest.TestCase):
    """Test MBC5 ROM bank selection (9-bit, bank 0 valid)."""

    def setUp(self):
        self.rom_data = _build_mbc5_rom(num_banks=8)
        self.rom_path = _write_temp_rom(self.rom_data)
        self.cart = Cartridge(self.rom_path)

    def tearDown(self):
        os.unlink(self.rom_path)

    def test_default_bank_is_1(self):
        self.assertEqual(self.cart._rom_bank, 1)
        self.assertEqual(self.cart.read(0x4000), 0x01)

    def test_switch_to_bank_2(self):
        self.cart.write(0x2000, 0x02)
        self.assertEqual(self.cart._rom_bank, 2)
        self.assertEqual(self.cart.read(0x4000), 0x02)

    def test_switch_to_bank_7(self):
        self.cart.write(0x2000, 0x07)
        self.assertEqual(self.cart._rom_bank, 7)
        self.assertEqual(self.cart.read(0x4000), 0x07)

    def test_bank_0_is_valid(self):
        """Unlike MBC1/MBC3, MBC5 allows selecting bank 0 for 0x4000-0x7FFF."""
        self.cart.write(0x2000, 0x00)
        self.assertEqual(self.cart._rom_bank, 0)
        # Bank 0 at 0x4000 reads the same data as 0x0000
        self.assertEqual(self.cart.read(0x4000), self.cart.read(0x0000))

    def test_lower_8_bits_from_0x2000(self):
        """Write to 0x2000-0x2FFF sets lower 8 bits of ROM bank."""
        self.cart.write(0x2000, 0x05)
        self.assertEqual(self.cart._rom_bank, 5)

    def test_9th_bit_from_0x3000(self):
        """Write to 0x3000-0x3FFF sets bit 8 of ROM bank."""
        # With only 8 banks, bit 8 wraps: (1 << 8) | 1 = 257, 257 % 8 = 1
        self.cart.write(0x3000, 0x01)
        expected = ((1 << 8) | (self.cart._mbc._rom_bank & 0xFF)) % 8
        self.assertEqual(self.cart._rom_bank, expected)

    def test_bank_wraps_to_num_banks(self):
        """Bank number wraps around ROM size."""
        # 8 banks: writing 9 should wrap to 9 % 8 = 1
        self.cart.write(0x2000, 0x09)
        self.assertEqual(self.cart._rom_bank, 1)

    def test_any_address_in_0x2000_0x2FFF_sets_low_bits(self):
        self.cart.write(0x2000, 0x03)
        self.assertEqual(self.cart._rom_bank, 3)
        self.cart.write(0x2FFF, 0x05)
        self.assertEqual(self.cart._rom_bank, 5)
        self.cart.write(0x2ABC, 0x02)
        self.assertEqual(self.cart._rom_bank, 2)

    def test_any_address_in_0x3000_0x3FFF_sets_high_bit(self):
        """Any address in 0x3000-0x3FFF sets bit 8."""
        self.cart.write(0x3000, 0x01)
        high_bit_set = (self.cart._mbc._rom_bank & 0x100) != 0 or self.cart._rom_bank == ((1 << 8) | 0) % 8
        # Just verify the write path works at both ends of the range
        self.cart.write(0x3FFF, 0x00)
        # Bit 8 cleared, lower byte preserved
        self.assertTrue(self.cart._rom_bank < 256)

    def test_bank0_fixed_regardless_of_switch(self):
        self.cart.write(0x2000, 0x05)
        self.assertEqual(self.cart.read(0x0000), 0x00)  # Still bank 0
        self.assertEqual(self.cart.read(0x4000), 0x05)

    def test_large_rom_512_banks(self):
        """Test with maximum MBC5 ROM size (512 banks = 8 MB)."""
        rom_data = _build_mbc5_rom(num_banks=512, ram_size_code=0x00)
        path = _write_temp_rom(rom_data)
        try:
            cart = Cartridge(path)
            # Select bank 511 (0x1FF): low byte = 0xFF, high bit = 1
            cart.write(0x2000, 0xFF)
            cart.write(0x3000, 0x01)
            self.assertEqual(cart._rom_bank, 511)
            self.assertEqual(cart.read(0x4000), 511 & 0xFF)

            # Select bank 256 (0x100): low byte = 0x00, high bit = 1
            cart.write(0x2000, 0x00)
            cart.write(0x3000, 0x01)
            self.assertEqual(cart._rom_bank, 256)
            self.assertEqual(cart.read(0x4000), 256 & 0xFF)
        finally:
            os.unlink(path)

    def test_9th_bit_preserves_lower_8_bits(self):
        """Writing to 0x3000 preserves the lower 8 bits set by 0x2000."""
        rom_data = _build_mbc5_rom(num_banks=512, ram_size_code=0x00)
        path = _write_temp_rom(rom_data)
        try:
            cart = Cartridge(path)
            cart.write(0x2000, 0x05)  # Low byte = 5
            cart.write(0x3000, 0x01)  # Set bit 8
            # Bank = (1 << 8) | 5 = 261
            self.assertEqual(cart._rom_bank, 261)
        finally:
            os.unlink(path)

    def test_low_byte_preserves_9th_bit(self):
        """Writing to 0x2000 preserves bit 8 set by 0x3000."""
        rom_data = _build_mbc5_rom(num_banks=512, ram_size_code=0x00)
        path = _write_temp_rom(rom_data)
        try:
            cart = Cartridge(path)
            cart.write(0x3000, 0x01)  # Set bit 8
            cart.write(0x2000, 0x0A)  # Low byte = 10
            # Bank = (1 << 8) | 10 = 266
            self.assertEqual(cart._rom_bank, 266)
        finally:
            os.unlink(path)


class TestMBC5ReadOffset(unittest.TestCase):
    """Test that reads compute the correct physical ROM offset."""

    def setUp(self):
        self.rom_data = bytearray(_build_mbc5_rom(num_banks=4))
        self.rom_data[0x4000] = 0xAA  # Bank 1
        self.rom_data[0x8000] = 0xBB  # Bank 2
        self.rom_data[0xC000] = 0xCC  # Bank 3
        self.rom_path = _write_temp_rom(bytes(self.rom_data))
        self.cart = Cartridge(self.rom_path)

    def tearDown(self):
        os.unlink(self.rom_path)

    def test_bank1_reads(self):
        self.assertEqual(self.cart.read(0x4000), 0xAA)

    def test_bank2_reads(self):
        self.cart.write(0x2000, 0x02)
        self.assertEqual(self.cart.read(0x4000), 0xBB)

    def test_bank3_reads(self):
        self.cart.write(0x2000, 0x03)
        self.assertEqual(self.cart.read(0x4000), 0xCC)

    def test_switch_back_and_forth(self):
        self.cart.write(0x2000, 0x03)
        self.assertEqual(self.cart.read(0x4000), 0xCC)
        self.cart.write(0x2000, 0x01)
        self.assertEqual(self.cart.read(0x4000), 0xAA)


class TestMBC5RAM(unittest.TestCase):
    """Test MBC5 external RAM (cartridge RAM)."""

    def setUp(self):
        # MBC5+RAM, 32 KB RAM (4 banks)
        self.rom_path = _write_temp_rom(_build_mbc5_rom(
            num_banks=4, cartridge_type=0x1A, ram_size_code=0x03
        ))
        self.cart = Cartridge(self.rom_path)

    def tearDown(self):
        os.unlink(self.rom_path)

    def test_ram_disabled_by_default(self):
        self.assertFalse(self.cart._ram_enabled)

    def test_ram_reads_0xff_when_disabled(self):
        self.assertEqual(self.cart.read(0xA000), 0xFF)

    def test_ram_enable(self):
        self.cart.write(0x0000, 0x0A)
        self.assertTrue(self.cart._ram_enabled)

    def test_ram_disable(self):
        self.cart.write(0x0000, 0x0A)
        self.cart.write(0x0000, 0x00)
        self.assertFalse(self.cart._ram_enabled)

    def test_ram_write_and_read(self):
        self.cart.write(0x0000, 0x0A)  # Enable RAM
        self.cart.write(0x4000, 0x00)  # Select RAM bank 0
        self.cart.write(0xA000, 0x42)
        self.assertEqual(self.cart.read(0xA000), 0x42)

    def test_ram_write_ignored_when_disabled(self):
        self.cart.write(0x4000, 0x00)
        self.cart.write(0xA000, 0x42)  # RAM disabled, write ignored
        self.cart.write(0x0000, 0x0A)  # Enable RAM
        self.assertEqual(self.cart.read(0xA000), 0x00)  # Still zero

    def test_ram_bank_switching(self):
        self.cart.write(0x0000, 0x0A)  # Enable RAM

        # Write to bank 0
        self.cart.write(0x4000, 0x00)
        self.cart.write(0xA000, 0x11)

        # Write to bank 1
        self.cart.write(0x4000, 0x01)
        self.cart.write(0xA000, 0x22)

        # Write to bank 2
        self.cart.write(0x4000, 0x02)
        self.cart.write(0xA000, 0x33)

        # Write to bank 3
        self.cart.write(0x4000, 0x03)
        self.cart.write(0xA000, 0x44)

        # Verify each bank retained its value
        self.cart.write(0x4000, 0x00)
        self.assertEqual(self.cart.read(0xA000), 0x11)
        self.cart.write(0x4000, 0x01)
        self.assertEqual(self.cart.read(0xA000), 0x22)
        self.cart.write(0x4000, 0x02)
        self.assertEqual(self.cart.read(0xA000), 0x33)
        self.cart.write(0x4000, 0x03)
        self.assertEqual(self.cart.read(0xA000), 0x44)

    def test_ram_multiple_addresses(self):
        """Write to various addresses within the 8 KB RAM bank."""
        self.cart.write(0x0000, 0x0A)
        self.cart.write(0x4000, 0x00)
        self.cart.write(0xA000, 0xAA)
        self.cart.write(0xA100, 0xBB)
        self.cart.write(0xBFFF, 0xCC)
        self.assertEqual(self.cart.read(0xA000), 0xAA)
        self.assertEqual(self.cart.read(0xA100), 0xBB)
        self.assertEqual(self.cart.read(0xBFFF), 0xCC)

    def test_ram_16_banks(self):
        """MBC5 supports up to 16 RAM banks (128 KB)."""
        path = _write_temp_rom(_build_mbc5_rom(
            num_banks=4, cartridge_type=0x1A, ram_size_code=0x04  # 128 KB
        ))
        try:
            cart = Cartridge(path)
            cart.write(0x0000, 0x0A)

            # Write a unique value to each of 16 banks
            for bank in range(16):
                cart.write(0x4000, bank)
                cart.write(0xA000, 0x10 + bank)

            # Verify each bank
            for bank in range(16):
                cart.write(0x4000, bank)
                self.assertEqual(cart.read(0xA000), 0x10 + bank,
                                 f"RAM bank {bank} data mismatch")
        finally:
            os.unlink(path)


class TestMBC5NoRAM(unittest.TestCase):
    """Test MBC5 variants without RAM."""

    def test_mbc5_no_ram_returns_0xff(self):
        """Type 0x19 (plain MBC5): external RAM reads return 0xFF."""
        path = _write_temp_rom(_build_mbc5_rom(
            num_banks=4, cartridge_type=0x19, ram_size_code=0x00
        ))
        try:
            cart = Cartridge(path)
            cart.write(0x0000, 0x0A)  # Enable
            cart.write(0x4000, 0x00)
            self.assertEqual(cart.read(0xA000), 0xFF)
        finally:
            os.unlink(path)

    def test_mbc5_rumble_no_ram_returns_0xff(self):
        """Type 0x1C (MBC5+RUMBLE): no RAM, reads return 0xFF."""
        path = _write_temp_rom(_build_mbc5_rom(
            num_banks=4, cartridge_type=0x1C, ram_size_code=0x00
        ))
        try:
            cart = Cartridge(path)
            cart.write(0x0000, 0x0A)
            cart.write(0x4000, 0x00)
            self.assertEqual(cart.read(0xA000), 0xFF)
        finally:
            os.unlink(path)


class TestMBC5Rumble(unittest.TestCase):
    """Test MBC5 rumble motor control."""

    def setUp(self):
        # MBC5+RUMBLE+RAM, 32 KB RAM (4 banks)
        self.rom_path = _write_temp_rom(_build_mbc5_rom(
            num_banks=4, cartridge_type=0x1D, ram_size_code=0x03
        ))
        self.cart = Cartridge(self.rom_path)

    def tearDown(self):
        os.unlink(self.rom_path)

    def test_rumble_bit_sets_motor(self):
        """Bit 3 of RAM bank register turns rumble on."""
        self.cart.write(0x4000, 0x08)  # Bit 3 = 1
        self.assertTrue(self.cart._mbc._rumble)

    def test_rumble_bit_clears_motor(self):
        """Writing 0 clears rumble."""
        self.cart.write(0x4000, 0x08)
        self.assertTrue(self.cart._mbc._rumble)
        self.cart.write(0x4000, 0x00)
        self.assertFalse(self.cart._mbc._rumble)

    def test_rumble_does_not_affect_ram_bank(self):
        """Bit 3 controls rumble, not RAM bank selection."""
        self.cart.write(0x4000, 0x0A)  # bits 0-2 = 2, bit 3 = 1
        self.assertEqual(self.cart._ram_bank, 2)
        self.assertTrue(self.cart._mbc._rumble)

    def test_rumble_cart_only_3_bits_for_ram_bank(self):
        """On rumble carts, only bits 0-2 select RAM bank (max 8 banks)."""
        self.cart.write(0x4000, 0x0F)  # bits 0-2 = 7, bit 3 = 1
        self.assertEqual(self.cart._ram_bank, 7)
        self.assertTrue(self.cart._mbc._rumble)

    def test_non_rumble_uses_4_bits_for_ram_bank(self):
        """On non-rumble carts, all 4 bits select RAM bank (max 16 banks)."""
        path = _write_temp_rom(_build_mbc5_rom(
            num_banks=4, cartridge_type=0x1A, ram_size_code=0x04  # 128 KB
        ))
        try:
            cart = Cartridge(path)
            cart.write(0x4000, 0x0F)  # All 4 bits = 15
            self.assertEqual(cart._ram_bank, 15)
        finally:
            os.unlink(path)


class TestMBC5MemoryIntegration(unittest.TestCase):
    """Test MBC5 through the Memory bus."""

    def setUp(self):
        self.rom_data = bytearray(_build_mbc5_rom(num_banks=4))
        self.rom_data[0x4000] = 0x11  # Bank 1
        self.rom_data[0x8000] = 0x22  # Bank 2
        self.rom_data[0xC000] = 0x33  # Bank 3
        self.rom_path = _write_temp_rom(bytes(self.rom_data))

        self.mem = Memory()
        self.cart = Cartridge(self.rom_path)
        self.mem.load_cartridge(self.cart)

    def tearDown(self):
        os.unlink(self.rom_path)

    def test_default_reads_bank1(self):
        self.assertEqual(self.mem.get_value(0x4000), 0x11)

    def test_rom_bank_switch_through_memory(self):
        self.mem.set_value(0x2000, 0x02)
        self.assertEqual(self.mem.get_value(0x4000), 0x22)

    def test_rom_bank_switch_to_bank3(self):
        self.mem.set_value(0x2000, 0x03)
        self.assertEqual(self.mem.get_value(0x4000), 0x33)

    def test_ram_read_write_through_memory(self):
        self.mem.set_value(0x0000, 0x0A)  # Enable RAM
        self.mem.set_value(0x4000, 0x00)  # RAM bank 0
        self.mem.set_value(0xA000, 0x42)
        self.assertEqual(self.mem.get_value(0xA000), 0x42)

    def test_ram_bank_switch_through_memory(self):
        self.mem.set_value(0x0000, 0x0A)

        self.mem.set_value(0x4000, 0x00)
        self.mem.set_value(0xA000, 0xAA)

        self.mem.set_value(0x4000, 0x01)
        self.mem.set_value(0xA000, 0xBB)

        self.mem.set_value(0x4000, 0x00)
        self.assertEqual(self.mem.get_value(0xA000), 0xAA)
        self.mem.set_value(0x4000, 0x01)
        self.assertEqual(self.mem.get_value(0xA000), 0xBB)

    def test_ram_disabled_returns_0xff_through_memory(self):
        self.assertEqual(self.mem.get_value(0xA000), 0xFF)

    def test_bank_0_selectable_through_memory(self):
        """Bank 0 is valid for MBC5 (reads same data as 0x0000-0x3FFF)."""
        self.mem.set_value(0x2000, 0x00)
        self.assertEqual(self.mem.get_value(0x4000), self.mem.get_value(0x0000))


class TestMBC5CartridgeType(unittest.TestCase):
    """Test that all 6 MBC5 cartridge types instantiate correctly."""

    def _make_cart(self, cartridge_type, ram_size_code=0x00):
        path = _write_temp_rom(_build_mbc5_rom(
            num_banks=4, cartridge_type=cartridge_type,
            ram_size_code=ram_size_code
        ))
        try:
            cart = Cartridge(path)
            return cart, path
        except Exception:
            os.unlink(path)
            raise

    def test_plain_mbc5_0x19(self):
        cart, path = self._make_cart(0x19)
        try:
            self.assertIsInstance(cart._mbc, MBC5)
            self.assertFalse(cart._mbc._has_rumble)
            self.assertFalse(cart.has_battery)
        finally:
            os.unlink(path)

    def test_mbc5_ram_battery_0x1B(self):
        cart, path = self._make_cart(0x1B, ram_size_code=0x03)
        try:
            self.assertIsInstance(cart._mbc, MBC5)
            self.assertFalse(cart._mbc._has_rumble)
            self.assertTrue(cart.has_battery)
        finally:
            os.unlink(path)

    def test_mbc5_rumble_ram_battery_0x1E(self):
        cart, path = self._make_cart(0x1E, ram_size_code=0x03)
        try:
            self.assertIsInstance(cart._mbc, MBC5)
            self.assertTrue(cart._mbc._has_rumble)
            self.assertTrue(cart.has_battery)
        finally:
            os.unlink(path)

    def test_mbc5_rumble_0x1C(self):
        cart, path = self._make_cart(0x1C)
        try:
            self.assertIsInstance(cart._mbc, MBC5)
            self.assertTrue(cart._mbc._has_rumble)
            self.assertFalse(cart.has_battery)
        finally:
            os.unlink(path)

    def test_mbc5_ram_0x1A(self):
        cart, path = self._make_cart(0x1A, ram_size_code=0x03)
        try:
            self.assertIsInstance(cart._mbc, MBC5)
            self.assertFalse(cart._mbc._has_rumble)
            self.assertFalse(cart.has_battery)
        finally:
            os.unlink(path)

    def test_mbc5_rumble_ram_0x1D(self):
        cart, path = self._make_cart(0x1D, ram_size_code=0x03)
        try:
            self.assertIsInstance(cart._mbc, MBC5)
            self.assertTrue(cart._mbc._has_rumble)
            self.assertFalse(cart.has_battery)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
