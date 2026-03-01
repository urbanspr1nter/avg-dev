class WaveChannel:
    """Wave channel (CH3) with 32-sample programmable waveform.

    Plays back 4-bit samples from wave RAM (0xFF30-0xFF3F) at a
    configurable frequency, with a volume shift applied.
    """

    # NR32 volume code -> right-shift amount
    VOLUME_SHIFT = {0: 4, 1: 0, 2: 1, 3: 2}

    def __init__(self):
        # Channel state
        self._enabled = False
        self._dac_enabled = False

        # Registers
        self._nr30 = 0  # DAC enable
        self._nr31 = 0  # Length load
        self._nr32 = 0  # Volume code
        self._nr33 = 0  # Period low
        self._nr34 = 0  # Trigger / length enable / period high

        # Wave RAM: 16 bytes = 32 x 4-bit samples
        self._wave_ram = bytearray(16)

        # Frequency timer
        self._freq_timer = 0
        self._wave_pos = 0  # 0-31
        self._period = 0  # 11-bit
        self._sample_buffer = 0  # Current 4-bit sample

        # Length counter
        self._length_counter = 0
        self._length_enabled = False

    def tick(self, cycles):
        """Advance the frequency timer by the given number of T-cycles."""
        if not self._enabled:
            return
        for _ in range(cycles):
            self._freq_timer -= 1
            if self._freq_timer <= 0:
                self._freq_timer = (2048 - self._period) * 2
                self._wave_pos = (self._wave_pos + 1) & 31
                # Read sample from wave RAM
                byte_idx = self._wave_pos >> 1
                if self._wave_pos & 1:
                    self._sample_buffer = self._wave_ram[byte_idx] & 0x0F
                else:
                    self._sample_buffer = (self._wave_ram[byte_idx] >> 4) & 0x0F

    def clock_length(self):
        """Clock the length counter (called at 256 Hz by frame sequencer)."""
        if self._length_enabled and self._length_counter > 0:
            self._length_counter -= 1
            if self._length_counter == 0:
                self._enabled = False

    def trigger(self):
        """Handle trigger event (NR34 bit 7 written)."""
        self._enabled = True
        if self._length_counter == 0:
            self._length_counter = 256
        self._freq_timer = (2048 - self._period) * 2
        self._wave_pos = 0

        if not self._dac_enabled:
            self._enabled = False

    def get_output(self):
        """Return the current digital output (0-15)."""
        if not self._enabled or not self._dac_enabled:
            return 0
        volume_code = (self._nr32 >> 5) & 0x03
        shift = self.VOLUME_SHIFT[volume_code]
        return self._sample_buffer >> shift

    def is_active(self):
        """Return True if the channel is enabled and DAC is on."""
        return self._enabled and self._dac_enabled

    def read(self, reg_offset):
        """Read a channel register by offset (0-4).

        Returns the raw register value. The APU applies read masks.
        """
        if reg_offset == 0:
            return self._nr30
        elif reg_offset == 1:
            return self._nr31
        elif reg_offset == 2:
            return self._nr32
        elif reg_offset == 3:
            return self._nr33
        elif reg_offset == 4:
            return self._nr34
        return 0xFF

    def write(self, reg_offset, value):
        """Write a channel register by offset (0-4)."""
        value = value & 0xFF
        if reg_offset == 0:
            self._nr30 = value
            self._dac_enabled = bool(value & 0x80)
            if not self._dac_enabled:
                self._enabled = False
        elif reg_offset == 1:
            self._nr31 = value
            self._length_counter = 256 - value
        elif reg_offset == 2:
            self._nr32 = value
        elif reg_offset == 3:
            self._nr33 = value
            self._period = (self._period & 0x700) | value
        elif reg_offset == 4:
            self._nr34 = value
            self._period = (self._period & 0xFF) | ((value & 0x07) << 8)
            self._length_enabled = bool(value & 0x40)
            if value & 0x80:  # Trigger
                self.trigger()

    def read_wave_ram(self, address):
        """Read a byte from wave RAM (0xFF30-0xFF3F)."""
        return self._wave_ram[address - 0xFF30]

    def write_wave_ram(self, address, value):
        """Write a byte to wave RAM (0xFF30-0xFF3F)."""
        self._wave_ram[address - 0xFF30] = value & 0xFF

    def power_off(self):
        """Reset all state when APU is powered off (wave RAM preserved)."""
        self._enabled = False
        self._nr30 = 0
        self._nr31 = 0
        self._nr32 = 0
        self._nr33 = 0
        self._nr34 = 0
        self._dac_enabled = False
        self._period = 0
        self._length_counter = 0
        self._length_enabled = False
        self._freq_timer = 0
        self._wave_pos = 0
        self._sample_buffer = 0
        # Wave RAM is NOT cleared on power off
