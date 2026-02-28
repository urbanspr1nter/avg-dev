import os

from src.cartridge.mbc import NoMBC, MBC1, MBC3

# Cartridge types that have a battery (RAM contents persist across power cycles)
BATTERY_TYPES = {0x03, 0x06, 0x09, 0x0F, 0x10, 0x13, 0x1B, 0x1E}


class Cartridge:
    """Game Boy cartridge ROM loader and header parser.

    Loads a .gb ROM file, parses the cartridge header (0x0100-0x014F),
    and stores the raw ROM data for byte-level access. Banking logic
    is delegated to an MBC strategy object (NoMBC, MBC1, MBC3, etc.).
    """

    # Cartridge type code -> human-readable name
    CARTRIDGE_TYPES = {
        0x00: "ROM ONLY",
        0x01: "MBC1",
        0x02: "MBC1+RAM",
        0x03: "MBC1+RAM+BATTERY",
        0x05: "MBC2",
        0x06: "MBC2+BATTERY",
        0x08: "ROM+RAM",
        0x09: "ROM+RAM+BATTERY",
        0x0F: "MBC3+TIMER+BATTERY",
        0x10: "MBC3+TIMER+RAM+BATTERY",
        0x11: "MBC3",
        0x12: "MBC3+RAM",
        0x13: "MBC3+RAM+BATTERY",
        0x19: "MBC5",
        0x1A: "MBC5+RAM",
        0x1B: "MBC5+RAM+BATTERY",
        0x1C: "MBC5+RUMBLE",
        0x1D: "MBC5+RUMBLE+RAM",
        0x1E: "MBC5+RUMBLE+RAM+BATTERY",
    }

    # RAM size code -> actual size in bytes
    RAM_SIZES = {
        0x00: 0,
        0x01: 0,
        0x02: 8192,       # 8 KB  (1 bank)
        0x03: 32768,      # 32 KB (4 banks)
        0x04: 131072,     # 128 KB (16 banks)
        0x05: 65536,      # 64 KB (8 banks)
    }

    def __init__(self, rom_path: str):
        self._rom_path = rom_path
        with open(rom_path, "rb") as f:
            self._rom_data = f.read()

        if len(self._rom_data) < 0x0150:
            raise ValueError(
                f"ROM too small ({len(self._rom_data)} bytes). "
                f"Minimum 336 bytes required for a valid header."
            )

        self._parse_header()
        self._init_mbc()

    def _init_mbc(self):
        """Initialize MBC strategy based on cartridge type."""
        num_rom_banks = max(self.rom_size // 0x4000, 2)

        if self.cartridge_type == 0x00:
            self._mbc = NoMBC(self._rom_data)
        elif self.cartridge_type in (0x01, 0x02, 0x03):
            self._mbc = MBC1(self._rom_data, num_rom_banks, self.ram_size)
        elif self.cartridge_type in (0x0F, 0x10, 0x11, 0x12, 0x13):
            has_rtc = self.cartridge_type in (0x0F, 0x10)
            self._mbc = MBC3(self._rom_data, num_rom_banks, self.ram_size,
                             has_rtc=has_rtc)
            self._mbc.start_rtc()
        else:
            self._mbc = NoMBC(self._rom_data)

    # Backward-compat properties so existing tests can read
    # self.cart._rom_bank, etc. without changes.
    @property
    def _rom_bank(self):
        return getattr(self._mbc, '_rom_bank', 1)

    @property
    def _ram_bank(self):
        return getattr(self._mbc, '_ram_bank', 0)

    @property
    def _ram_enabled(self):
        return getattr(self._mbc, '_ram_enabled', False)

    @property
    def _banking_mode(self):
        return getattr(self._mbc, '_banking_mode', 0)

    @property
    def _num_rom_banks(self):
        return getattr(self._mbc, '_num_rom_banks', 2)

    def _parse_header(self):
        """Parse the cartridge header at 0x0100-0x014F."""
        d = self._rom_data

        # entry_point and nintendo_logo are kept as raw bytes because they
        # don't have a more meaningful scalar representation. entry_point is
        # 4 bytes of machine code (typically NOP; JP 0x0150) — parsing it into
        # a structure would be over-engineering since nothing consumes it.
        # nintendo_logo is 48 bytes of bitmap data whose only use is byte-for-byte
        # validation against the expected pattern by the boot ROM.
        self.entry_point = bytes(d[0x0100:0x0104])
        self.nintendo_logo = bytes(d[0x0104:0x0134])

        # Remaining header fields are parsed into their useful forms: strings,
        # integers, or derived human-readable values.
        self.title = bytes(d[0x0134:0x0144]).decode("ascii", errors="replace").rstrip("\x00")
        self.cgb_flag = d[0x0143]
        self.cartridge_type = d[0x0147]
        self.rom_size_code = d[0x0148]
        self.ram_size_code = d[0x0149]
        self.destination_code = d[0x014A]
        self.header_checksum = d[0x014D]

        # Derived fields
        self.rom_size = 32768 << self.rom_size_code
        self.ram_size = self.RAM_SIZES.get(self.ram_size_code, 0)
        self.cartridge_type_name = self.CARTRIDGE_TYPES.get(
            self.cartridge_type, f"UNKNOWN (0x{self.cartridge_type:02X})"
        )

    def read(self, address: int) -> int:
        """Read one byte from the cartridge (ROM or external RAM).

        0x0000-0x3FFF: always bank 0 (fixed ROM).
        0x4000-0x7FFF: mapped to the currently selected ROM bank.
        0xA000-0xBFFF: external RAM (if present and enabled).
        """
        if not (0x0000 <= address <= 0x7FFF or 0xA000 <= address <= 0xBFFF):
            raise IndexError(
                f"Cartridge address 0x{address:04X} out of range"
            )
        return self._mbc.read(address)

    def write(self, address, value):
        """Handle writes to the cartridge address space.

        0x0000-0x7FFF: MBC register commands (bank switching, RAM enable).
        0xA000-0xBFFF: external RAM writes (if present and enabled).
        """
        self._mbc.write(address, value)

    def size(self) -> int:
        """Return the total ROM data length in bytes."""
        return len(self._rom_data)

    def print_header(self):
        """Print a formatted summary of the cartridge header."""
        destination = "Japanese" if self.destination_code == 0x00 else "Non-Japanese"
        checksum_status = "valid" if self.validate_header_checksum() else "INVALID"
        lines = [
            f"Title:          {self.title}",
            f"Cartridge type: 0x{self.cartridge_type:02X} ({self.cartridge_type_name})",
            f"ROM size:       0x{self.rom_size_code:02X} ({self.rom_size // 1024} KB)",
            f"RAM size:       0x{self.ram_size_code:02X} ({self.ram_size // 1024} KB)" if self.ram_size > 0
            else f"RAM size:       0x{self.ram_size_code:02X} (None)",
            f"CGB flag:       0x{self.cgb_flag:02X}",
            f"Destination:    0x{self.destination_code:02X} ({destination})",
            f"Entry point:    {self.entry_point.hex(' ')}",
            f"File size:      {self.size()} bytes ({self.size() // 1024} KB)",
            f"Checksum:       0x{self.header_checksum:02X} ({checksum_status})",
        ]
        print("\n".join(lines))

    @property
    def has_battery(self):
        """True if this cartridge type has battery-backed RAM."""
        return self.cartridge_type in BATTERY_TYPES

    @property
    def sav_path(self):
        """Path to the .sav file (derived from ROM path)."""
        base, _ = os.path.splitext(self._rom_path)
        return base + ".sav"

    def load_battery(self):
        """Load cartridge RAM from .sav file if it exists."""
        ram = getattr(self._mbc, '_ram', None)
        if not self.has_battery or ram is None:
            return False
        if not os.path.exists(self.sav_path):
            return False
        with open(self.sav_path, "rb") as f:
            data = f.read()
        # Copy into existing RAM bytearray (truncate or pad to fit)
        size = min(len(data), len(ram))
        ram[:size] = data[:size]
        return True

    def save_battery(self):
        """Save cartridge RAM to .sav file."""
        ram = getattr(self._mbc, '_ram', None)
        if not self.has_battery or ram is None:
            return False
        with open(self.sav_path, "wb") as f:
            f.write(ram)
        return True

    def validate_header_checksum(self) -> bool:
        """Verify the header checksum at 0x014D.

        The checksum is computed over bytes 0x0134-0x014C:
            x = 0
            for addr in 0x0134..0x014C:
                x = x - rom[addr] - 1
            checksum = x & 0xFF
        """
        checksum = 0
        for addr in range(0x0134, 0x014D):
            checksum = (checksum - self._rom_data[addr] - 1) & 0xFF
        return checksum == self.header_checksum
