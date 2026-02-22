class Timer:
    """Game Boy timer subsystem (0xFF04-0xFF07).

    The timer is driven by a 16-bit internal counter that increments every
    T-cycle (4.194 MHz). Four memory-mapped registers expose timer state:

      - DIV  (0xFF04): Upper 8 bits of internal counter. Writing resets to 0.
      - TIMA (0xFF05): Timer counter. Increments at TAC-selected rate.
                       On overflow (255->0), reloads from TMA and fires
                       timer interrupt (IF bit 2).
      - TMA  (0xFF06): Timer modulo. Value loaded into TIMA on overflow.
      - TAC  (0xFF07): Timer control. Bit 2 = enable, bits 1-0 = clock select.

    Clock select (TAC bits 1-0):
      0b00 -> 4096 Hz    (every 1024 T-cycles, internal counter bit 9)
      0b01 -> 262144 Hz  (every 16 T-cycles, internal counter bit 3)
      0b10 -> 65536 Hz   (every 64 T-cycles, internal counter bit 5)
      0b11 -> 16384 Hz   (every 256 T-cycles, internal counter bit 7)

    TIMA increments on the falling edge of the selected internal counter bit.
    """

    # TAC clock select -> which bit of internal counter to monitor
    TAC_CLOCK_BITS = {
        0b00: 9,   # 1024 T-cycles
        0b01: 3,   # 16 T-cycles
        0b10: 5,   # 64 T-cycles
        0b11: 7,   # 256 T-cycles
    }

    def __init__(self):
        self._internal_counter = 0
        self._tima = 0x00
        self._tma = 0x00
        self._tac = 0x00
        self._memory = None  # Set by Memory.load_timer() for IF register access

    def read(self, address):
        """Read a timer register."""
        if address == 0xFF04:
            return (self._internal_counter >> 8) & 0xFF
        if address == 0xFF05:
            return self._tima
        if address == 0xFF06:
            return self._tma
        if address == 0xFF07:
            return self._tac | 0xF8  # Upper 5 bits read as 1
        return 0xFF

    def write(self, address, value):
        """Write a timer register."""
        if address == 0xFF04:
            # Writing ANY value to DIV resets the entire internal counter
            self._internal_counter = 0
        elif address == 0xFF05:
            self._tima = value & 0xFF
        elif address == 0xFF06:
            self._tma = value & 0xFF
        elif address == 0xFF07:
            self._tac = value & 0x07

    def tick(self, cycles):
        """Advance the timer by the given number of T-cycles.

        Called by the CPU run loop after each instruction. For each T-cycle,
        the internal counter increments and, if the timer is enabled, TIMA
        increments on the falling edge of the TAC-selected counter bit.
        """
        timer_enabled = (self._tac & 0x04) != 0
        clock_bit = self.TAC_CLOCK_BITS[self._tac & 0x03]

        for _ in range(cycles):
            old_counter = self._internal_counter
            self._internal_counter = (self._internal_counter + 1) & 0xFFFF

            if not timer_enabled:
                continue

            # Detect falling edge: selected bit was 1, now 0
            old_bit = (old_counter >> clock_bit) & 1
            new_bit = (self._internal_counter >> clock_bit) & 1

            if old_bit == 1 and new_bit == 0:
                self._tima += 1
                if self._tima > 0xFF:
                    self._tima = self._tma  # Reload from TMA
                    self._request_timer_interrupt()

    def _request_timer_interrupt(self):
        """Set bit 2 of the IF register to request a timer interrupt."""
        if self._memory is not None:
            # Read IF, set bit 2 (timer), write back.
            # Use direct memory array access to avoid circular dispatch.
            if_val = self._memory.memory[0xFF0F]
            self._memory.memory[0xFF0F] = if_val | 0x04
