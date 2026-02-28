import unittest
from unittest.mock import MagicMock, patch

from src.frontend.pygame_frontend import (
    CYCLES_PER_FRAME,
    DMG_PALETTE,
    FRAME_DURATION,
    GB_HEIGHT,
    GB_WIDTH,
    KEY_MAP,
)


class TestDMGPalette(unittest.TestCase):
    """Test the classic DMG green palette constants."""

    def test_has_four_entries(self):
        self.assertEqual(len(DMG_PALETTE), 4)

    def test_entries_are_rgb_tuples(self):
        for i, color in enumerate(DMG_PALETTE):
            self.assertEqual(len(color), 3, f"Shade {i} is not an RGB triple")
            for ch in color:
                self.assertGreaterEqual(ch, 0)
                self.assertLessEqual(ch, 255)

    def test_shades_darken_monotonically(self):
        """Each shade should be darker (lower sum of RGB) than the previous."""
        for i in range(1, 4):
            brighter = sum(DMG_PALETTE[i - 1])
            darker = sum(DMG_PALETTE[i])
            self.assertGreater(brighter, darker,
                               f"Shade {i} is not darker than shade {i - 1}")


class TestKeyMap(unittest.TestCase):
    """Test the keyboard-to-joypad button mapping."""

    JOYPAD_BUTTONS = {'right', 'left', 'up', 'down', 'a', 'b', 'select', 'start'}

    def test_covers_all_buttons(self):
        mapped_buttons = set(KEY_MAP.values())
        self.assertEqual(mapped_buttons, self.JOYPAD_BUTTONS)

    def test_no_duplicate_buttons(self):
        buttons = list(KEY_MAP.values())
        self.assertEqual(len(buttons), len(set(buttons)),
                         "Two keys map to the same button")

    def test_eight_entries(self):
        self.assertEqual(len(KEY_MAP), 8)


class TestTimingConstants(unittest.TestCase):
    """Test Game Boy timing constants."""

    def test_cycles_per_frame(self):
        """154 scanlines × 456 dots = 70,224 T-cycles."""
        self.assertEqual(CYCLES_PER_FRAME, 154 * 456)

    def test_frame_duration_approximately_16_74ms(self):
        expected = 70_224 / 4_194_304
        self.assertAlmostEqual(FRAME_DURATION, expected, places=8)

    def test_frame_rate_approximately_59_7_fps(self):
        fps = 1.0 / FRAME_DURATION
        self.assertAlmostEqual(fps, 59.7, delta=0.1)


class TestLCDResolution(unittest.TestCase):
    """Test Game Boy LCD resolution constants."""

    def test_width(self):
        self.assertEqual(GB_WIDTH, 160)

    def test_height(self):
        self.assertEqual(GB_HEIGHT, 144)


class TestFrameCycleAdvancement(unittest.TestCase):
    """Test that running one frame advances the cycle counter correctly."""

    def test_one_frame_advances_by_approximately_70224(self):
        """Run the GameBoy for one frame and check cycle count."""
        from src.gameboy import GameBoy

        gb = GameBoy()
        # Load a minimal ROM so the CPU has something to execute (NOP sled)
        gb.memory.memory[0x0000:0x8000] = [0x00] * 0x8000  # Fill with NOPs
        gb.cpu.registers.PC = 0x0000

        before = gb.cpu.current_cycles
        target = before + CYCLES_PER_FRAME
        gb.run(max_cycles=target)
        after = gb.cpu.current_cycles

        elapsed = after - before
        # Should be at least CYCLES_PER_FRAME (may overshoot by one instruction)
        self.assertGreaterEqual(elapsed, CYCLES_PER_FRAME)
        # Overshoot should be small (max instruction is 24 cycles)
        self.assertLess(elapsed, CYCLES_PER_FRAME + 32)


class TestHandleEvents(unittest.TestCase):
    """Test event handling logic (mocked pygame)."""

    def _make_frontend(self):
        """Create a PygameFrontend with pygame fully mocked."""
        from src.gameboy import GameBoy

        gb = GameBoy()
        with patch('src.frontend.pygame_frontend.pygame') as mock_pg:
            from src.frontend.pygame_frontend import PygameFrontend
            frontend = PygameFrontend(gb, scale=1)
            frontend._mock_pg = mock_pg
        return frontend

    def test_keydown_calls_joypad_press(self):
        """KEYDOWN with a mapped key should call joypad.press()."""
        import pygame as real_pg

        from src.gameboy import GameBoy

        gb = GameBoy()
        gb.joypad.press = MagicMock()

        with patch('src.frontend.pygame_frontend.pygame') as mock_pg:
            # Map mock constants to real values so KEY_MAP works
            mock_pg.K_k = real_pg.K_k
            mock_pg.K_j = real_pg.K_j
            mock_pg.K_w = real_pg.K_w
            mock_pg.K_a = real_pg.K_a
            mock_pg.K_s = real_pg.K_s
            mock_pg.K_d = real_pg.K_d
            mock_pg.K_RETURN = real_pg.K_RETURN
            mock_pg.K_DELETE = real_pg.K_DELETE
            mock_pg.K_ESCAPE = real_pg.K_ESCAPE
            mock_pg.QUIT = real_pg.QUIT
            mock_pg.KEYDOWN = real_pg.KEYDOWN
            mock_pg.KEYUP = real_pg.KEYUP

            from src.frontend.pygame_frontend import PygameFrontend
            frontend = PygameFrontend(gb, scale=1)

            event = MagicMock()
            event.type = real_pg.KEYDOWN
            event.key = real_pg.K_k  # 'a' button
            mock_pg.event.get.return_value = [event]

            frontend._handle_events()
            gb.joypad.press.assert_called_once_with('a')

    def test_keyup_calls_joypad_release(self):
        """KEYUP with a mapped key should call joypad.release()."""
        import pygame as real_pg

        from src.gameboy import GameBoy

        gb = GameBoy()
        gb.joypad.release = MagicMock()

        with patch('src.frontend.pygame_frontend.pygame') as mock_pg:
            mock_pg.K_k = real_pg.K_k
            mock_pg.K_j = real_pg.K_j
            mock_pg.K_w = real_pg.K_w
            mock_pg.K_a = real_pg.K_a
            mock_pg.K_s = real_pg.K_s
            mock_pg.K_d = real_pg.K_d
            mock_pg.K_RETURN = real_pg.K_RETURN
            mock_pg.K_DELETE = real_pg.K_DELETE
            mock_pg.K_ESCAPE = real_pg.K_ESCAPE
            mock_pg.QUIT = real_pg.QUIT
            mock_pg.KEYDOWN = real_pg.KEYDOWN
            mock_pg.KEYUP = real_pg.KEYUP

            from src.frontend.pygame_frontend import PygameFrontend
            frontend = PygameFrontend(gb, scale=1)

            event = MagicMock()
            event.type = real_pg.KEYUP
            event.key = real_pg.K_j  # 'b' button
            mock_pg.event.get.return_value = [event]

            frontend._handle_events()
            gb.joypad.release.assert_called_once_with('b')

    def test_unmapped_key_ignored(self):
        """KEYDOWN with an unmapped key should not call press()."""
        import pygame as real_pg

        from src.gameboy import GameBoy

        gb = GameBoy()
        gb.joypad.press = MagicMock()

        with patch('src.frontend.pygame_frontend.pygame') as mock_pg:
            mock_pg.K_ESCAPE = real_pg.K_ESCAPE
            mock_pg.QUIT = real_pg.QUIT
            mock_pg.KEYDOWN = real_pg.KEYDOWN
            mock_pg.KEYUP = real_pg.KEYUP

            from src.frontend.pygame_frontend import PygameFrontend
            frontend = PygameFrontend(gb, scale=1)

            event = MagicMock()
            event.type = real_pg.KEYDOWN
            event.key = real_pg.K_F1  # Not mapped
            mock_pg.event.get.return_value = [event]

            frontend._handle_events()
            gb.joypad.press.assert_not_called()

    def test_escape_stops_loop(self):
        """Pressing Escape should set _running to False."""
        import pygame as real_pg

        from src.gameboy import GameBoy

        gb = GameBoy()

        with patch('src.frontend.pygame_frontend.pygame') as mock_pg:
            mock_pg.K_ESCAPE = real_pg.K_ESCAPE
            mock_pg.QUIT = real_pg.QUIT
            mock_pg.KEYDOWN = real_pg.KEYDOWN
            mock_pg.KEYUP = real_pg.KEYUP

            from src.frontend.pygame_frontend import PygameFrontend
            frontend = PygameFrontend(gb, scale=1)
            frontend._running = True

            event = MagicMock()
            event.type = real_pg.KEYDOWN
            event.key = real_pg.K_ESCAPE
            mock_pg.event.get.return_value = [event]

            frontend._handle_events()
            self.assertFalse(frontend._running)

    def test_quit_event_stops_loop(self):
        """QUIT event should set _running to False."""
        import pygame as real_pg

        from src.gameboy import GameBoy

        gb = GameBoy()

        with patch('src.frontend.pygame_frontend.pygame') as mock_pg:
            mock_pg.QUIT = real_pg.QUIT
            mock_pg.KEYDOWN = real_pg.KEYDOWN
            mock_pg.KEYUP = real_pg.KEYUP

            from src.frontend.pygame_frontend import PygameFrontend
            frontend = PygameFrontend(gb, scale=1)
            frontend._running = True

            event = MagicMock()
            event.type = real_pg.QUIT
            mock_pg.event.get.return_value = [event]

            frontend._handle_events()
            self.assertFalse(frontend._running)


class TestPostBootState(unittest.TestCase):
    """Test the init_post_boot_state() helper in GameBoy."""

    def test_registers_set_correctly(self):
        from src.gameboy import GameBoy

        gb = GameBoy()
        gb.init_post_boot_state()

        self.assertEqual(gb.cpu.get_register('AF'), 0x01B0)
        self.assertEqual(gb.cpu.get_register('BC'), 0x0013)
        self.assertEqual(gb.cpu.get_register('DE'), 0x00D8)
        self.assertEqual(gb.cpu.get_register('HL'), 0x014D)
        self.assertEqual(gb.cpu.registers.SP, 0xFFFE)
        self.assertEqual(gb.cpu.registers.PC, 0x0100)

    def test_if_register_set(self):
        from src.gameboy import GameBoy

        gb = GameBoy()
        gb.init_post_boot_state()

        # IF register is masked to 5 bits by hardware dispatch
        # 0xE1 & 0x1F = 0x01 (V-Blank flag set)
        self.assertEqual(gb.memory.get_value(0xFF0F), 0x01)


if __name__ == '__main__':
    unittest.main()
