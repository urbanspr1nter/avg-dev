class Cartridge:
    """Game Boy cartridge ROM loader and header parser.

    Loads a .gb ROM file, parses the cartridge header (0x0100-0x014F),
    and stores the raw ROM data for byte-level access.
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
        with open(rom_path, "rb") as f:
            self._rom_data = f.read()

        if len(self._rom_data) < 0x0150:
            raise ValueError(
                f"ROM too small ({len(self._rom_data)} bytes). "
                f"Minimum 336 bytes required for a valid header."
            )

        self._parse_header()

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
        """Read one byte from the ROM data at the given offset."""
        if address < 0 or address >= len(self._rom_data):
            raise IndexError(
                f"ROM address 0x{address:04X} out of range "
                f"(ROM size: 0x{len(self._rom_data):04X})"
            )
        return self._rom_data[address]

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
