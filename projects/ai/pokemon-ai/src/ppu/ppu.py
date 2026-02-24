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
        # --- STAT interrupt ---
        self._stat_irq_line = False  # Previous state for rising-edge detection
        # --- Framebuffer ---
        self._framebuffer = [[0] * 160 for _ in range(144)]
        self._window_line = 0   # Internal window line counter

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
            self._dma_transfer(value)
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
                    if self._ly < self.VISIBLE_SCANLINES:
                        self._render_scanline()
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
                        self._window_line = 0
                        self._set_mode(2)
                    self._update_lyc_flag()

    # ------------------------------------------------------------------ #
    #  Internal helpers
    # ------------------------------------------------------------------ #

    def _set_mode(self, mode: int) -> None:
        """Update the current mode and STAT bits 0-1."""
        self._mode = mode
        self._stat = (self._stat & 0xFC) | (mode & 0x03)
        self._update_stat_irq()

    def _update_lyc_flag(self) -> None:
        """Set or clear STAT bit 2 based on LY == LYC comparison."""
        if self._ly == self._lyc:
            self._stat |= 0x04
        else:
            self._stat &= ~0x04
        self._update_stat_irq()

    def _update_stat_irq(self) -> None:
        """Evaluate STAT interrupt line and fire on rising edge."""
        stat = self._stat
        new_line = False
        if (stat & 0x08) and self._mode == 0:
            new_line = True
        if (stat & 0x10) and self._mode == 1:
            new_line = True
        if (stat & 0x20) and self._mode == 2:
            new_line = True
        if (stat & 0x40) and (self._ly == self._lyc):
            new_line = True

        if new_line and not self._stat_irq_line:
            self._request_stat_interrupt()

        self._stat_irq_line = new_line

    def _request_vblank_interrupt(self) -> None:
        """Set bit 0 of the IF register to request a V-Blank interrupt."""
        if self._memory is not None:
            if_val = self._memory.memory[0xFF0F]
            self._memory.memory[0xFF0F] = if_val | 0x01

    def _request_stat_interrupt(self) -> None:
        """Set bit 1 of the IF register to request a STAT interrupt."""
        if self._memory is not None:
            if_val = self._memory.memory[0xFF0F]
            self._memory.memory[0xFF0F] = if_val | 0x02

    def _dma_transfer(self, source_page) -> None:
        """Copy 160 bytes from source_page*0x100 into OAM (0xFE00-0xFE9F)."""
        if self._memory is None:
            return
        base = source_page * 0x100
        mem = self._memory.memory
        for i in range(160):
            mem[0xFE00 + i] = mem[base + i]

    # ------------------------------------------------------------------ #
    #  Background + window rendering
    # ------------------------------------------------------------------ #

    @staticmethod
    def _tile_data_address(tile_index, unsigned_mode):
        """Return the VRAM address of a tile given its index and addressing mode."""
        if unsigned_mode:
            return 0x8000 + tile_index * 16
        # Signed addressing: tile_index treated as signed byte
        if tile_index > 127:
            tile_index -= 256
        return 0x9000 + tile_index * 16

    def _render_scanline(self) -> None:
        """Render the current scanline's background, window, and sprites into the framebuffer."""
        if self._memory is None:
            return

        ly = self._ly
        scy = self._scy
        scx = self._scx
        lcdc = self._lcdc
        bgp = self._bgp
        mem = self._memory.memory
        unsigned_mode = bool(lcdc & 0x10)

        # Per-scanline BG color indices (pre-palette) for sprite BG priority
        bg_indices = [0] * 160

        # --- Background ---
        bg_map_base = 0x9C00 if lcdc & 0x08 else 0x9800

        scroll_y = (ly + scy) & 0xFF
        tile_row = scroll_y >> 3
        row_in_tile = scroll_y & 0x07

        row = self._framebuffer[ly]
        for px in range(160):
            scroll_x = (px + scx) & 0xFF
            tile_col = scroll_x >> 3

            tile_index = mem[bg_map_base + tile_row * 32 + tile_col]
            tile_addr = self._tile_data_address(tile_index, unsigned_mode)

            byte_offset = tile_addr + row_in_tile * 2
            low_byte = mem[byte_offset]
            high_byte = mem[byte_offset + 1]

            bit_pos = 7 - (scroll_x & 0x07)
            color_index = (((high_byte >> bit_pos) & 1) << 1) | ((low_byte >> bit_pos) & 1)
            bg_indices[px] = color_index
            row[px] = (bgp >> (color_index * 2)) & 0x03

        # --- Window ---
        if (lcdc & 0x20) and ly >= self._wy:
            win_x_start = self._wx - 7
            win_map_base = 0x9C00 if lcdc & 0x40 else 0x9800
            win_y = self._window_line
            win_tile_row = win_y >> 3
            win_row_in_tile = win_y & 0x07
            window_rendered = False

            start_px = max(0, win_x_start)
            for px in range(start_px, 160):
                win_px = px - win_x_start
                win_tile_col = win_px >> 3

                tile_index = mem[win_map_base + win_tile_row * 32 + win_tile_col]
                tile_addr = self._tile_data_address(tile_index, unsigned_mode)

                byte_offset = tile_addr + win_row_in_tile * 2
                low_byte = mem[byte_offset]
                high_byte = mem[byte_offset + 1]

                bit_pos = 7 - (win_px & 0x07)
                color_index = (((high_byte >> bit_pos) & 1) << 1) | ((low_byte >> bit_pos) & 1)
                bg_indices[px] = color_index
                row[px] = (bgp >> (color_index * 2)) & 0x03
                window_rendered = True

            if window_rendered:
                self._window_line += 1

        # --- Sprites ---
        if lcdc & 0x02:
            self._render_sprites(ly, row, bg_indices, mem)

    # ------------------------------------------------------------------ #
    #  Sprite rendering
    # ------------------------------------------------------------------ #

    def _render_sprites(self, ly, row, bg_indices, mem):
        """Render sprites for the current scanline."""
        lcdc = self._lcdc
        sprite_height = 16 if (lcdc & 0x04) else 8

        # OAM scan: collect up to 10 sprites overlapping this scanline
        sprites = []
        for i in range(40):
            oam_addr = 0xFE00 + i * 4
            raw_y = mem[oam_addr]
            screen_y = raw_y - 16
            if screen_y <= ly < screen_y + sprite_height:
                sprites.append((
                    i,
                    raw_y,
                    mem[oam_addr + 1],
                    mem[oam_addr + 2],
                    mem[oam_addr + 3],
                ))
                if len(sprites) == 10:
                    break

        # Sort by X position (stable sort preserves OAM index for ties)
        sprites.sort(key=lambda s: s[2])

        # Render in reverse priority order (lowest priority first, highest overwrites)
        for oam_idx, raw_y, raw_x, tile_idx, attrs in reversed(sprites):
            screen_x = raw_x - 8
            screen_y = raw_y - 16
            y_flip = bool(attrs & 0x40)
            x_flip = bool(attrs & 0x20)
            palette = self._obp1 if (attrs & 0x10) else self._obp0
            bg_priority = bool(attrs & 0x80)

            # Row within sprite
            row_in_sprite = ly - screen_y
            if y_flip:
                row_in_sprite = (sprite_height - 1) - row_in_sprite

            # Tile address (8x16: bit 0 of index ignored)
            if sprite_height == 16:
                tile_idx &= 0xFE
                if row_in_sprite >= 8:
                    tile_idx |= 0x01
                    row_in_sprite -= 8
            tile_addr = 0x8000 + tile_idx * 16

            low_byte = mem[tile_addr + row_in_sprite * 2]
            high_byte = mem[tile_addr + row_in_sprite * 2 + 1]

            for col in range(8):
                px = screen_x + col
                if px < 0 or px >= 160:
                    continue

                bit = col if x_flip else (7 - col)
                color_index = (((high_byte >> bit) & 1) << 1) | ((low_byte >> bit) & 1)
                if color_index == 0:
                    continue  # transparent

                if bg_priority and bg_indices[px] != 0:
                    continue  # hidden behind non-zero BG

                shade = (palette >> (color_index * 2)) & 0x03
                row[px] = shade

    # ------------------------------------------------------------------ #
    #  Public accessors
    # ------------------------------------------------------------------ #

    def get_framebuffer(self):
        """Return the 160x144 framebuffer (list of lists, shade values 0-3)."""
        return self._framebuffer

    _ASCII_SHADES = [" ", "░", "▒", "█"]

    def render_ascii(self) -> str:
        """Return an ASCII string representation of the framebuffer."""
        lines = []
        for row in self._framebuffer:
            lines.append("".join(self._ASCII_SHADES[shade] for shade in row))
        return "\n".join(lines)
