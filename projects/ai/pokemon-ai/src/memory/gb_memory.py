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
        self.memory = [0] * 0x10000
        self._cartridge = None
        self._serial = None
        self._timer = None

    def load_cartridge(self, cartridge):
        """Load a cartridge into the memory bus.

        When a cartridge is loaded, reads from 0x0000-0x7FFF are delegated
        to the cartridge ROM data, and writes to that range are ignored
        (ROM is read-only on real hardware).
        """
        self._cartridge = cartridge

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
        # ROM range: delegate to cartridge when one is loaded
        if address <= 0x7FFF and self._cartridge is not None:
            return self._cartridge.read(address)

        # I/O register dispatch
        if 0xFF01 <= address <= 0xFF02 and self._serial is not None:
            return self._serial.read(address)
        if 0xFF04 <= address <= 0xFF07 and self._timer is not None:
            return self._timer.read(address)

        idx = self._map_address(address)

        # Handle special memory-mapped registers
        if address == 0xFF0F:  # IF - Interrupt Flag register
            if hasattr(self, '_cpu') and self._cpu and hasattr(self._cpu, 'interrupts'):
                return self._cpu.interrupts.get_if_register()
        elif address == 0xFFFF:  # IE - Interrupt Enable register
            if hasattr(self, '_cpu') and self._cpu and hasattr(self._cpu, 'interrupts'):
                return self._cpu.interrupts.get_ie_register()

        return self.memory[idx]

    def set_value(self, address: int, value: int):
        """
        Write an 8-bit value to the given address.
        When a cartridge is loaded, writes to the ROM range (0x0000-0x7FFF)
        are ignored — ROM is read-only on real hardware. Without a cartridge
        (e.g. in tests), writes are allowed for simplicity.
        """
        # ROM range: ignore writes when a cartridge is loaded
        if address <= 0x7FFF and self._cartridge is not None:
            return

        # I/O register dispatch
        if 0xFF01 <= address <= 0xFF02 and self._serial is not None:
            self._serial.write(address, value)
            return
        if 0xFF04 <= address <= 0xFF07 and self._timer is not None:
            self._timer.write(address, value)
            return

        idx = self._map_address(address)

        # Handle special memory-mapped registers
        if address == 0xFF0F:  # IF - Interrupt Flag register
            # Write to interrupt flag register
            if hasattr(self, '_cpu') and self._cpu and hasattr(self._cpu, 'interrupts'):
                self._cpu.interrupts.set_if_register(value & 0xFF)
                return
        elif address == 0xFFFF:  # IE - Interrupt Enable register
            # Write to interrupt enable register
            if hasattr(self, '_cpu') and self._cpu and hasattr(self._cpu, 'interrupts'):
                self._cpu.interrupts.set_ie_register(value & 0xFF)
                return
        
        self.memory[idx] = value & 0xFF
