import array
import os
import pickle
import time
import wave

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
FAST_FORWARD_MULTIPLIER = 3        # Hold Space for 3x speed

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

    def __init__(self, gameboy, scale=3, wav_path=None, rom_path=None):
        self._gb = gameboy
        self._scale = scale
        self._running = False
        self._fast_forward = False
        self._audio_enabled = True
        self._wav_path = wav_path
        self._wav_file = None
        self._rom_path = rom_path

        pygame.mixer.pre_init(frequency=48000, size=-16, channels=2, buffer=1024)
        pygame.init()
        try:
            pygame.mixer.init()
            self._audio_channel = pygame.mixer.Channel(0)
        except pygame.error:
            self._audio_enabled = False
            self._audio_channel = None

        # Audio streaming buffer: accumulate samples across frames and feed
        # larger chunks to the mixer to avoid gaps between tiny per-frame chunks.
        # Target ~4 frames worth (~3200 stereo samples) per chunk.
        self._audio_buffer = array.array('h')
        self._audio_chunk_size = 4096  # stereo samples (2048 frames × 2 channels)

        self._screen = pygame.display.set_mode(
            (GB_WIDTH * scale, GB_HEIGHT * scale)
        )
        pygame.display.set_caption("Game Boy")

        # Pre-allocated RGB buffer for fast framebuffer → Surface conversion
        self._pixel_buffer = bytearray(GB_WIDTH * GB_HEIGHT * 3)

    def run(self):
        """Main emulation loop: run one frame, render, handle input, repeat."""
        self._running = True

        if self._wav_path:
            self._wav_file = wave.open(self._wav_path, 'wb')
            self._wav_file.setnchannels(2)
            self._wav_file.setsampwidth(2)  # 16-bit
            self._wav_file.setframerate(48000)

        try:
            while self._running:
                frame_start = time.perf_counter()

                # 1. Process input events
                self._handle_events()

                # 2. Run emulation frames
                #    Normal: 1 frame, then render. Fast-forward: run N frames,
                #    only render the last one (rendering is the bottleneck).
                frames_to_run = FAST_FORWARD_MULTIPLIER if self._fast_forward else 1
                for _ in range(frames_to_run):
                    target = self._gb.cpu.current_cycles + CYCLES_PER_FRAME
                    self._gb.run(max_cycles=target)

                # 3. Drain audio samples
                self._drain_audio()

                # 4. Render framebuffer to the window
                self._render_frame()

                # 5. Throttle to real-time
                elapsed = time.perf_counter() - frame_start
                remaining = FRAME_DURATION - elapsed
                if remaining > 0:
                    time.sleep(remaining)
        finally:
            if self._wav_file:
                self._wav_file.close()
                print(f"Audio saved to {self._wav_path}")
            pygame.quit()

    def _handle_events(self):
        """Process pygame events: window close, key press/release."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._running = False
                elif event.key == pygame.K_SPACE:
                    self._fast_forward = True
                elif event.key == pygame.K_m:
                    self._audio_enabled = not self._audio_enabled
                elif (event.mod & pygame.KMOD_CTRL) and pygame.K_1 <= event.key <= pygame.K_9:
                    self._save_state(event.key - pygame.K_1 + 1)
                elif not (event.mod & (pygame.KMOD_CTRL | pygame.KMOD_ALT | pygame.KMOD_SHIFT)) \
                        and pygame.K_1 <= event.key <= pygame.K_9:
                    self._load_state(event.key - pygame.K_1 + 1)
                else:
                    button = KEY_MAP.get(event.key)
                    if button:
                        self._gb.joypad.press(button)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self._fast_forward = False
                else:
                    button = KEY_MAP.get(event.key)
                    if button:
                        self._gb.joypad.release(button)

    def _save_state(self, slot):
        """Save emulator state to the given slot."""
        if self._rom_path is None:
            return
        path = f"{self._rom_path}.state{slot}"
        try:
            state = self._gb.save_state()
            with open(path, 'wb') as f:
                pickle.dump(state, f)
            print(f"State saved to slot {slot}")
        except OSError as e:
            print(f"Failed to save state slot {slot}: {e}")

    def _load_state(self, slot):
        """Load emulator state from the given slot."""
        if self._rom_path is None:
            return
        path = f"{self._rom_path}.state{slot}"
        if not os.path.exists(path):
            print(f"No save state in slot {slot}")
            return
        try:
            with open(path, 'rb') as f:
                state = pickle.load(f)
            self._gb.load_state(state)
            print(f"State loaded from slot {slot}")
        except (OSError, pickle.UnpicklingError, ValueError, KeyError) as e:
            print(f"Failed to load state slot {slot}: {e}")

    def _drain_audio(self):
        """Convert APU sample buffer to PCM for playback and/or WAV export."""
        samples = self._gb.apu.drain_samples()
        if not samples:
            return

        audio_buf = self._audio_buffer
        for left, right in samples:
            audio_buf.append(int(max(-1.0, min(1.0, left)) * 32767))
            audio_buf.append(int(max(-1.0, min(1.0, right)) * 32767))

        # Write to WAV file if recording
        if self._wav_file:
            self._wav_file.writeframes(audio_buf[-len(samples) * 2:].tobytes())

        # Feed to mixer when we have enough samples for a chunk
        if self._audio_enabled and self._audio_channel is not None:
            # Cap buffer to ~100ms to prevent latency buildup during fast-forward
            max_buf = 48000 * 2 // 10  # 100ms of stereo samples
            if len(audio_buf) > max_buf:
                del audio_buf[:len(audio_buf) - max_buf]

            chunk_size = self._audio_chunk_size
            while len(audio_buf) >= chunk_size:
                chunk = array.array('h', audio_buf[:chunk_size])
                del audio_buf[:chunk_size]
                sound = pygame.mixer.Sound(buffer=chunk)
                if not self._audio_channel.get_busy():
                    self._audio_channel.play(sound)
                else:
                    self._audio_channel.queue(sound)
                    break  # Only 1 queued sound allowed; wait for next drain

    def _render_frame(self):
        """Blit the GB framebuffer onto the pygame window."""
        framebuffer = self._gb.get_framebuffer()
        buf = self._pixel_buffer

        offset = 0
        for y in range(GB_HEIGHT):
            row = framebuffer[y]
            for x in range(GB_WIDTH):
                r, g, b = DMG_PALETTE[row[x]]
                buf[offset] = r
                buf[offset + 1] = g
                buf[offset + 2] = b
                offset += 3

        image = pygame.image.frombuffer(buf, (GB_WIDTH, GB_HEIGHT), 'RGB')
        scaled = pygame.transform.scale(
            image,
            (GB_WIDTH * self._scale, GB_HEIGHT * self._scale),
        )
        self._screen.blit(scaled, (0, 0))
        pygame.display.flip()
