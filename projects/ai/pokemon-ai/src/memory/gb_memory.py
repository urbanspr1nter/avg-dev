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

    def set_value(self, address: int, value: int):
        """
        Write an 8-bit value to the given address.
        In a full emulator ROM areas would be read-only; here we allow
        writes for simplicity. Value is masked to 0xFF.
        """
        idx = self._map_address(address)
        self.memory[idx] = value & 0xFF

    def get_value(self, address: int) -> int:
        """
        Read an 8-bit value from the given address.
        """
        idx = self._map_address(address)
        
        # Handle special memory-mapped registers
        if address == 0xFF0F:  # IF - Interrupt Flag register
            # Read current interrupt flag state
            if hasattr(self, '_cpu') and self._cpu and hasattr(self._cpu, 'interrupts'):
                return self._cpu.interrupts.get_if_register()
        elif address == 0xFFFF:  # IE - Interrupt Enable register
            # Read current interrupt enable state
            if hasattr(self, '_cpu') and self._cpu and hasattr(self._cpu, 'interrupts'):
                return self._cpu.interrupts.get_ie_register()
        
        return self.memory[idx]

    def set_value(self, address: int, value: int):
        """
        Write an 8-bit value to the given address.
        In a full emulator ROM areas would be read-only; here we allow
        writes for simplicity. Value is masked to 0xFF.
        """
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
