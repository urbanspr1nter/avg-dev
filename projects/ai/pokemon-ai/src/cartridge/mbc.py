import time


class NoMBC:
    """ROM ONLY cartridge (type 0x00). No banking, no RAM."""

    def __init__(self, rom_data):
        self._rom_data = rom_data

    def read(self, address):
        if address <= 0x7FFF:
            if address < len(self._rom_data):
                return self._rom_data[address]
            return 0xFF
        # 0xA000-0xBFFF: no external RAM
        return 0xFF

    def write(self, address, value):
        pass  # ROM ONLY: all writes silently ignored


class MBC1:
    """MBC1 mapper. 5-bit ROM bank, 2-bit RAM bank, banking mode."""

    def __init__(self, rom_data, num_rom_banks, ram_size):
        self._rom_data = rom_data
        self._num_rom_banks = num_rom_banks
        self._ram = bytearray(ram_size) if ram_size > 0 else None
        self._rom_bank = 1
        self._ram_bank = 0
        self._ram_enabled = False
        self._banking_mode = 0

    def read(self, address):
        if address <= 0x3FFF:
            return self._rom_data[address]
        if address <= 0x7FFF:
            offset = (self._rom_bank * 0x4000) + (address - 0x4000)
            if offset < len(self._rom_data):
                return self._rom_data[offset]
            return 0xFF
        # 0xA000-0xBFFF: external RAM
        if self._ram is not None and self._ram_enabled:
            ram_offset = (self._ram_bank * 0x2000) + (address - 0xA000)
            if ram_offset < len(self._ram):
                return self._ram[ram_offset]
        return 0xFF

    def write(self, address, value):
        value = value & 0xFF
        if address <= 0x1FFF:
            self._ram_enabled = (value & 0x0F) == 0x0A
        elif address <= 0x3FFF:
            bank = value & 0x1F
            if bank == 0:
                bank = 1
            self._rom_bank = bank % self._num_rom_banks
        elif address <= 0x5FFF:
            self._ram_bank = value & 0x03
        elif address <= 0x7FFF:
            self._banking_mode = value & 0x01
        elif 0xA000 <= address <= 0xBFFF:
            if self._ram is not None and self._ram_enabled:
                ram_offset = (self._ram_bank * 0x2000) + (address - 0xA000)
                if ram_offset < len(self._ram):
                    self._ram[ram_offset] = value


class MBC3:
    """MBC3 mapper. 7-bit ROM bank, 4 RAM banks, optional RTC."""

    def __init__(self, rom_data, num_rom_banks, ram_size, has_rtc=False):
        self._rom_data = rom_data
        self._num_rom_banks = num_rom_banks
        self._ram = bytearray(ram_size) if ram_size > 0 else None
        self._rom_bank = 1
        self._ram_bank = 0
        self._ram_enabled = False

        # RTC state
        self._has_rtc = has_rtc
        self._rtc_registers = [0] * 5  # S, M, H, DL, DH (latched values)
        self._rtc_latch_state = 0xFF
        self._rtc_halted = False
        self._rtc_base_timestamp = None
        self._rtc_base_seconds = 0

    def start_rtc(self):
        """Initialize RTC timekeeping. Called when cartridge is loaded."""
        if self._has_rtc:
            self._rtc_base_timestamp = time.time()
            self._rtc_base_seconds = 0

    def read(self, address):
        if address <= 0x3FFF:
            return self._rom_data[address]
        if address <= 0x7FFF:
            offset = (self._rom_bank * 0x4000) + (address - 0x4000)
            if offset < len(self._rom_data):
                return self._rom_data[offset]
            return 0xFF
        # 0xA000-0xBFFF: RAM bank or RTC register
        if not self._ram_enabled:
            return 0xFF
        if 0x08 <= self._ram_bank <= 0x0C:
            if self._has_rtc:
                return self._rtc_registers[self._ram_bank - 0x08]
            return 0xFF
        if self._ram is not None and self._ram_bank <= 0x03:
            ram_offset = (self._ram_bank * 0x2000) + (address - 0xA000)
            if ram_offset < len(self._ram):
                return self._ram[ram_offset]
        return 0xFF

    def write(self, address, value):
        value = value & 0xFF
        if address <= 0x1FFF:
            self._ram_enabled = (value & 0x0F) == 0x0A
        elif address <= 0x3FFF:
            bank = value & 0x7F  # 7-bit bank number
            if bank == 0:
                bank = 1
            self._rom_bank = bank % self._num_rom_banks
        elif address <= 0x5FFF:
            self._ram_bank = value  # 0x00-0x03 for RAM, 0x08-0x0C for RTC
        elif address <= 0x7FFF:
            # RTC latch: write 0x00 then 0x01
            if self._has_rtc:
                if self._rtc_latch_state == 0x00 and value == 0x01:
                    self._latch_rtc()
                self._rtc_latch_state = value
        elif 0xA000 <= address <= 0xBFFF:
            if not self._ram_enabled:
                return
            if 0x08 <= self._ram_bank <= 0x0C:
                if self._has_rtc:
                    self._write_rtc_register(self._ram_bank, value)
            elif self._ram is not None and self._ram_bank <= 0x03:
                ram_offset = (self._ram_bank * 0x2000) + (address - 0xA000)
                if ram_offset < len(self._ram):
                    self._ram[ram_offset] = value

    def _latch_rtc(self):
        """Freeze current time into RTC registers."""
        if self._rtc_halted or self._rtc_base_timestamp is None:
            total = self._rtc_base_seconds
        else:
            elapsed = int(time.time() - self._rtc_base_timestamp)
            total = self._rtc_base_seconds + elapsed

        seconds = total % 60
        minutes = (total // 60) % 60
        hours = (total // 3600) % 24
        days = total // 86400

        self._rtc_registers[0] = seconds
        self._rtc_registers[1] = minutes
        self._rtc_registers[2] = hours
        self._rtc_registers[3] = days & 0xFF
        dh = (days >> 8) & 0x01
        if self._rtc_halted:
            dh |= 0x40
        if days > 511:
            dh |= 0x80
        self._rtc_registers[4] = dh

    def _write_rtc_register(self, reg, value):
        """Write to an RTC register, updating internal timekeeping."""
        idx = reg - 0x08
        self._rtc_registers[idx] = value

        # Handle halt bit in DH register
        if idx == 4:
            new_halted = bool(value & 0x40)
            if new_halted and not self._rtc_halted:
                # Halting: accumulate elapsed time
                if self._rtc_base_timestamp is not None:
                    elapsed = int(time.time() - self._rtc_base_timestamp)
                    self._rtc_base_seconds += elapsed
                self._rtc_base_timestamp = None
            elif not new_halted and self._rtc_halted:
                # Resuming: start fresh timestamp
                self._rtc_base_timestamp = time.time()
            self._rtc_halted = new_halted

        # Reconstruct base_seconds from register values
        s = self._rtc_registers[0]
        m = self._rtc_registers[1]
        h = self._rtc_registers[2]
        dl = self._rtc_registers[3]
        dh_val = self._rtc_registers[4]
        days = dl | ((dh_val & 0x01) << 8)
        self._rtc_base_seconds = s + m * 60 + h * 3600 + days * 86400
        if not self._rtc_halted and self._rtc_base_timestamp is None:
            self._rtc_base_timestamp = time.time()
