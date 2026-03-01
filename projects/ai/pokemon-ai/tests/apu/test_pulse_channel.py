import unittest

from src.apu.pulse_channel import PulseChannel


class TestPulseChannelRegisters(unittest.TestCase):
    """Test register read/write behavior for the pulse channel."""

    def setUp(self):
        self.ch = PulseChannel(has_sweep=True)

    def test_default_register_values(self):
        for i in range(5):
            self.assertEqual(self.ch.read(i), 0)

    def test_write_read_nrx0_sweep(self):
        self.ch.write(0, 0x67)  # pace=6, sub, step=7
        self.assertEqual(self.ch.read(0), 0x67)

    def test_write_read_nrx1_duty_length(self):
        self.ch.write(1, 0xC0)  # duty=3, length_load=0
        self.assertEqual(self.ch.read(1), 0xC0)
        self.assertEqual(self.ch._length_counter, 64)

    def test_nrx1_length_counter_load(self):
        self.ch.write(1, 0x20)  # length_load=32
        self.assertEqual(self.ch._length_counter, 32)  # 64 - 32

    def test_write_read_nrx2_envelope(self):
        self.ch.write(2, 0xF3)  # vol=15, dec, pace=3
        self.assertEqual(self.ch.read(2), 0xF3)

    def test_nrx2_dac_enable(self):
        self.ch.write(2, 0xF0)  # vol=15, direction=0, pace=0
        self.assertTrue(self.ch._dac_enabled)
        self.ch.write(2, 0x08)  # vol=0, direction=1 (increase), pace=0
        self.assertTrue(self.ch._dac_enabled)
        self.ch.write(2, 0x00)  # vol=0, direction=0 -> DAC off
        self.assertFalse(self.ch._dac_enabled)

    def test_nrx2_dac_off_disables_channel(self):
        # Enable channel first
        self.ch.write(2, 0xF0)
        self.ch.write(4, 0x80)  # trigger
        self.assertTrue(self.ch._enabled)
        # Turn DAC off
        self.ch.write(2, 0x00)
        self.assertFalse(self.ch._enabled)

    def test_nrx3_period_low(self):
        self.ch.write(3, 0xAB)
        self.assertEqual(self.ch._period & 0xFF, 0xAB)

    def test_nrx4_period_high(self):
        self.ch.write(3, 0xFF)
        self.ch.write(4, 0x07)  # period high = 7
        self.assertEqual(self.ch._period, 0x7FF)

    def test_nrx4_length_enable(self):
        self.ch.write(4, 0x40)
        self.assertTrue(self.ch._length_enabled)

    def test_nrx4_trigger_enables_channel(self):
        self.ch.write(2, 0xF0)  # DAC on
        self.ch.write(4, 0x80)  # trigger
        self.assertTrue(self.ch._enabled)

    def test_nrx4_trigger_with_dac_off(self):
        self.ch.write(2, 0x00)  # DAC off
        self.ch.write(4, 0x80)  # trigger
        self.assertFalse(self.ch._enabled)


class TestPulseChannelFrequencyTimer(unittest.TestCase):
    """Test frequency timer and duty cycle stepping."""

    def setUp(self):
        self.ch = PulseChannel(has_sweep=False)
        # Enable channel with a fast period
        self.ch.write(2, 0xF0)  # DAC on, vol=15

    def test_duty_pos_advances(self):
        # Period = 2047: timer period = (2048-2047)*4 = 4 T-cycles per step
        self.ch.write(3, 0xFF)
        self.ch.write(4, 0x87)  # trigger, period_high=7
        initial_pos = self.ch._duty_pos
        self.ch.tick(4)  # One timer period
        self.assertEqual(self.ch._duty_pos, (initial_pos + 1) & 7)

    def test_duty_pos_wraps(self):
        self.ch.write(3, 0xFF)
        self.ch.write(4, 0x87)  # trigger, period=2047
        self.ch.tick(4 * 8)  # 8 steps = full cycle
        # Should be back to where we started (trigger reloads timer,
        # first tick completes it)

    def test_slow_period(self):
        # Period = 0: timer period = 2048*4 = 8192 T-cycles
        self.ch.write(3, 0x00)
        self.ch.write(4, 0x80)  # trigger, period=0
        initial_pos = self.ch._duty_pos
        self.ch.tick(8191)  # One short of timer period
        self.assertEqual(self.ch._duty_pos, initial_pos)
        self.ch.tick(1)  # Completes the timer period
        self.assertEqual(self.ch._duty_pos, (initial_pos + 1) & 7)

    def test_disabled_channel_no_tick(self):
        self.ch.write(3, 0xFF)
        self.ch.write(4, 0x87)  # trigger
        self.ch._enabled = False
        initial_pos = self.ch._duty_pos
        self.ch.tick(100)
        self.assertEqual(self.ch._duty_pos, initial_pos)


class TestPulseChannelDutyOutput(unittest.TestCase):
    """Test duty cycle waveform output."""

    def setUp(self):
        self.ch = PulseChannel(has_sweep=False)

    def _setup_channel(self, duty, volume=15):
        self.ch.write(1, duty << 6)
        self.ch.write(2, (volume << 4) | 0x08)  # vol, increase
        self.ch.write(3, 0xFF)
        self.ch.write(4, 0x87)  # trigger, period=2047

    def test_duty_0_pattern(self):
        """12.5% duty: only position 7 is high."""
        self._setup_channel(0)
        outputs = []
        for _ in range(8):
            outputs.append(self.ch.get_output())
            self.ch.tick(4)
        high_count = sum(1 for o in outputs if o > 0)
        self.assertEqual(high_count, 1)  # 1/8 = 12.5%

    def test_duty_1_pattern(self):
        """25% duty: positions 0 and 7 are high."""
        self._setup_channel(1)
        outputs = []
        for _ in range(8):
            outputs.append(self.ch.get_output())
            self.ch.tick(4)
        high_count = sum(1 for o in outputs if o > 0)
        self.assertEqual(high_count, 2)  # 2/8 = 25%

    def test_duty_2_pattern(self):
        """50% duty: 4 high positions."""
        self._setup_channel(2)
        outputs = []
        for _ in range(8):
            outputs.append(self.ch.get_output())
            self.ch.tick(4)
        high_count = sum(1 for o in outputs if o > 0)
        self.assertEqual(high_count, 4)  # 4/8 = 50%

    def test_duty_3_pattern(self):
        """75% duty: 6 high positions."""
        self._setup_channel(3)
        outputs = []
        for _ in range(8):
            outputs.append(self.ch.get_output())
            self.ch.tick(4)
        high_count = sum(1 for o in outputs if o > 0)
        self.assertEqual(high_count, 6)  # 6/8 = 75%

    def test_output_scales_with_volume(self):
        self._setup_channel(2, volume=8)
        # Find a high position
        for _ in range(8):
            out = self.ch.get_output()
            if out > 0:
                self.assertEqual(out, 8)
                return
            self.ch.tick(4)
        self.fail("No high output found")

    def test_output_zero_when_disabled(self):
        self._setup_channel(2)
        self.ch._enabled = False
        self.assertEqual(self.ch.get_output(), 0)

    def test_output_zero_when_dac_off(self):
        self._setup_channel(2)
        self.ch.write(2, 0x00)  # DAC off
        self.assertEqual(self.ch.get_output(), 0)


class TestPulseChannelLengthCounter(unittest.TestCase):
    """Test length counter behavior."""

    def setUp(self):
        self.ch = PulseChannel(has_sweep=False)
        self.ch.write(2, 0xF0)  # DAC on

    def test_length_countdown(self):
        self.ch.write(1, 0x3E)  # length_load=62, counter=2
        self.ch.write(4, 0xC0)  # trigger, length_enable=True
        self.assertTrue(self.ch._enabled)
        self.ch.clock_length()
        self.assertTrue(self.ch._enabled)
        self.assertEqual(self.ch._length_counter, 1)
        self.ch.clock_length()
        self.assertFalse(self.ch._enabled)

    def test_length_disabled_no_countdown(self):
        self.ch.write(1, 0x3E)  # counter=2
        self.ch.write(4, 0x80)  # trigger, length_enable=False
        self.ch.clock_length()
        self.ch.clock_length()
        self.assertTrue(self.ch._enabled)

    def test_trigger_reloads_length_when_zero(self):
        self.ch.write(1, 0x00)  # length_load=0, counter=64
        self.ch.write(4, 0x80)  # trigger
        self.assertEqual(self.ch._length_counter, 64)

    def test_trigger_keeps_length_when_nonzero(self):
        self.ch.write(1, 0x3E)  # counter=2
        self.ch.write(4, 0x80)  # trigger
        self.assertEqual(self.ch._length_counter, 2)


class TestPulseChannelEnvelope(unittest.TestCase):
    """Test volume envelope behavior."""

    def setUp(self):
        self.ch = PulseChannel(has_sweep=False)

    def test_envelope_decrease(self):
        self.ch.write(2, 0xF1)  # vol=15, decrease, pace=1
        self.ch.write(4, 0x80)  # trigger
        self.assertEqual(self.ch._volume, 15)
        self.ch.clock_envelope()
        self.assertEqual(self.ch._volume, 14)

    def test_envelope_increase(self):
        self.ch.write(2, 0x09)  # vol=0, increase, pace=1
        self.ch.write(4, 0x80)  # trigger
        self.assertEqual(self.ch._volume, 0)
        self.ch.clock_envelope()
        self.assertEqual(self.ch._volume, 1)

    def test_envelope_clamp_at_zero(self):
        self.ch.write(2, 0x11)  # vol=1, decrease, pace=1
        self.ch.write(4, 0x80)  # trigger
        self.ch.clock_envelope()
        self.assertEqual(self.ch._volume, 0)
        self.ch.clock_envelope()
        self.assertEqual(self.ch._volume, 0)  # Stays at 0

    def test_envelope_clamp_at_fifteen(self):
        self.ch.write(2, 0xE9)  # vol=14, increase, pace=1
        self.ch.write(4, 0x80)  # trigger
        self.ch.clock_envelope()
        self.assertEqual(self.ch._volume, 15)
        self.ch.clock_envelope()
        self.assertEqual(self.ch._volume, 15)  # Stays at 15

    def test_envelope_pace_zero_disabled(self):
        self.ch.write(2, 0xF0)  # vol=15, decrease, pace=0
        self.ch.write(4, 0x80)  # trigger
        self.ch.clock_envelope()
        self.assertEqual(self.ch._volume, 15)  # No change

    def test_envelope_pace_timing(self):
        self.ch.write(2, 0xF3)  # vol=15, decrease, pace=3
        self.ch.write(4, 0x80)  # trigger
        self.ch.clock_envelope()  # Timer: 3->2
        self.assertEqual(self.ch._volume, 15)
        self.ch.clock_envelope()  # Timer: 2->1
        self.assertEqual(self.ch._volume, 15)
        self.ch.clock_envelope()  # Timer: 1->0, fires, reload to 3
        self.assertEqual(self.ch._volume, 14)


class TestPulseChannelSweep(unittest.TestCase):
    """Test CH1 sweep behavior."""

    def setUp(self):
        self.ch = PulseChannel(has_sweep=True)
        self.ch.write(2, 0xF0)  # DAC on

    def test_sweep_increases_frequency(self):
        self.ch.write(0, 0x11)  # pace=1, addition, step=1
        self.ch.write(3, 0x00)
        self.ch.write(4, 0x82)  # trigger, period_high=2 -> period=512
        self.assertEqual(self.ch._sweep_shadow, 512)
        self.ch.clock_sweep()  # Timer fires: 512 + 512>>1 = 768
        self.assertEqual(self.ch._period, 768)

    def test_sweep_decreases_frequency(self):
        self.ch.write(0, 0x19)  # pace=1, subtraction, step=1
        self.ch.write(3, 0x00)
        self.ch.write(4, 0x82)  # trigger, period=512
        self.ch.clock_sweep()  # 512 - 512>>1 = 256
        self.assertEqual(self.ch._period, 256)

    def test_sweep_overflow_disables_channel(self):
        self.ch.write(0, 0x11)  # pace=1, addition, step=1
        self.ch.write(3, 0x00)
        self.ch.write(4, 0x86)  # trigger, period=0x600=1536
        # 1536 + 768 = 2304 > 2047 -> disable
        self.ch.clock_sweep()
        self.assertFalse(self.ch._enabled)

    def test_sweep_step_zero_no_write(self):
        self.ch.write(0, 0x10)  # pace=1, addition, step=0
        self.ch.write(3, 0x00)
        self.ch.write(4, 0x82)  # trigger, period=512
        original = self.ch._period
        self.ch.clock_sweep()
        self.assertEqual(self.ch._period, original)

    def test_sweep_pace_zero_no_update(self):
        self.ch.write(0, 0x01)  # pace=0, addition, step=1
        self.ch.write(3, 0x00)
        self.ch.write(4, 0x82)  # trigger, period=512
        original = self.ch._period
        self.ch.clock_sweep()
        self.assertEqual(self.ch._period, original)

    def test_sweep_trigger_overflow_check(self):
        """On trigger with step!=0, overflow check is performed immediately."""
        self.ch.write(0, 0x11)  # pace=1, addition, step=1
        self.ch.write(3, 0xFF)
        self.ch.write(4, 0x87)  # trigger, period=2047
        # 2047 + 2047>>1 = 3070 > 2047 -> disabled on trigger
        self.assertFalse(self.ch._enabled)

    def test_no_sweep_on_ch2(self):
        ch2 = PulseChannel(has_sweep=False)
        ch2.write(2, 0xF0)  # DAC on
        ch2.write(3, 0x00)
        ch2.write(4, 0x82)  # trigger, period=512
        original = ch2._period
        ch2.clock_sweep()  # Should do nothing
        self.assertEqual(ch2._period, original)

    def test_sweep_negate_then_add_disables(self):
        """Using subtraction then switching to addition disables channel."""
        self.ch.write(0, 0x19)  # pace=1, subtraction, step=1
        self.ch.write(3, 0x00)
        self.ch.write(4, 0x82)  # trigger, period=512
        self.ch.clock_sweep()  # Uses subtraction, sets negate_used
        self.assertTrue(self.ch._enabled)
        # Switch to addition mode
        self.ch.write(0, 0x11)  # pace=1, addition, step=1
        self.assertFalse(self.ch._enabled)


class TestPulseChannelTrigger(unittest.TestCase):
    """Test trigger event behavior."""

    def setUp(self):
        self.ch = PulseChannel(has_sweep=True)

    def test_trigger_reloads_envelope(self):
        self.ch.write(2, 0xA3)  # vol=10, decrease, pace=3
        self.ch.write(4, 0x80)  # trigger
        self.assertEqual(self.ch._volume, 10)
        self.assertEqual(self.ch._env_pace, 3)

    def test_trigger_reloads_freq_timer(self):
        self.ch.write(2, 0xF0)  # DAC on
        self.ch.write(3, 0x00)
        self.ch.write(4, 0x82)  # trigger, period=512
        self.assertEqual(self.ch._freq_timer, (2048 - 512) * 4)

    def test_trigger_sweep_setup(self):
        self.ch.write(0, 0x23)  # pace=2, addition, step=3
        self.ch.write(2, 0xF0)  # DAC on
        self.ch.write(3, 0x00)
        self.ch.write(4, 0x84)  # trigger, period=1024
        self.assertEqual(self.ch._sweep_shadow, 1024)
        self.assertTrue(self.ch._sweep_enabled)
        self.assertEqual(self.ch._sweep_pace, 2)
        self.assertEqual(self.ch._sweep_step, 3)


class TestPulseChannelPowerOff(unittest.TestCase):
    """Test power off behavior."""

    def test_power_off_resets_state(self):
        ch = PulseChannel(has_sweep=True)
        ch.write(2, 0xF0)
        ch.write(4, 0x80)  # trigger
        self.assertTrue(ch._enabled)
        ch.power_off()
        self.assertFalse(ch._enabled)
        self.assertFalse(ch._dac_enabled)
        for i in range(5):
            self.assertEqual(ch.read(i), 0)

    def test_power_off_resets_sweep(self):
        ch = PulseChannel(has_sweep=True)
        ch.write(0, 0x23)
        ch.write(2, 0xF0)
        ch.write(4, 0x80)
        ch.power_off()
        self.assertFalse(ch._sweep_enabled)
        self.assertEqual(ch._sweep_shadow, 0)


class TestPulseChannelIsActive(unittest.TestCase):
    """Test is_active() method."""

    def test_active_when_enabled_and_dac_on(self):
        ch = PulseChannel(has_sweep=False)
        ch.write(2, 0xF0)
        ch.write(4, 0x80)
        self.assertTrue(ch.is_active())

    def test_inactive_when_disabled(self):
        ch = PulseChannel(has_sweep=False)
        ch.write(2, 0xF0)
        self.assertFalse(ch.is_active())

    def test_inactive_when_dac_off(self):
        ch = PulseChannel(has_sweep=False)
        ch.write(2, 0x00)
        self.assertFalse(ch.is_active())


if __name__ == '__main__':
    unittest.main()
