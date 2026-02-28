import unittest

from src.joypad.joypad import Joypad
from src.memory.gb_memory import Memory


class TestJoypadRegister(unittest.TestCase):
    """Test joypad register read/write and select-line multiplexing."""

    def setUp(self):
        self.joypad = Joypad()

    def test_default_read_no_buttons(self):
        """Default state: both groups deselected, no buttons pressed → 0xFF."""
        # Select = 0x30 (neither selected), buttons all high → 0xC0 | 0x30 | 0x0F = 0xFF
        self.assertEqual(self.joypad.read(0xFF00), 0xFF)

    def test_write_select_dpad(self):
        """Writing 0x20 selects d-pad (bit 4 low)."""
        self.joypad.write(0xFF00, 0x20)
        result = self.joypad.read(0xFF00)
        # Bits 7-6 = 11, bit 5 = 1, bit 4 = 0, bits 0-3 = 1111 (no buttons)
        self.assertEqual(result, 0xEF)

    def test_write_select_action(self):
        """Writing 0x10 selects action buttons (bit 5 low)."""
        self.joypad.write(0xFF00, 0x10)
        result = self.joypad.read(0xFF00)
        # Bits 7-6 = 11, bit 5 = 0, bit 4 = 1, bits 0-3 = 1111 (no buttons)
        self.assertEqual(result, 0xDF)

    def test_write_select_neither(self):
        """Writing 0x30 deselects both groups — bits 0-3 all high."""
        self.joypad.write(0xFF00, 0x30)
        result = self.joypad.read(0xFF00)
        self.assertEqual(result, 0xFF)

    def test_write_select_both(self):
        """Writing 0x00 selects both groups — AND of d-pad and action."""
        self.joypad.write(0xFF00, 0x00)
        # No buttons pressed: AND of 0x0F and 0x0F = 0x0F
        result = self.joypad.read(0xFF00)
        self.assertEqual(result, 0xCF)

    def test_write_only_affects_select_bits(self):
        """Writing to 0xFF00 only changes bits 4-5, ignores other bits."""
        self.joypad.write(0xFF00, 0xFF)  # All bits set
        # Only bits 4-5 should be stored (0x30)
        self.assertEqual(self.joypad._select, 0x30)

    def test_bits_7_6_always_high(self):
        """Bits 7-6 always read as 1 regardless of state."""
        for select in [0x00, 0x10, 0x20, 0x30]:
            self.joypad.write(0xFF00, select)
            result = self.joypad.read(0xFF00)
            self.assertEqual(result & 0xC0, 0xC0,
                             f"Bits 7-6 not high with select=0x{select:02X}")


class TestJoypadButtons(unittest.TestCase):
    """Test button press/release and visibility through select lines."""

    def setUp(self):
        self.joypad = Joypad()

    # --- D-pad buttons ---

    def test_press_right_visible_with_dpad_selected(self):
        """Pressing right shows as bit 0 low when d-pad is selected."""
        self.joypad.press('right')
        self.joypad.write(0xFF00, 0x20)  # Select d-pad
        result = self.joypad.read(0xFF00)
        self.assertEqual(result & 0x0F, 0x0E)  # bit 0 low

    def test_press_left(self):
        self.joypad.press('left')
        self.joypad.write(0xFF00, 0x20)
        self.assertEqual(self.joypad.read(0xFF00) & 0x0F, 0x0D)  # bit 1 low

    def test_press_up(self):
        self.joypad.press('up')
        self.joypad.write(0xFF00, 0x20)
        self.assertEqual(self.joypad.read(0xFF00) & 0x0F, 0x0B)  # bit 2 low

    def test_press_down(self):
        self.joypad.press('down')
        self.joypad.write(0xFF00, 0x20)
        self.assertEqual(self.joypad.read(0xFF00) & 0x0F, 0x07)  # bit 3 low

    # --- Action buttons ---

    def test_press_a_visible_with_action_selected(self):
        """Pressing A shows as bit 0 low when action is selected."""
        self.joypad.press('a')
        self.joypad.write(0xFF00, 0x10)  # Select action
        result = self.joypad.read(0xFF00)
        self.assertEqual(result & 0x0F, 0x0E)  # bit 0 low

    def test_press_b(self):
        self.joypad.press('b')
        self.joypad.write(0xFF00, 0x10)
        self.assertEqual(self.joypad.read(0xFF00) & 0x0F, 0x0D)  # bit 1 low

    def test_press_select_button(self):
        self.joypad.press('select')
        self.joypad.write(0xFF00, 0x10)
        self.assertEqual(self.joypad.read(0xFF00) & 0x0F, 0x0B)  # bit 2 low

    def test_press_start(self):
        self.joypad.press('start')
        self.joypad.write(0xFF00, 0x10)
        self.assertEqual(self.joypad.read(0xFF00) & 0x0F, 0x07)  # bit 3 low

    # --- Multiplexing ---

    def test_dpad_not_visible_with_action_selected(self):
        """D-pad presses should NOT be visible when action group is selected."""
        self.joypad.press('right')
        self.joypad.write(0xFF00, 0x10)  # Select action (not d-pad)
        result = self.joypad.read(0xFF00)
        self.assertEqual(result & 0x0F, 0x0F)  # All high, right not visible

    def test_action_not_visible_with_dpad_selected(self):
        """Action presses should NOT be visible when d-pad group is selected."""
        self.joypad.press('a')
        self.joypad.write(0xFF00, 0x20)  # Select d-pad (not action)
        result = self.joypad.read(0xFF00)
        self.assertEqual(result & 0x0F, 0x0F)  # All high, A not visible

    # --- Multiple buttons ---

    def test_multiple_dpad_buttons(self):
        """Multiple d-pad buttons pressed simultaneously."""
        self.joypad.press('right')
        self.joypad.press('down')
        self.joypad.write(0xFF00, 0x20)
        result = self.joypad.read(0xFF00)
        # right = bit 0, down = bit 3 → 0x0F & ~0x01 & ~0x08 = 0x06
        self.assertEqual(result & 0x0F, 0x06)

    def test_both_groups_selected_and_of_groups(self):
        """Both groups selected: pressed buttons from either group visible."""
        self.joypad.press('right')  # d-pad bit 0
        self.joypad.press('a')     # action bit 0
        self.joypad.write(0xFF00, 0x00)  # Both selected
        result = self.joypad.read(0xFF00)
        # AND of 0x0E (d-pad) and 0x0E (action) = 0x0E → bit 0 low
        self.assertEqual(result & 0x0F, 0x0E)

    def test_both_groups_mixed_buttons(self):
        """Both groups selected with different buttons from each group."""
        self.joypad.press('right')  # d-pad bit 0
        self.joypad.press('start') # action bit 3
        self.joypad.write(0xFF00, 0x00)
        result = self.joypad.read(0xFF00)
        # AND of 0x0E (d-pad: right) and 0x07 (action: start) = 0x06
        self.assertEqual(result & 0x0F, 0x06)

    # --- Release ---

    def test_release_button(self):
        """Releasing a button sets its bit back to 1."""
        self.joypad.press('a')
        self.joypad.release('a')
        self.joypad.write(0xFF00, 0x10)
        result = self.joypad.read(0xFF00)
        self.assertEqual(result & 0x0F, 0x0F)

    def test_release_one_of_multiple(self):
        """Releasing one button leaves others pressed."""
        self.joypad.press('a')
        self.joypad.press('b')
        self.joypad.release('a')
        self.joypad.write(0xFF00, 0x10)
        result = self.joypad.read(0xFF00)
        # Only B pressed (bit 1 low)
        self.assertEqual(result & 0x0F, 0x0D)


class TestJoypadInterrupt(unittest.TestCase):
    """Test joypad interrupt (IF bit 4) on button press."""

    def setUp(self):
        self.memory = Memory()
        self.joypad = Joypad()
        self.memory.load_joypad(self.joypad)
        # Clear IF register
        self.memory.memory[0xFF0F] = 0x00

    def test_press_fires_interrupt(self):
        """Pressing a button should set IF bit 4."""
        self.joypad.press('a')
        self.assertEqual(self.memory.memory[0xFF0F] & 0x10, 0x10)

    def test_release_does_not_fire_interrupt(self):
        """Releasing a button should NOT fire an interrupt."""
        self.joypad.press('a')
        self.memory.memory[0xFF0F] = 0x00  # Clear IF
        self.joypad.release('a')
        self.assertEqual(self.memory.memory[0xFF0F] & 0x10, 0x00)

    def test_press_already_pressed_no_interrupt(self):
        """Pressing a button that's already pressed should NOT re-fire."""
        self.joypad.press('a')
        self.memory.memory[0xFF0F] = 0x00  # Clear IF
        self.joypad.press('a')  # Already pressed
        self.assertEqual(self.memory.memory[0xFF0F] & 0x10, 0x00)

    def test_multiple_presses_each_fire(self):
        """Each new button press fires its own interrupt."""
        self.joypad.press('a')
        self.assertEqual(self.memory.memory[0xFF0F] & 0x10, 0x10)

        self.memory.memory[0xFF0F] = 0x00  # Clear IF
        self.joypad.press('b')
        self.assertEqual(self.memory.memory[0xFF0F] & 0x10, 0x10)

    def test_interrupt_preserves_other_if_bits(self):
        """Joypad interrupt should not clear other IF bits."""
        self.memory.memory[0xFF0F] = 0x05  # V-Blank + Timer already set
        self.joypad.press('start')
        self.assertEqual(self.memory.memory[0xFF0F], 0x15)  # All three set

    def test_no_interrupt_without_memory(self):
        """Press without memory wired should not crash."""
        standalone = Joypad()
        standalone.press('a')  # Should not raise


class TestJoypadMemoryIntegration(unittest.TestCase):
    """Test joypad through the Memory bus dispatch."""

    def setUp(self):
        self.memory = Memory()
        self.joypad = Joypad()
        self.memory.load_joypad(self.joypad)

    def test_memory_dispatches_read(self):
        """Reading 0xFF00 through memory should go to joypad."""
        # Default: neither group selected, no buttons → 0xFF
        self.assertEqual(self.memory.get_value(0xFF00), 0xFF)

    def test_memory_dispatches_write(self):
        """Writing 0xFF00 through memory should go to joypad."""
        self.memory.set_value(0xFF00, 0x20)  # Select d-pad
        self.assertEqual(self.joypad._select, 0x20)

    def test_write_read_roundtrip(self):
        """Write select through memory, read back through memory."""
        self.memory.set_value(0xFF00, 0x20)  # Select d-pad
        self.joypad.press('right')
        result = self.memory.get_value(0xFF00)
        self.assertEqual(result & 0x0F, 0x0E)  # bit 0 low

    def test_replaces_old_hack_behavior(self):
        """Default joypad returns same result as old hack for 'no buttons'."""
        # Old hack returned 0xC0 | select | 0x0F when no buttons pressed.
        # With select=0x00 (both selected), that's 0xCF.
        self.memory.set_value(0xFF00, 0x00)
        result = self.memory.get_value(0xFF00)
        self.assertEqual(result, 0xCF)


class TestGameBoyJoypadIntegration(unittest.TestCase):
    """Test joypad wiring through the GameBoy class."""

    def test_gameboy_wires_joypad(self):
        """GameBoy should create and wire a joypad."""
        from src.gameboy import GameBoy
        gb = GameBoy()
        self.assertIsNotNone(gb.joypad)
        self.assertIs(gb.memory._joypad, gb.joypad)
        self.assertIs(gb.joypad._memory, gb.memory)

    def test_gameboy_joypad_press_visible(self):
        """Pressing a button through gb.joypad should be visible via memory."""
        from src.gameboy import GameBoy
        gb = GameBoy()
        gb.joypad.press('a')
        gb.memory.set_value(0xFF00, 0x10)  # Select action
        result = gb.memory.get_value(0xFF00)
        self.assertEqual(result & 0x0F, 0x0E)


if __name__ == '__main__':
    unittest.main()
