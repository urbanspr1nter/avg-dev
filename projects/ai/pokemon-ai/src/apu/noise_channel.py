class NoiseChannel:
    """Noise channel (CH4) with linear feedback shift register.

    Generates pseudo-random noise using a 15-bit LFSR. An optional
    7-bit mode produces more regular/tonal noise by also writing the
    XOR result into bit 6.
    """

    DIVISOR_TABLE = [8, 16, 32, 48, 64, 80, 96, 112]

    def __init__(self):
        # Channel state
        self._enabled = False
        self._dac_enabled = False

        # Registers
        self._nr41 = 0  # Length load
        self._nr42 = 0  # Volume envelope
        self._nr43 = 0  # Clock shift / width / divisor
        self._nr44 = 0  # Trigger / length enable

        # LFSR
        self._lfsr = 0x7FFF  # 15-bit, all 1s

        # Frequency timer
        self._freq_timer = 0
        self._clock_shift = 0
        self._divisor_code = 0
        self._width_mode = False

        # Length counter
        self._length_counter = 0
        self._length_enabled = False

        # Volume envelope
        self._volume = 0
        self._env_timer = 0
        self._env_pace = 0
        self._env_direction = 0  # +1 = increase, -1 = decrease

    def tick(self, cycles):
        """Advance the frequency timer by the given number of T-cycles."""
        if not self._enabled:
            return
        self._freq_timer -= cycles
        while self._freq_timer <= 0:
            self._freq_timer += self._get_timer_period()
            # Clock the LFSR
            xor_bit = (self._lfsr & 1) ^ ((self._lfsr >> 1) & 1)
            self._lfsr >>= 1
            self._lfsr |= (xor_bit << 14)  # Set bit 14
            if self._width_mode:
                # 7-bit mode: also set bit 6
                self._lfsr = (self._lfsr & ~0x40) | (xor_bit << 6)

    def _get_timer_period(self):
        """Calculate the timer period from clock shift and divisor code."""
        divisor = self.DIVISOR_TABLE[self._divisor_code]
        period = divisor << self._clock_shift
        return max(period, 1)  # Ensure we don't get stuck at 0

    def clock_length(self):
        """Clock the length counter (called at 256 Hz by frame sequencer)."""
        if self._length_enabled and self._length_counter > 0:
            self._length_counter -= 1
            if self._length_counter == 0:
                self._enabled = False

    def clock_envelope(self):
        """Clock the volume envelope (called at 64 Hz by frame sequencer)."""
        if self._env_pace == 0:
            return
        self._env_timer -= 1
        if self._env_timer <= 0:
            self._env_timer = self._env_pace
            new_volume = self._volume + self._env_direction
            if 0 <= new_volume <= 15:
                self._volume = new_volume

    def trigger(self):
        """Handle trigger event (NR44 bit 7 written)."""
        self._enabled = True
        if self._length_counter == 0:
            self._length_counter = 64

        # Reload frequency timer
        self._freq_timer = self._get_timer_period()

        # Reload envelope
        self._volume = (self._nr42 >> 4) & 0x0F
        self._env_direction = 1 if (self._nr42 & 0x08) else -1
        self._env_pace = self._nr42 & 0x07
        self._env_timer = self._env_pace if self._env_pace > 0 else 8

        # Reset LFSR
        self._lfsr = 0x7FFF

        if not self._dac_enabled:
            self._enabled = False

    def get_output(self):
        """Return the current digital output (0-15)."""
        if not self._enabled or not self._dac_enabled:
            return 0
        # Output is inverted bit 0 of LFSR
        return (~self._lfsr & 1) * self._volume

    def is_active(self):
        """Return True if the channel is enabled and DAC is on."""
        return self._enabled and self._dac_enabled

    def read(self, reg_offset):
        """Read a channel register by offset (0-3).

        Returns the raw register value. The APU applies read masks.
        """
        if reg_offset == 0:
            return self._nr41
        elif reg_offset == 1:
            return self._nr42
        elif reg_offset == 2:
            return self._nr43
        elif reg_offset == 3:
            return self._nr44
        return 0xFF

    def write(self, reg_offset, value):
        """Write a channel register by offset (0-3)."""
        value = value & 0xFF
        if reg_offset == 0:
            self._nr41 = value
            self._length_counter = 64 - (value & 0x3F)
        elif reg_offset == 1:
            self._nr42 = value
            self._dac_enabled = (value & 0xF8) != 0
            if not self._dac_enabled:
                self._enabled = False
        elif reg_offset == 2:
            self._nr43 = value
            self._clock_shift = (value >> 4) & 0x0F
            self._width_mode = bool(value & 0x08)
            self._divisor_code = value & 0x07
        elif reg_offset == 3:
            self._nr44 = value
            self._length_enabled = bool(value & 0x40)
            if value & 0x80:  # Trigger
                self.trigger()

    def save_state(self):
        return {
            'enabled': self._enabled,
            'dac_enabled': self._dac_enabled,
            'nr41': self._nr41,
            'nr42': self._nr42,
            'nr43': self._nr43,
            'nr44': self._nr44,
            'lfsr': self._lfsr,
            'freq_timer': self._freq_timer,
            'clock_shift': self._clock_shift,
            'divisor_code': self._divisor_code,
            'width_mode': self._width_mode,
            'length_counter': self._length_counter,
            'length_enabled': self._length_enabled,
            'volume': self._volume,
            'env_timer': self._env_timer,
            'env_pace': self._env_pace,
            'env_direction': self._env_direction,
        }

    def load_state(self, state):
        self._enabled = state['enabled']
        self._dac_enabled = state['dac_enabled']
        self._nr41 = state['nr41']
        self._nr42 = state['nr42']
        self._nr43 = state['nr43']
        self._nr44 = state['nr44']
        self._lfsr = state['lfsr']
        self._freq_timer = state['freq_timer']
        self._clock_shift = state['clock_shift']
        self._divisor_code = state['divisor_code']
        self._width_mode = state['width_mode']
        self._length_counter = state['length_counter']
        self._length_enabled = state['length_enabled']
        self._volume = state['volume']
        self._env_timer = state['env_timer']
        self._env_pace = state['env_pace']
        self._env_direction = state['env_direction']

    def power_off(self):
        """Reset all state when APU is powered off."""
        self._enabled = False
        self._nr41 = 0
        self._nr42 = 0
        self._nr43 = 0
        self._nr44 = 0
        self._dac_enabled = False
        self._lfsr = 0x7FFF
        self._freq_timer = 0
        self._clock_shift = 0
        self._divisor_code = 0
        self._width_mode = False
        self._length_counter = 0
        self._length_enabled = False
        self._volume = 0
        self._env_timer = 0
        self._env_pace = 0
        self._env_direction = 0
