class Memory:
    """
    Minimal GameBoy memory model following the official memory map.
    The full address space is 64 KiB (0x0000-0xFFFF). All addresses
    are treated as unsigned 8‑bit values. For simplicity, the memory
    is represented by a list of 65536 integers initialized to zero.

    Address ranges:
      * 0x0000-0x7FFF : ROM (read-only in this minimal model)
      * 0x8000-0x9FFF : Video RAM (VRAM)
      * 0xA000-0xBFFF : External RAM
      * 0xC000-0xDFFF : Work RAM (WRAM)
      * 0xE000-0xFDFF : Echo RAM - mirror of C000-DDFF
      * 0xFE00-0xFE9F : OAM (Object Attribute Memory)
      * 0xFEA0-0xFEFF : Not usable (ignored in this model)
      * 0xFF00-0xFF7F : I/O Registers
      * 0xFF80-0xFFFE : High RAM (HRAM)
      * 0xFFFF       : Interrupt Enable register
    """

    def __init__(self):
        # 64 KiB of memory, each cell holds an 8-bit value.
        # bytearray gives C-level indexing, faster than Python list.
        self.memory = bytearray(0x10000)
        self._cartridge = None
        self._mbc = None  # Cached MBC for fast ROM reads
        self._rom_data = None  # Cached ROM data for inlined reads
        self._serial = None
        self._timer = None
        self._ppu = None
        self._joypad = None
        self._apu = None

    def load_cartridge(self, cartridge):
        """Load a cartridge into the memory bus.

        When a cartridge is loaded, reads from 0x0000-0x7FFF are delegated
        to the cartridge ROM data, and writes to that range are ignored
        (ROM is read-only on real hardware).
        """
        self._cartridge = cartridge
        self._mbc = cartridge._mbc
        self._rom_data = cartridge._mbc._rom_data

    def load_serial(self, serial):
        """Load a serial port handler into the memory bus.

        Reads/writes to 0xFF01-0xFF02 are delegated to the serial handler.
        """
        self._serial = serial

    def load_timer(self, timer):
        """Load a timer into the memory bus.

        Reads/writes to 0xFF04-0xFF07 are delegated to the timer handler.
        The timer gets a reference to memory so it can set IF bits, and
        the CPU gets a reference to the timer so it can tick it each cycle.

        Expected call order: Memory -> CPU -> load_timer(). The GameBoy
        class enforces this. The hasattr guard below exists only as a safety
        net for unit tests that may wire components in isolation without a CPU.
        """
        self._timer = timer
        self._timer._memory = self
        # Wire CPU's timer reference if CPU has already been created.
        # In normal usage (via GameBoy class), CPU always exists by this point.
        # The guard handles the edge case of unit tests that create Memory + Timer
        # without a CPU.
        if hasattr(self, '_cpu') and self._cpu:
            self._cpu._timer = timer

    def load_joypad(self, joypad):
        """Load a joypad handler into the memory bus.

        Reads/writes to 0xFF00 are delegated to the joypad handler.
        The joypad gets a reference to memory so it can set IF bits
        (joypad interrupt, bit 4).
        """
        self._joypad = joypad
        self._joypad._memory = self

    def load_ppu(self, ppu):
        """Load a PPU into the memory bus.

        Reads/writes to 0xFF40-0xFF4B are delegated to the PPU handler.
        The PPU gets a reference to memory so it can set IF bits (V-Blank
        interrupt), and the CPU gets a reference for tick() calls.
        """
        self._ppu = ppu
        self._ppu._memory = self
        if hasattr(self, '_cpu') and self._cpu:
            self._cpu._ppu = ppu

    def load_apu(self, apu):
        """Load an APU into the memory bus.

        Reads/writes to 0xFF10-0xFF3F are delegated to the APU handler.
        The CPU gets a reference for tick() calls.
        """
        self._apu = apu
        if hasattr(self, '_cpu') and self._cpu:
            self._cpu._apu = apu

    def save_state(self):
        return {'memory': bytes(self.memory)}

    def load_state(self, state):
        self.memory = bytearray(state['memory'])

    def _map_address(self, address: int) -> int:
        """
        Map a logical address to the underlying array index.
        Handles the echo RAM mirror (E000-FDFF -> C000-DDFF).
        Raises ValueError for addresses outside 0x0000-0xFFFF.
        """
        if not 0 <= address <= 0xFFFF:
            raise ValueError(f"Address out of range: {address:#06X}")

        # Echo RAM mirrors C000-DDFF
        if 0xE000 <= address <= 0xFDFF:
            return address - 0x2000  # map to C000‑DDFF

        return address

    def get_value(self, address: int) -> int:
        """
        Read an 8-bit value from the given address.
        """
        if not 0 <= address <= 0xFFFF:
            raise ValueError(f"Address out of range: {address:#06X}")
        # Fast path: ROM range (most frequent — instruction fetches)
        if address <= 0x7FFF:
            rom_data = self._rom_data
            if rom_data is not None:
                if address <= 0x3FFF:
                    return rom_data[address]
                offset = (self._mbc._rom_bank * 0x4000) + (address - 0x4000)
                return rom_data[offset] if offset < len(rom_data) else 0xFF
            return self.memory[address]

        # Fast path: WRAM, HRAM, and most RAM reads
        if address < 0xFE00:
            if 0xA000 <= address <= 0xBFFF and self._cartridge is not None:
                return self._cartridge.read(address)
            # VRAM access restriction (mode 3)
            if 0x8000 <= address <= 0x9FFF and self._ppu is not None \
                    and (self._ppu._lcdc & 0x80) and self._ppu._mode == 3:
                return 0xFF
            # Echo RAM
            if 0xE000 <= address <= 0xFDFF:
                return self.memory[address - 0x2000]
            return self.memory[address]

        # OAM access restriction (modes 2/3)
        if 0xFE00 <= address <= 0xFE9F:
            if self._ppu is not None and (self._ppu._lcdc & 0x80) \
                    and self._ppu._mode in (2, 3):
                return 0xFF
            return self.memory[address]

        # I/O registers (0xFF00-0xFF4B) and special registers
        if address == 0xFF0F:
            # IF register: mask to 5 bits only when CPU is wired up
            if self._cpu:
                return self.memory[0xFF0F] & 0x1F
            return self.memory[0xFF0F]
        if address == 0xFFFF:
            return self.memory[0xFFFF]
        if address == 0xFF00 and self._joypad is not None:
            return self._joypad.read(address)
        if 0xFF01 <= address <= 0xFF02 and self._serial is not None:
            return self._serial.read(address)
        if 0xFF04 <= address <= 0xFF07 and self._timer is not None:
            return self._timer.read(address)
        if 0xFF10 <= address <= 0xFF3F and self._apu is not None:
            return self._apu.read(address)
        if 0xFF40 <= address <= 0xFF4B and self._ppu is not None:
            return self._ppu.read(address)

        return self.memory[address]

    def set_value(self, address: int, value: int):
        """
        Write an 8-bit value to the given address.
        """
        if not 0 <= address <= 0xFFFF:
            raise ValueError(f"Address out of range: {address:#06X}")
        value = value & 0xFF

        # ROM range: forward to cartridge for MBC register handling
        if address <= 0x7FFF:
            if self._cartridge is not None:
                self._cartridge.write(address, value)
            else:
                self.memory[address] = value
            return

        # Fast path: WRAM, VRAM, external RAM
        if address < 0xFE00:
            if 0xA000 <= address <= 0xBFFF and self._cartridge is not None:
                self._cartridge.write(address, value)
                return
            # VRAM access restriction (mode 3)
            if 0x8000 <= address <= 0x9FFF and self._ppu is not None \
                    and (self._ppu._lcdc & 0x80) and self._ppu._mode == 3:
                return
            # Echo RAM
            if 0xE000 <= address <= 0xFDFF:
                self.memory[address - 0x2000] = value
                return
            self.memory[address] = value
            return

        # OAM access restriction (modes 2/3)
        if 0xFE00 <= address <= 0xFE9F:
            if self._ppu is not None and (self._ppu._lcdc & 0x80) \
                    and self._ppu._mode in (2, 3):
                return
            self.memory[address] = value
            return

        # I/O registers and special registers
        if address == 0xFF0F:
            self.memory[0xFF0F] = value & 0x1F
            return
        if address == 0xFFFF:
            self.memory[0xFFFF] = value
            return
        if address == 0xFF00 and self._joypad is not None:
            self._joypad.write(address, value)
            return
        if 0xFF01 <= address <= 0xFF02 and self._serial is not None:
            self._serial.write(address, value)
            return
        if 0xFF04 <= address <= 0xFF07 and self._timer is not None:
            self._timer.write(address, value)
            return
        if 0xFF10 <= address <= 0xFF3F and self._apu is not None:
            self._apu.write(address, value)
            return
        if 0xFF40 <= address <= 0xFF4B and self._ppu is not None:
            self._ppu.write(address, value)
            return

        self.memory[address] = value
