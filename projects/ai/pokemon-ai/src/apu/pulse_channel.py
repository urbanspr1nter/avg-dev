class PulseChannel:
    """Pulse wave channel (CH1 or CH2).

    CH1 has a frequency sweep unit; CH2 does not.
    Both share the same duty cycle, envelope, length counter, and frequency
    timer logic.
    """

    DUTY_TABLE = [
        [0, 0, 0, 0, 0, 0, 0, 1],  # 12.5%
        [1, 0, 0, 0, 0, 0, 0, 1],  # 25%
        [1, 0, 0, 0, 0, 1, 1, 1],  # 50%
        [0, 1, 1, 1, 1, 1, 1, 0],  # 75%
    ]

    def __init__(self, has_sweep=False):
        self._has_sweep = has_sweep

        # Channel state
        self._enabled = False
        self._dac_enabled = False

        # Registers (raw values)
        self._nrx0 = 0  # Sweep (CH1 only)
        self._nrx1 = 0  # Duty / length load
        self._nrx2 = 0  # Volume envelope
        self._nrx3 = 0  # Period low
        self._nrx4 = 0  # Trigger / length enable / period high

        # Frequency timer
        self._freq_timer = 0
        self._duty_pos = 0
        self._period = 0  # 11-bit period value (combined NRx3 + NRx4 bits 2-0)

        # Length counter
        self._length_counter = 0
        self._length_enabled = False

        # Volume envelope
        self._volume = 0
        self._env_timer = 0
        self._env_pace = 0
        self._env_direction = 0  # +1 = increase, -1 = decrease

        # Sweep (CH1 only)
        self._sweep_shadow = 0
        self._sweep_timer = 0
        self._sweep_enabled = False
        self._sweep_pace = 0
        self._sweep_direction = 0  # 0 = addition, 1 = subtraction
        self._sweep_step = 0
        self._sweep_negate_used = False

    def tick(self, cycles):
        """Advance the frequency timer by the given number of T-cycles."""
        if not self._enabled:
            return
        for _ in range(cycles):
            self._freq_timer -= 1
            if self._freq_timer <= 0:
                self._freq_timer = (2048 - self._period) * 4
                self._duty_pos = (self._duty_pos + 1) & 7

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

    def clock_sweep(self):
        """Clock the sweep unit (called at 128 Hz by frame sequencer, CH1 only)."""
        if not self._has_sweep:
            return
        self._sweep_timer -= 1
        if self._sweep_timer <= 0:
            self._sweep_timer = self._sweep_pace if self._sweep_pace > 0 else 8
            if self._sweep_enabled and self._sweep_pace > 0:
                new_period = self._calculate_sweep()
                if new_period > 2047:
                    self._enabled = False
                    return
                if self._sweep_step > 0:
                    self._sweep_shadow = new_period
                    self._period = new_period
                    self._nrx3 = new_period & 0xFF
                    self._nrx4 = (self._nrx4 & 0xF8) | ((new_period >> 8) & 0x07)
                    # Second overflow check
                    if self._calculate_sweep() > 2047:
                        self._enabled = False

    def _calculate_sweep(self):
        """Calculate the new frequency from the sweep shadow register."""
        shifted = self._sweep_shadow >> self._sweep_step
        if self._sweep_direction:  # subtraction
            self._sweep_negate_used = True
            return self._sweep_shadow - shifted
        return self._sweep_shadow + shifted

    def trigger(self):
        """Handle trigger event (NRx4 bit 7 written)."""
        self._enabled = True
        if self._length_counter == 0:
            self._length_counter = 64

        # Reload frequency timer
        self._freq_timer = (2048 - self._period) * 4

        # Reload envelope
        self._volume = (self._nrx2 >> 4) & 0x0F
        self._env_direction = 1 if (self._nrx2 & 0x08) else -1
        self._env_pace = self._nrx2 & 0x07
        self._env_timer = self._env_pace if self._env_pace > 0 else 8

        # Sweep (CH1 only)
        if self._has_sweep:
            self._sweep_shadow = self._period
            self._sweep_pace = (self._nrx0 >> 4) & 0x07
            self._sweep_direction = (self._nrx0 >> 3) & 0x01
            self._sweep_step = self._nrx0 & 0x07
            self._sweep_timer = self._sweep_pace if self._sweep_pace > 0 else 8
            self._sweep_enabled = self._sweep_pace > 0 or self._sweep_step > 0
            self._sweep_negate_used = False
            # If step is non-zero, perform overflow check (result NOT written back)
            if self._sweep_step > 0:
                if self._calculate_sweep() > 2047:
                    self._enabled = False

        # DAC check: if DAC is off, channel stays disabled
        if not self._dac_enabled:
            self._enabled = False

    def get_output(self):
        """Return the current digital output (0-15)."""
        if not self._enabled or not self._dac_enabled:
            return 0
        duty = (self._nrx1 >> 6) & 0x03
        return self.DUTY_TABLE[duty][self._duty_pos] * self._volume

    def is_active(self):
        """Return True if the channel is enabled and DAC is on."""
        return self._enabled and self._dac_enabled

    def read(self, reg_offset):
        """Read a channel register by offset (0-4).

        Returns the raw register value. The APU applies read masks.
        """
        if reg_offset == 0:
            return self._nrx0
        elif reg_offset == 1:
            return self._nrx1
        elif reg_offset == 2:
            return self._nrx2
        elif reg_offset == 3:
            return self._nrx3
        elif reg_offset == 4:
            return self._nrx4
        return 0xFF

    def write(self, reg_offset, value):
        """Write a channel register by offset (0-4)."""
        value = value & 0xFF
        if reg_offset == 0:
            # Sweep register (CH1 only)
            self._nrx0 = value
            if self._has_sweep:
                new_direction = (value >> 3) & 0x01
                # Switching from subtraction to addition after negate was used
                # disables the channel
                if self._sweep_negate_used and self._sweep_direction == 1 and new_direction == 0:
                    self._enabled = False
                self._sweep_direction = new_direction
                self._sweep_pace = (value >> 4) & 0x07
                self._sweep_step = value & 0x07

        elif reg_offset == 1:
            self._nrx1 = value
            self._length_counter = 64 - (value & 0x3F)

        elif reg_offset == 2:
            self._nrx2 = value
            self._dac_enabled = (value & 0xF8) != 0
            if not self._dac_enabled:
                self._enabled = False

        elif reg_offset == 3:
            self._nrx3 = value
            self._period = (self._period & 0x700) | value

        elif reg_offset == 4:
            self._nrx4 = value
            self._period = (self._period & 0xFF) | ((value & 0x07) << 8)
            self._length_enabled = bool(value & 0x40)
            if value & 0x80:  # Trigger
                self.trigger()

    def save_state(self):
        state = {
            'enabled': self._enabled,
            'dac_enabled': self._dac_enabled,
            'nrx0': self._nrx0,
            'nrx1': self._nrx1,
            'nrx2': self._nrx2,
            'nrx3': self._nrx3,
            'nrx4': self._nrx4,
            'freq_timer': self._freq_timer,
            'duty_pos': self._duty_pos,
            'period': self._period,
            'length_counter': self._length_counter,
            'length_enabled': self._length_enabled,
            'volume': self._volume,
            'env_timer': self._env_timer,
            'env_pace': self._env_pace,
            'env_direction': self._env_direction,
        }
        if self._has_sweep:
            state['sweep_shadow'] = self._sweep_shadow
            state['sweep_timer'] = self._sweep_timer
            state['sweep_enabled'] = self._sweep_enabled
            state['sweep_pace'] = self._sweep_pace
            state['sweep_direction'] = self._sweep_direction
            state['sweep_step'] = self._sweep_step
            state['sweep_negate_used'] = self._sweep_negate_used
        return state

    def load_state(self, state):
        self._enabled = state['enabled']
        self._dac_enabled = state['dac_enabled']
        self._nrx0 = state['nrx0']
        self._nrx1 = state['nrx1']
        self._nrx2 = state['nrx2']
        self._nrx3 = state['nrx3']
        self._nrx4 = state['nrx4']
        self._freq_timer = state['freq_timer']
        self._duty_pos = state['duty_pos']
        self._period = state['period']
        self._length_counter = state['length_counter']
        self._length_enabled = state['length_enabled']
        self._volume = state['volume']
        self._env_timer = state['env_timer']
        self._env_pace = state['env_pace']
        self._env_direction = state['env_direction']
        if self._has_sweep:
            self._sweep_shadow = state['sweep_shadow']
            self._sweep_timer = state['sweep_timer']
            self._sweep_enabled = state['sweep_enabled']
            self._sweep_pace = state['sweep_pace']
            self._sweep_direction = state['sweep_direction']
            self._sweep_step = state['sweep_step']
            self._sweep_negate_used = state['sweep_negate_used']

    def power_off(self):
        """Reset all state when APU is powered off."""
        self._enabled = False
        self._nrx0 = 0
        self._nrx1 = 0
        self._nrx2 = 0
        self._nrx3 = 0
        self._nrx4 = 0
        self._dac_enabled = False
        self._period = 0
        self._length_counter = 0
        self._length_enabled = False
        self._volume = 0
        self._env_timer = 0
        self._env_pace = 0
        self._env_direction = 0
        self._freq_timer = 0
        self._duty_pos = 0
        if self._has_sweep:
            self._sweep_shadow = 0
            self._sweep_timer = 0
            self._sweep_enabled = False
            self._sweep_pace = 0
            self._sweep_direction = 0
            self._sweep_step = 0
            self._sweep_negate_used = False
