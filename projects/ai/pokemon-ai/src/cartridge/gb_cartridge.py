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
        self._init_mbc()

    def _init_mbc(self):
        """Initialize MBC state based on cartridge type."""
        self._rom_bank = 1  # Switchable bank defaults to 1
        self._ram_bank = 0
        self._ram_enabled = False
        self._banking_mode = 0  # 0 = ROM mode, 1 = RAM mode
        self._num_rom_banks = max(self.rom_size // 0x4000, 2)

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
        """Read one byte from the cartridge ROM.

        0x0000-0x3FFF: always bank 0 (fixed).
        0x4000-0x7FFF: mapped to the currently selected ROM bank.
        For ROM ONLY cartridges this is always bank 1 (flat access).
        """
        if address < 0 or address > 0x7FFF:
            raise IndexError(
                f"ROM address 0x{address:04X} out of range (must be 0x0000-0x7FFF)"
            )
        if address <= 0x3FFF:
            return self._rom_data[address]

        # 0x4000-0x7FFF: offset into the selected bank
        offset = (self._rom_bank * 0x4000) + (address - 0x4000)
        if offset < len(self._rom_data):
            return self._rom_data[offset]
        return 0xFF  # Out-of-bounds reads return 0xFF

    def write(self, address, value):
        """Handle writes to the ROM address range (MBC register commands).

        On real hardware, these writes are intercepted by the MBC chip on the
        cartridge PCB. The MBC decodes only a few upper address bits to
        determine the register region — see the region table below.

        For ROM ONLY cartridges, writes are silently ignored.
        """
        if self.cartridge_type == 0x00:
            return  # ROM ONLY: no MBC, writes do nothing

        value = value & 0xFF
        if address <= 0x1FFF:
            # RAM enable: 0x0A in lower nibble enables, anything else disables
            self._ram_enabled = (value & 0x0F) == 0x0A
        elif address <= 0x3FFF:
            # ROM bank select (lower 5 bits)
            bank = value & 0x1F
            if bank == 0:
                bank = 1  # Bank 0 cannot be selected — MBC1 treats 0 as 1
            self._rom_bank = bank % self._num_rom_banks
        elif address <= 0x5FFF:
            # RAM bank or upper ROM bank bits (2 bits)
            self._ram_bank = value & 0x03
        elif address <= 0x7FFF:
            # Banking mode select
            self._banking_mode = value & 0x01

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
