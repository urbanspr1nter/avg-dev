from src.apu.pulse_channel import PulseChannel
from src.apu.wave_channel import WaveChannel
from src.apu.noise_channel import NoiseChannel

_NOISE_DIVISOR_TABLE = NoiseChannel.DIVISOR_TABLE


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
        # Cache class constants as instance attrs for faster access
        self._sample_period = self.SAMPLE_PERIOD

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

        fs_counter = self._fs_counter + cycles
        sample_counter = self._sample_counter + cycles

        # Fast path: no event boundary within this batch
        if fs_counter < 8192 and sample_counter < self._sample_period:
            self._fs_counter = fs_counter
            self._sample_counter = sample_counter
            # Inline channel ticks to avoid 4 method calls
            ch1 = self._ch1
            if ch1._enabled:
                ch1._freq_timer -= cycles
                if ch1._freq_timer <= 0:
                    while ch1._freq_timer <= 0:
                        ch1._freq_timer += (2048 - ch1._period) * 4
                        ch1._duty_pos = (ch1._duty_pos + 1) & 7
            ch2 = self._ch2
            if ch2._enabled:
                ch2._freq_timer -= cycles
                if ch2._freq_timer <= 0:
                    while ch2._freq_timer <= 0:
                        ch2._freq_timer += (2048 - ch2._period) * 4
                        ch2._duty_pos = (ch2._duty_pos + 1) & 7
            ch3 = self._ch3
            if ch3._enabled:
                ch3._freq_timer -= cycles
                if ch3._freq_timer <= 0:
                    while ch3._freq_timer <= 0:
                        ch3._freq_timer += (2048 - ch3._period) * 2
                        ch3._wave_pos = (ch3._wave_pos + 1) & 31
                        byte_idx = ch3._wave_pos >> 1
                        if ch3._wave_pos & 1:
                            ch3._sample_buffer = ch3._wave_ram[byte_idx] & 0x0F
                        else:
                            ch3._sample_buffer = (ch3._wave_ram[byte_idx] >> 4) & 0x0F
            ch4 = self._ch4
            if ch4._enabled:
                ch4._freq_timer -= cycles
                if ch4._freq_timer <= 0:
                    while ch4._freq_timer <= 0:
                        divisor = _NOISE_DIVISOR_TABLE[ch4._divisor_code]
                        period = divisor << ch4._clock_shift
                        ch4._freq_timer += period if period else 1
                        xor_bit = (ch4._lfsr & 1) ^ ((ch4._lfsr >> 1) & 1)
                        ch4._lfsr = (ch4._lfsr >> 1) | (xor_bit << 14)
                        if ch4._width_mode:
                            ch4._lfsr = (ch4._lfsr & ~0x40) | (xor_bit << 6)
            return

        # Slow path: event boundary crossed
        sample_period = self._sample_period
        remaining = cycles
        while remaining > 0:
            cycles_to_fs = 8192 - self._fs_counter
            cycles_to_sample = int(sample_period - self._sample_counter) + 1
            step = min(remaining, cycles_to_fs, cycles_to_sample)

            self._fs_counter += step
            self._sample_counter += step
            remaining -= step

            self._ch1.tick(step)
            self._ch2.tick(step)
            self._ch3.tick(step)
            self._ch4.tick(step)

            if self._fs_counter >= 8192:
                self._fs_counter = 0
                self._clock_frame_sequencer()

            if self._sample_counter >= sample_period:
                self._sample_counter -= sample_period
                self._sample_buffer.append(self._mix_channels())

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
        # Get DAC outputs inline (avoid list creation + loop)
        ch1 = self._ch1
        d1 = (ch1.get_output() / 7.5) - 1.0 if ch1._dac_enabled else 0.0
        ch2 = self._ch2
        d2 = (ch2.get_output() / 7.5) - 1.0 if ch2._dac_enabled else 0.0
        ch3 = self._ch3
        d3 = (ch3.get_output() / 7.5) - 1.0 if ch3._dac_enabled else 0.0
        ch4 = self._ch4
        d4 = (ch4.get_output() / 7.5) - 1.0 if ch4._dac_enabled else 0.0

        nr51 = self._nr51
        left = 0.0
        right = 0.0

        # NR51 panning: bits 4-7 = left, bits 0-3 = right
        if nr51 & 0x10: left += d1
        if nr51 & 0x01: right += d1
        if nr51 & 0x20: left += d2
        if nr51 & 0x02: right += d2
        if nr51 & 0x40: left += d3
        if nr51 & 0x04: right += d3
        if nr51 & 0x80: left += d4
        if nr51 & 0x08: right += d4

        # Normalize and apply master volume from NR50
        nr50 = self._nr50
        left *= (((nr50 >> 4) & 0x07) + 1) / 32.0
        right *= ((nr50 & 0x07) + 1) / 32.0

        # Inline high-pass filter (avoid 2 method calls)
        charge = self._hpf_charge_factor
        cap_l = self._hpf_capacitor_left
        out_l = left - cap_l
        self._hpf_capacitor_left = left - out_l * charge

        cap_r = self._hpf_capacitor_right
        out_r = right - cap_r
        self._hpf_capacitor_right = right - out_r * charge

        return (out_l, out_r)

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

    def save_state(self):
        return {
            'ch1': self._ch1.save_state(),
            'ch2': self._ch2.save_state(),
            'ch3': self._ch3.save_state(),
            'ch4': self._ch4.save_state(),
            'nr50': self._nr50,
            'nr51': self._nr51,
            'power': self._power,
            'fs_counter': self._fs_counter,
            'fs_step': self._fs_step,
            'sample_counter': self._sample_counter,
            'hpf_capacitor_left': self._hpf_capacitor_left,
            'hpf_capacitor_right': self._hpf_capacitor_right,
        }

    def load_state(self, state):
        self._ch1.load_state(state['ch1'])
        self._ch2.load_state(state['ch2'])
        self._ch3.load_state(state['ch3'])
        self._ch4.load_state(state['ch4'])
        self._nr50 = state['nr50']
        self._nr51 = state['nr51']
        self._power = state['power']
        self._fs_counter = state['fs_counter']
        self._fs_step = state['fs_step']
        self._sample_counter = state['sample_counter']
        self._hpf_capacitor_left = state['hpf_capacitor_left']
        self._hpf_capacitor_right = state['hpf_capacitor_right']
        self._sample_buffer = []

    def drain_samples(self):
        """Return pending samples and clear the buffer.

        Returns a list of (left, right) float tuples.
        Called by the frontend to get audio data.
        """
        samples = self._sample_buffer
        self._sample_buffer = []
        return samples
