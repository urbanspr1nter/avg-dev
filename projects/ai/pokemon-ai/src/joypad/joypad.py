class Joypad:
    """Game Boy joypad (P1/JOYP register at 0xFF00).

    The Game Boy has 8 buttons split into two groups, read through a single
    register using select-line multiplexing. Everything is active-low: a 0 bit
    means "selected" or "pressed", a 1 bit means "not selected" or "not pressed".

    Register layout (0xFF00):
      Bit 7-6: Unused (always read 1)
      Bit 5:   P15 — select action buttons (0 = selected)
      Bit 4:   P14 — select d-pad (0 = selected)
      Bit 3:   Down  / Start   (0 = pressed)
      Bit 2:   Up    / Select  (0 = pressed)
      Bit 1:   Left  / B       (0 = pressed)
      Bit 0:   Right / A       (0 = pressed)

    Games write bits 4-5 to select which button group to read, then read
    bits 0-3 to get the button state for that group.

    Button groups:
      D-pad   (selected by bit 4 = 0): right=bit0, left=bit1, up=bit2, down=bit3
      Action  (selected by bit 5 = 0): a=bit0, b=bit1, select=bit2, start=bit3

    Joypad interrupt (IF bit 4) fires on any button press (1->0 transition).
    """

    # Button name -> (group, bit position)
    # group: 'dpad' or 'action'
    BUTTON_MAP = {
        'right':  ('dpad', 0),
        'left':   ('dpad', 1),
        'up':     ('dpad', 2),
        'down':   ('dpad', 3),
        'a':      ('action', 0),
        'b':      ('action', 1),
        'select': ('action', 2),
        'start':  ('action', 3),
    }

    def __init__(self):
        self._select = 0x30      # Bits 4-5: both groups deselected (idle)
        self._dpad = 0x0F        # Bits 0-3: no d-pad buttons pressed (all high)
        self._buttons = 0x0F     # Bits 0-3: no action buttons pressed (all high)
        self._memory = None      # Set by Memory.load_joypad() for IF access

    def read(self, address):
        """Read the joypad register (0xFF00)."""
        result = 0xC0 | self._select  # Bits 7-6 always 1, plus select lines

        select = self._select & 0x30
        if select == 0x00:
            # Both groups selected — AND the two (0 if either pressed)
            result |= (self._dpad & self._buttons)
        elif not (select & 0x10):
            # Bit 4 low = d-pad selected
            result |= self._dpad
        elif not (select & 0x20):
            # Bit 5 low = action selected
            result |= self._buttons
        else:
            # Neither selected (0x30) — bits 0-3 all high
            result |= 0x0F

        return result

    def write(self, address, value):
        """Write the joypad register (0xFF00).

        Only bits 4-5 (select lines) are writable. Bits 0-3 reflect button
        state and are read-only. Bits 6-7 are unused.
        """
        self._select = value & 0x30

    def press(self, button):
        """Press a button. Fires joypad interrupt on 1->0 transition.

        Args:
            button: One of 'right', 'left', 'up', 'down', 'a', 'b', 'select', 'start'
        """
        group, bit = self.BUTTON_MAP[button]
        mask = 1 << bit

        if group == 'dpad':
            was_released = (self._dpad & mask) != 0
            self._dpad &= ~mask & 0x0F
        else:
            was_released = (self._buttons & mask) != 0
            self._buttons &= ~mask & 0x0F

        if was_released:
            self._request_joypad_interrupt()

    def release(self, button):
        """Release a button.

        Args:
            button: One of 'right', 'left', 'up', 'down', 'a', 'b', 'select', 'start'
        """
        group, bit = self.BUTTON_MAP[button]
        mask = 1 << bit

        if group == 'dpad':
            self._dpad |= mask
        else:
            self._buttons |= mask

    def _request_joypad_interrupt(self):
        """Set bit 4 of the IF register to request a joypad interrupt."""
        if self._memory is not None:
            if_val = self._memory.memory[0xFF0F]
            self._memory.memory[0xFF0F] = if_val | 0x10
