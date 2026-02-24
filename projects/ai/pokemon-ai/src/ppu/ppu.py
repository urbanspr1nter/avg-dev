class PPU:
    """Game Boy Pixel Processing Unit — register layer.

    Holds the 12 memory-mapped PPU registers (0xFF40-0xFF4B) and handles
    read/write dispatch from the memory bus.  No rendering logic yet — this
    is the data foundation that all future PPU work builds on.
    """

    def __init__(self):
        # --- LCD Control & Status ---
        self._lcdc = 0x91       # 0xFF40  LCD Control (post-boot default)
        self._stat = 0x00       # 0xFF41  LCD Status
        # --- Scroll ---
        self._scy = 0x00        # 0xFF42  Background scroll Y
        self._scx = 0x00        # 0xFF43  Background scroll X
        # --- Scanline ---
        self._ly = 0x00         # 0xFF44  Current scanline (read-only from CPU)
        self._lyc = 0x00        # 0xFF45  LY compare
        # --- DMA ---
        self._dma = 0x00        # 0xFF46  OAM DMA transfer trigger
        # --- Palettes ---
        self._bgp = 0xFC        # 0xFF47  Background palette
        self._obp0 = 0xFF       # 0xFF48  Sprite palette 0
        self._obp1 = 0xFF       # 0xFF49  Sprite palette 1
        # --- Window ---
        self._wy = 0x00         # 0xFF4A  Window Y position
        self._wx = 0x00         # 0xFF4B  Window X position

    # ------------------------------------------------------------------ #
    #  Register read
    # ------------------------------------------------------------------ #

    def read(self, address: int) -> int:
        if address == 0xFF40:
            return self._lcdc
        if address == 0xFF41:
            # Bit 7 always reads as 1
            return self._stat | 0x80
        if address == 0xFF42:
            return self._scy
        if address == 0xFF43:
            return self._scx
        if address == 0xFF44:
            return self._ly
        if address == 0xFF45:
            return self._lyc
        if address == 0xFF46:
            return self._dma
        if address == 0xFF47:
            return self._bgp
        if address == 0xFF48:
            return self._obp0
        if address == 0xFF49:
            return self._obp1
        if address == 0xFF4A:
            return self._wy
        if address == 0xFF4B:
            return self._wx
        return 0xFF

    # ------------------------------------------------------------------ #
    #  Register write
    # ------------------------------------------------------------------ #

    def write(self, address: int, value: int) -> None:
        value = value & 0xFF

        if address == 0xFF40:
            self._lcdc = value
        elif address == 0xFF41:
            # Bits 0-2 are read-only (mode + coincidence flag).
            # Only bits 3-6 are writable.
            writable = value & 0x78       # keep bits 3-6 from the write
            readonly = self._stat & 0x07  # preserve bits 0-2
            self._stat = writable | readonly
        elif address == 0xFF42:
            self._scy = value
        elif address == 0xFF43:
            self._scx = value
        elif address == 0xFF44:
            # LY is read-only; writing resets it to 0
            self._ly = 0
        elif address == 0xFF45:
            self._lyc = value
        elif address == 0xFF46:
            self._dma = value
            # Actual DMA transfer logic will be added later
        elif address == 0xFF47:
            self._bgp = value
        elif address == 0xFF48:
            self._obp0 = value
        elif address == 0xFF49:
            self._obp1 = value
        elif address == 0xFF4A:
            self._wy = value
        elif address == 0xFF4B:
            self._wx = value
