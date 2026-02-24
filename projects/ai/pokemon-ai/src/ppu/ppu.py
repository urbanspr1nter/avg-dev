class PPU:
    """Game Boy Pixel Processing Unit — registers and mode state machine.

    Holds the 12 memory-mapped PPU registers (0xFF40-0xFF4B) and implements
    the scanline mode state machine that cycles through OAM Scan (mode 2),
    Pixel Transfer (mode 3), H-Blank (mode 0), and V-Blank (mode 1).

    Timing per scanline (456 T-cycles):
        Mode 2: dots   0-79   (80 cycles)  — OAM Scan
        Mode 3: dots  80-251  (172 cycles)  — Pixel Transfer
        Mode 0: dots 252-455  (204 cycles)  — H-Blank

    154 scanlines per frame (144 visible + 10 V-Blank = 70,224 T-cycles).
    """

    # Timing constants
    DOTS_PER_SCANLINE = 456
    OAM_SCAN_DOTS = 80
    PIXEL_TRANSFER_END = 252   # OAM_SCAN_DOTS + 172
    VISIBLE_SCANLINES = 144
    TOTAL_SCANLINES = 154

    def __init__(self):
        # --- LCD Control & Status ---
        self._lcdc = 0x91       # 0xFF40  LCD Control (post-boot default)
        self._stat = 0x02       # 0xFF41  LCD Status (mode 2 at startup)
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
        # --- Mode state machine ---
        self._dot = 0           # Dot counter within current scanline (0-455)
        self._mode = 2          # Current PPU mode (starts at OAM Scan)
        self._memory = None     # Set by Memory.load_ppu() for IF register access

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

    # ------------------------------------------------------------------ #
    #  Mode state machine
    # ------------------------------------------------------------------ #

    def tick(self, cycles: int) -> None:
        """Advance the PPU by the given number of T-cycles.

        Called by the CPU run loop after each instruction (and during HALT
        idle).  Each T-cycle advances the dot counter and triggers mode
        transitions at the correct thresholds.
        """
        if not (self._lcdc & 0x80):
            # LCD disabled — PPU does not advance
            return

        for _ in range(cycles):
            self._dot += 1

            if self._ly < self.VISIBLE_SCANLINES:
                # Visible scanline: cycle through modes 2 → 3 → 0
                if self._dot == self.OAM_SCAN_DOTS:
                    self._set_mode(3)
                elif self._dot == self.PIXEL_TRANSFER_END:
                    self._set_mode(0)
                elif self._dot == self.DOTS_PER_SCANLINE:
                    self._dot = 0
                    self._ly += 1
                    if self._ly == self.VISIBLE_SCANLINES:
                        self._set_mode(1)
                        self._request_vblank_interrupt()
                    else:
                        self._set_mode(2)
                    self._update_lyc_flag()
            else:
                # V-Blank scanlines (144-153)
                if self._dot == self.DOTS_PER_SCANLINE:
                    self._dot = 0
                    self._ly += 1
                    if self._ly > self.TOTAL_SCANLINES - 1:
                        self._ly = 0
                        self._set_mode(2)
                    self._update_lyc_flag()

    # ------------------------------------------------------------------ #
    #  Internal helpers
    # ------------------------------------------------------------------ #

    def _set_mode(self, mode: int) -> None:
        """Update the current mode and STAT bits 0-1."""
        self._mode = mode
        self._stat = (self._stat & 0xFC) | (mode & 0x03)

    def _update_lyc_flag(self) -> None:
        """Set or clear STAT bit 2 based on LY == LYC comparison."""
        if self._ly == self._lyc:
            self._stat |= 0x04
        else:
            self._stat &= ~0x04

    def _request_vblank_interrupt(self) -> None:
        """Set bit 0 of the IF register to request a V-Blank interrupt."""
        if self._memory is not None:
            if_val = self._memory.memory[0xFF0F]
            self._memory.memory[0xFF0F] = if_val | 0x01
