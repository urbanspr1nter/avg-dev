from src.apu.pulse_channel import PulseChannel
from src.apu.wave_channel import WaveChannel
from src.apu.noise_channel import NoiseChannel


class APU:
    """Game Boy Audio Processing Unit.

    Manages 4 sound channels, a frame sequencer, stereo mixing, and
    sample output. Register range: 0xFF10-0xFF3F.

    The APU is ticked by the CPU after each instruction (same pattern as
    Timer and PPU). It generates stereo samples at 48 kHz into a buffer
    that the frontend can drain for audio playback.
    """

    SAMPLE_RATE = 48000
    CPU_CLOCK = 4_194_304
    SAMPLE_PERIOD = CPU_CLOCK / SAMPLE_RATE  # ~87.38 T-cycles
    FRAME_SEQUENCER_PERIOD = 8192  # T-cycles per frame sequencer step

    # Register read masks: unused bits read as 1
    READ_MASKS = {
        0xFF10: 0x80, 0xFF11: 0x3F, 0xFF12: 0x00, 0xFF13: 0xFF, 0xFF14: 0xBF,
        0xFF16: 0x3F, 0xFF17: 0x00, 0xFF18: 0xFF, 0xFF19: 0xBF,
        0xFF1A: 0x7F, 0xFF1B: 0xFF, 0xFF1C: 0x9F, 0xFF1D: 0xFF, 0xFF1E: 0xBF,
        0xFF20: 0xFF, 0xFF21: 0x00, 0xFF22: 0x00, 0xFF23: 0xBF,
        0xFF24: 0x00, 0xFF25: 0x00, 0xFF26: 0x70,
    }

    def __init__(self):
        # Channels
        self._ch1 = PulseChannel(has_sweep=True)
        self._ch2 = PulseChannel(has_sweep=False)
        self._ch3 = WaveChannel()
        self._ch4 = NoiseChannel()

        # Master control registers
        self._nr50 = 0  # Master volume / VIN panning
        self._nr51 = 0  # Channel panning
        self._power = False  # NR52 bit 7

        # Frame sequencer
        self._fs_counter = 0
        self._fs_step = 0

        # Sample generation
        self._sample_counter = 0.0
        self._sample_buffer = []

        # High-pass filter state (removes DC offset)
        self._hpf_capacitor_left = 0.0
        self._hpf_capacitor_right = 0.0
        # Charge factor adjusted for 48 kHz sample rate
        # DMG factor at native rate: 0.999958
        # Adjusted: 0.999958 ^ (4194304 / 48000) ≈ 0.996
        self._hpf_charge_factor = 0.996

    def tick(self, cycles):
        """Advance the APU by the given number of T-cycles."""
        if not self._power:
            return

        for _ in range(cycles):
            # Frame sequencer
            self._fs_counter += 1
            if self._fs_counter >= self.FRAME_SEQUENCER_PERIOD:
                self._fs_counter = 0
                self._clock_frame_sequencer()

            # Tick channel frequency timers
            self._ch1.tick(1)
            self._ch2.tick(1)
            self._ch3.tick(1)
            self._ch4.tick(1)

            # Sample generation at target rate
            self._sample_counter += 1.0
            if self._sample_counter >= self.SAMPLE_PERIOD:
                self._sample_counter -= self.SAMPLE_PERIOD
                sample = self._mix_channels()
                self._sample_buffer.append(sample)

    def _clock_frame_sequencer(self):
        """Clock the frame sequencer step and dispatch to channel modulators."""
        step = self._fs_step

        # Length counter: steps 0, 2, 4, 6
        if step % 2 == 0:
            self._ch1.clock_length()
            self._ch2.clock_length()
            self._ch3.clock_length()
            self._ch4.clock_length()

        # Sweep: steps 2, 6
        if step in (2, 6):
            self._ch1.clock_sweep()

        # Envelope: step 7
        if step == 7:
            self._ch1.clock_envelope()
            self._ch2.clock_envelope()
            self._ch4.clock_envelope()

        self._fs_step = (self._fs_step + 1) & 7

    def _mix_channels(self):
        """Mix all channels into a stereo sample pair (left, right).

        Returns a tuple of (left, right) floats in approximately -1.0 to +1.0.
        """
        # Get DAC outputs for each channel
        channels = [self._ch1, self._ch2, self._ch3, self._ch4]
        dac_outputs = []
        for ch in channels:
            if ch._dac_enabled:
                dac_outputs.append((ch.get_output() / 7.5) - 1.0)
            else:
                dac_outputs.append(0.0)

        left = 0.0
        right = 0.0

        # NR51 panning: bits 4-7 = left, bits 0-3 = right
        for i, dac_out in enumerate(dac_outputs):
            if self._nr51 & (0x10 << i):  # Left
                left += dac_out
            if self._nr51 & (0x01 << i):  # Right
                right += dac_out

        # Normalize (up to 4 channels summed)
        left /= 4.0
        right /= 4.0

        # Apply master volume from NR50
        left_volume = ((self._nr50 >> 4) & 0x07) + 1
        right_volume = (self._nr50 & 0x07) + 1
        left *= left_volume / 8.0
        right *= right_volume / 8.0

        # High-pass filter
        left, self._hpf_capacitor_left = self._high_pass(
            left, self._hpf_capacitor_left)
        right, self._hpf_capacitor_right = self._high_pass(
            right, self._hpf_capacitor_right)

        return (left, right)

    def _high_pass(self, sample, capacitor):
        """Apply a simple high-pass filter to remove DC offset."""
        out = sample - capacitor
        capacitor = sample - out * self._hpf_charge_factor
        return (out, capacitor)

    def read(self, address):
        """Read an APU register (0xFF10-0xFF3F)."""
        # Wave RAM
        if 0xFF30 <= address <= 0xFF3F:
            return self._ch3.read_wave_ram(address)

        # Unused gaps
        if address in (0xFF15, 0xFF1F) or 0xFF27 <= address <= 0xFF2F:
            return 0xFF

        # NR52: power + channel status
        if address == 0xFF26:
            status = 0x70  # Bits 4-6 always read as 1
            if self._power:
                status |= 0x80
            if self._ch1.is_active():
                status |= 0x01
            if self._ch2.is_active():
                status |= 0x02
            if self._ch3.is_active():
                status |= 0x04
            if self._ch4.is_active():
                status |= 0x08
            return status

        # When powered off, all registers (except NR52 and wave RAM) read as 0xFF
        if not self._power:
            return 0xFF

        # Master control registers
        if address == 0xFF24:
            return self._nr50
        if address == 0xFF25:
            return self._nr51

        # Channel registers
        raw = self._read_channel_register(address)
        mask = self.READ_MASKS.get(address, 0xFF)
        return raw | mask

    def _read_channel_register(self, address):
        """Route a register read to the appropriate channel."""
        if 0xFF10 <= address <= 0xFF14:
            return self._ch1.read(address - 0xFF10)
        if 0xFF16 <= address <= 0xFF19:
            return self._ch2.read(address - 0xFF15)
        if 0xFF1A <= address <= 0xFF1E:
            return self._ch3.read(address - 0xFF1A)
        if 0xFF20 <= address <= 0xFF23:
            return self._ch4.read(address - 0xFF20)
        return 0xFF

    def write(self, address, value):
        """Write an APU register (0xFF10-0xFF3F)."""
        value = value & 0xFF

        # Wave RAM is always writable
        if 0xFF30 <= address <= 0xFF3F:
            self._ch3.write_wave_ram(address, value)
            return

        # NR52: only bit 7 (power) is writable
        if address == 0xFF26:
            new_power = bool(value & 0x80)
            if self._power and not new_power:
                self._power_off()
            elif not self._power and new_power:
                self._fs_step = 0
                self._fs_counter = 0
            self._power = new_power
            return

        # When powered off, writes to all registers except NR52 are ignored
        if not self._power:
            return

        # Master control registers
        if address == 0xFF24:
            self._nr50 = value
            return
        if address == 0xFF25:
            self._nr51 = value
            return

        # Channel registers
        self._write_channel_register(address, value)

    def _write_channel_register(self, address, value):
        """Route a register write to the appropriate channel."""
        if 0xFF10 <= address <= 0xFF14:
            self._ch1.write(address - 0xFF10, value)
        elif 0xFF16 <= address <= 0xFF19:
            self._ch2.write(address - 0xFF15, value)
        elif 0xFF1A <= address <= 0xFF1E:
            self._ch3.write(address - 0xFF1A, value)
        elif 0xFF20 <= address <= 0xFF23:
            self._ch4.write(address - 0xFF20, value)

    def _power_off(self):
        """Zero all registers and disable all channels."""
        self._ch1.power_off()
        self._ch2.power_off()
        self._ch3.power_off()  # Wave RAM preserved inside
        self._ch4.power_off()
        self._nr50 = 0
        self._nr51 = 0

    def drain_samples(self):
        """Return pending samples and clear the buffer.

        Returns a list of (left, right) float tuples.
        Called by the frontend to get audio data.
        """
        samples = self._sample_buffer
        self._sample_buffer = []
        return samples
