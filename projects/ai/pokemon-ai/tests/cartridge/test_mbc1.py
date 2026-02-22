import os
import tempfile
import unittest

from src.cartridge.gb_cartridge import Cartridge
from src.memory.gb_memory import Memory


def _build_mbc1_rom(num_banks=4):
    """Build a synthetic MBC1 ROM with known data in each bank.

    Each bank's first byte is set to the bank number (0x00, 0x01, 0x02, ...),
    making it easy to verify which bank is mapped.
    """
    bank_size = 0x4000  # 16KB per bank
    rom = bytearray(num_banks * bank_size)

    # Mark first byte of each bank with its bank number
    for bank in range(num_banks):
        rom[bank * bank_size] = bank

    # Fill in a valid cartridge header in bank 0
    rom[0x0100] = 0x00  # NOP
    rom[0x0101] = 0xC3  # JP
    rom[0x0102] = 0x50
    rom[0x0103] = 0x01
    rom[0x0147] = 0x01  # MBC1

    # rom_size_code: 0x00=32KB(2 banks), 0x01=64KB(4 banks), 0x02=128KB(8 banks)
    if num_banks <= 2:
        rom[0x0148] = 0x00
    elif num_banks <= 4:
        rom[0x0148] = 0x01
    elif num_banks <= 8:
        rom[0x0148] = 0x02
    elif num_banks <= 16:
        rom[0x0148] = 0x03
    else:
        rom[0x0148] = 0x04

    rom[0x0149] = 0x00  # No RAM

    # Compute header checksum
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


class TestMBC1BankSwitching(unittest.TestCase):
    """Test MBC1 ROM bank selection."""

    def setUp(self):
        self.rom_data = _build_mbc1_rom(num_banks=4)
        self.rom_path = _write_temp_rom(self.rom_data)
        self.cart = Cartridge(self.rom_path)

    def tearDown(self):
        os.unlink(self.rom_path)

    def test_bank0_always_at_0x0000(self):
        """Bank 0 is always accessible at 0x0000-0x3FFF."""
        self.assertEqual(self.cart.read(0x0000), 0x00)  # Bank 0 marker

    def test_default_bank_is_1(self):
        """0x4000-0x7FFF defaults to bank 1."""
        self.assertEqual(self.cart._rom_bank, 1)
        self.assertEqual(self.cart.read(0x4000), 0x01)  # Bank 1 marker

    def test_switch_to_bank_2(self):
        self.cart.write(0x2000, 0x02)
        self.assertEqual(self.cart._rom_bank, 2)
        self.assertEqual(self.cart.read(0x4000), 0x02)

    def test_switch_to_bank_3(self):
        self.cart.write(0x2000, 0x03)
        self.assertEqual(self.cart._rom_bank, 3)
        self.assertEqual(self.cart.read(0x4000), 0x03)

    def test_bank_0_maps_to_bank_1(self):
        """Writing 0 to bank register selects bank 1 (MBC1 quirk)."""
        self.cart.write(0x2000, 0x00)
        self.assertEqual(self.cart._rom_bank, 1)
        self.assertEqual(self.cart.read(0x4000), 0x01)

    def test_bank_wraps_to_num_banks(self):
        """Bank number wraps around ROM size."""
        # 4 banks: writing 5 should wrap to 5 % 4 = 1
        self.cart.write(0x2000, 0x05)
        self.assertEqual(self.cart._rom_bank, 1)

    def test_bank_select_uses_lower_5_bits(self):
        """Only lower 5 bits of the write are used for bank select."""
        # 0xE2 = 0b11100010, lower 5 bits = 0b00010 = 2
        self.cart.write(0x2000, 0xE2)
        self.assertEqual(self.cart._rom_bank, 2)

    def test_any_address_in_range_selects_bank(self):
        """Any write to 0x2000-0x3FFF selects the bank (MBC decodes upper bits only)."""
        self.cart.write(0x2000, 0x02)
        self.assertEqual(self.cart._rom_bank, 2)
        self.cart.write(0x3FFF, 0x03)
        self.assertEqual(self.cart._rom_bank, 3)
        self.cart.write(0x2ABC, 0x01)
        self.assertEqual(self.cart._rom_bank, 1)

    def test_bank0_fixed_regardless_of_switch(self):
        """Switching banks only affects 0x4000-0x7FFF, not 0x0000-0x3FFF."""
        self.cart.write(0x2000, 0x03)
        self.assertEqual(self.cart.read(0x0000), 0x00)  # Still bank 0
        self.assertEqual(self.cart.read(0x4000), 0x03)   # Now bank 3


class TestMBC1ReadOffset(unittest.TestCase):
    """Test that reads compute the correct physical ROM offset."""

    def setUp(self):
        # 4 banks, put unique data at 0x4000 offset in each bank
        self.rom_data = bytearray(_build_mbc1_rom(num_banks=4))
        # Bank 1 at physical offset 0x4000
        self.rom_data[0x4000] = 0xAA
        self.rom_data[0x4001] = 0xBB
        # Bank 2 at physical offset 0x8000
        self.rom_data[0x8000] = 0xCC
        self.rom_data[0x8001] = 0xDD
        # Bank 3 at physical offset 0xC000
        self.rom_data[0xC000] = 0xEE
        self.rom_data[0xC001] = 0xFF
        self.rom_path = _write_temp_rom(bytes(self.rom_data))
        self.cart = Cartridge(self.rom_path)

    def tearDown(self):
        os.unlink(self.rom_path)

    def test_bank1_reads(self):
        self.assertEqual(self.cart.read(0x4000), 0xAA)
        self.assertEqual(self.cart.read(0x4001), 0xBB)

    def test_bank2_reads(self):
        self.cart.write(0x2000, 0x02)
        self.assertEqual(self.cart.read(0x4000), 0xCC)
        self.assertEqual(self.cart.read(0x4001), 0xDD)

    def test_bank3_reads(self):
        self.cart.write(0x2000, 0x03)
        self.assertEqual(self.cart.read(0x4000), 0xEE)
        self.assertEqual(self.cart.read(0x4001), 0xFF)

    def test_switch_back_and_forth(self):
        self.cart.write(0x2000, 0x03)
        self.assertEqual(self.cart.read(0x4000), 0xEE)
        self.cart.write(0x2000, 0x01)
        self.assertEqual(self.cart.read(0x4000), 0xAA)
        self.cart.write(0x2000, 0x02)
        self.assertEqual(self.cart.read(0x4000), 0xCC)


class TestMBC1OtherRegisters(unittest.TestCase):
    """Test RAM enable, RAM bank, and banking mode registers."""

    def setUp(self):
        self.rom_path = _write_temp_rom(_build_mbc1_rom(num_banks=4))
        self.cart = Cartridge(self.rom_path)

    def tearDown(self):
        os.unlink(self.rom_path)

    def test_ram_disabled_by_default(self):
        self.assertFalse(self.cart._ram_enabled)

    def test_ram_enable(self):
        self.cart.write(0x0000, 0x0A)
        self.assertTrue(self.cart._ram_enabled)

    def test_ram_disable(self):
        self.cart.write(0x0000, 0x0A)  # Enable
        self.cart.write(0x0000, 0x00)  # Disable
        self.assertFalse(self.cart._ram_enabled)

    def test_ram_enable_checks_lower_nibble(self):
        """Only lower nibble 0x0A enables RAM."""
        self.cart.write(0x0000, 0xFA)  # Lower nibble is 0xA
        self.assertTrue(self.cart._ram_enabled)
        self.cart.write(0x0000, 0x0B)  # Lower nibble is 0xB
        self.assertFalse(self.cart._ram_enabled)

    def test_ram_bank_select(self):
        self.cart.write(0x4000, 0x02)
        self.assertEqual(self.cart._ram_bank, 2)

    def test_ram_bank_select_masks_to_2_bits(self):
        self.cart.write(0x4000, 0xFF)
        self.assertEqual(self.cart._ram_bank, 3)

    def test_banking_mode_default(self):
        self.assertEqual(self.cart._banking_mode, 0)

    def test_banking_mode_select(self):
        self.cart.write(0x6000, 0x01)
        self.assertEqual(self.cart._banking_mode, 1)

    def test_banking_mode_masks_to_1_bit(self):
        self.cart.write(0x6000, 0xFF)
        self.assertEqual(self.cart._banking_mode, 1)


class TestMBC1ROMOnly(unittest.TestCase):
    """Test that ROM ONLY cartridges ignore writes."""

    def setUp(self):
        rom = bytearray(0x8000)
        rom[0x0147] = 0x00  # ROM ONLY
        checksum = 0
        for addr in range(0x0134, 0x014D):
            checksum = (checksum - rom[addr] - 1) & 0xFF
        rom[0x014D] = checksum
        self.rom_path = _write_temp_rom(bytes(rom))
        self.cart = Cartridge(self.rom_path)

    def tearDown(self):
        os.unlink(self.rom_path)

    def test_writes_ignored(self):
        self.cart.write(0x2000, 0x02)
        self.assertEqual(self.cart._rom_bank, 1)  # Unchanged


class TestMBC1MemoryIntegration(unittest.TestCase):
    """Test MBC1 bank switching through the Memory bus."""

    def setUp(self):
        self.rom_data = bytearray(_build_mbc1_rom(num_banks=4))
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

    def test_bank_switch_through_memory_write(self):
        """Writing to 0x2000-0x3FFF through Memory should switch banks."""
        self.mem.set_value(0x2000, 0x02)
        self.assertEqual(self.mem.get_value(0x4000), 0x22)

    def test_bank_switch_to_bank3(self):
        self.mem.set_value(0x2000, 0x03)
        self.assertEqual(self.mem.get_value(0x4000), 0x33)

    def test_bank0_unaffected_by_switch(self):
        self.mem.set_value(0x2000, 0x03)
        self.assertEqual(self.mem.get_value(0x0000), self.rom_data[0x0000])


if __name__ == "__main__":
    unittest.main()
