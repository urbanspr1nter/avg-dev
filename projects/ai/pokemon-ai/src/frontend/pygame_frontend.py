import time

import pygame

# Game Boy LCD resolution
GB_WIDTH = 160
GB_HEIGHT = 144

# Classic DMG green palette: shade value (0-3) → RGB tuple
DMG_PALETTE = (
    (155, 188, 15),   # 0: lightest
    (139, 172, 15),   # 1: light
    (48, 98, 48),     # 2: dark
    (15, 56, 15),     # 3: darkest
)

# Game Boy timing
CYCLES_PER_FRAME = 70_224          # 154 scanlines × 456 T-cycles
FRAME_DURATION = 70_224 / 4_194_304  # ~16.74ms → ~59.7 fps

# Keyboard → joypad button mapping
KEY_MAP = {
    pygame.K_d:      'right',
    pygame.K_a:      'left',
    pygame.K_w:      'up',
    pygame.K_s:      'down',
    pygame.K_k:      'a',
    pygame.K_j:      'b',
    pygame.K_RETURN: 'start',
    pygame.K_DELETE: 'select',
}


class PygameFrontend:
    """Pygame-based frontend for the Game Boy emulator.

    Thin rendering layer: owns the pygame window and event loop,
    delegates all emulation to the GameBoy instance passed at construction.
    The GameBoy core has no knowledge of this class.
    """

    def __init__(self, gameboy, scale=3):
        self._gb = gameboy
        self._scale = scale
        self._running = False

        pygame.init()
        self._screen = pygame.display.set_mode(
            (GB_WIDTH * scale, GB_HEIGHT * scale)
        )
        pygame.display.set_caption("Game Boy")

        # Native 160×144 surface, scaled up on blit
        self._surface = pygame.Surface((GB_WIDTH, GB_HEIGHT))

    def run(self):
        """Main emulation loop: run one frame, render, handle input, repeat."""
        self._running = True

        while self._running:
            frame_start = time.perf_counter()

            # 1. Process input events
            self._handle_events()

            # 2. Run one frame of emulation (70,224 T-cycles)
            target = self._gb.cpu.current_cycles + CYCLES_PER_FRAME
            self._gb.run(max_cycles=target)

            # 3. Render framebuffer to the window
            self._render_frame()

            # 4. Throttle to real-time
            elapsed = time.perf_counter() - frame_start
            remaining = FRAME_DURATION - elapsed
            if remaining > 0:
                time.sleep(remaining)

        pygame.quit()

    def _handle_events(self):
        """Process pygame events: window close, key press/release."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._running = False
                button = KEY_MAP.get(event.key)
                if button:
                    self._gb.joypad.press(button)
            elif event.type == pygame.KEYUP:
                button = KEY_MAP.get(event.key)
                if button:
                    self._gb.joypad.release(button)

    def _render_frame(self):
        """Blit the GB framebuffer onto the pygame window."""
        framebuffer = self._gb.get_framebuffer()

        for y in range(GB_HEIGHT):
            row = framebuffer[y]
            for x in range(GB_WIDTH):
                self._surface.set_at((x, y), DMG_PALETTE[row[x]])

        scaled = pygame.transform.scale(
            self._surface,
            (GB_WIDTH * self._scale, GB_HEIGHT * self._scale),
        )
        self._screen.blit(scaled, (0, 0))
        pygame.display.flip()
