import unittest

from src.apu.noise_channel import NoiseChannel


class TestNoiseChannelRegisters(unittest.TestCase):
    """Test register read/write behavior for the noise channel."""

    def setUp(self):
        self.ch = NoiseChannel()

    def test_default_register_values(self):
        for i in range(4):
            self.assertEqual(self.ch.read(i), 0)

    def test_nr41_length_load(self):
        self.ch.write(0, 0x20)  # length_load=32
        self.assertEqual(self.ch._length_counter, 32)  # 64 - 32

    def test_nr41_length_max(self):
        self.ch.write(0, 0x00)  # length_load=0
        self.assertEqual(self.ch._length_counter, 64)

    def test_nr42_envelope(self):
        self.ch.write(1, 0xF3)  # vol=15, decrease, pace=3
        self.assertEqual(self.ch.read(1), 0xF3)

    def test_nr42_dac_enable(self):
        self.ch.write(1, 0xF0)
        self.assertTrue(self.ch._dac_enabled)
        self.ch.write(1, 0x08)  # vol=0, increase
        self.assertTrue(self.ch._dac_enabled)
        self.ch.write(1, 0x00)  # DAC off
        self.assertFalse(self.ch._dac_enabled)

    def test_nr42_dac_off_disables(self):
        self.ch.write(1, 0xF0)
        self.ch.write(3, 0x80)  # trigger
        self.assertTrue(self.ch._enabled)
        self.ch.write(1, 0x00)  # DAC off
        self.assertFalse(self.ch._enabled)

    def test_nr43_fields(self):
        self.ch.write(2, 0xB5)  # shift=11, width=0, divisor=5
        self.assertEqual(self.ch._clock_shift, 11)
        self.assertFalse(self.ch._width_mode)
        self.assertEqual(self.ch._divisor_code, 5)

    def test_nr43_width_mode(self):
        self.ch.write(2, 0x08)  # width mode = 1
        self.assertTrue(self.ch._width_mode)

    def test_nr44_length_enable(self):
        self.ch.write(3, 0x40)
        self.assertTrue(self.ch._length_enabled)

    def test_nr44_trigger(self):
        self.ch.write(1, 0xF0)  # DAC on
        self.ch.write(3, 0x80)  # trigger
        self.assertTrue(self.ch._enabled)


class TestNoiseChannelLFSR(unittest.TestCase):
    """Test LFSR behavior."""

    def setUp(self):
        self.ch = NoiseChannel()
        self.ch.write(1, 0xF0)  # DAC on, vol=15

    def test_lfsr_initialized_on_trigger(self):
        self.ch.write(3, 0x80)  # trigger
        self.assertEqual(self.ch._lfsr, 0x7FFF)

    def test_lfsr_15bit_produces_sequence(self):
        """LFSR should produce a pseudo-random sequence."""
        self.ch.write(2, 0x00)  # shift=0, 15-bit, divisor=0
        self.ch.write(3, 0x80)  # trigger
        values = set()
        for _ in range(100):
            self.ch._freq_timer = 1  # Force immediate clock
            self.ch.tick(1)
            values.add(self.ch._lfsr)
        self.assertGreater(len(values), 10)  # Should produce many unique values

    def test_lfsr_7bit_shorter_sequence(self):
        """7-bit mode should produce a shorter repeating sequence."""
        self.ch.write(2, 0x08)  # width mode = 1
        self.ch.write(3, 0x80)  # trigger
        values = []
        for _ in range(200):
            self.ch._freq_timer = 1
            self.ch.tick(1)
            values.append(self.ch._lfsr)
        # 7-bit LFSR max period is 127
        # Check for repetition within 200 steps
        unique = set(values)
        self.assertLessEqual(len(unique), 127)

    def test_lfsr_xor_operation(self):
        """Verify XOR of bits 0 and 1, placed in bit 14."""
        self.ch.write(2, 0x00)
        self.ch.write(3, 0x80)  # trigger -> lfsr = 0x7FFF
        # All bits are 1: bit0=1, bit1=1 -> xor=0
        # After shift right: bit 14 = 0
        self.ch._freq_timer = 1
        self.ch.tick(1)
        self.assertEqual((self.ch._lfsr >> 14) & 1, 0)

    def test_lfsr_7bit_sets_bit6(self):
        """In 7-bit mode, XOR result also written to bit 6."""
        self.ch.write(2, 0x08)  # width mode
        self.ch.write(3, 0x80)  # trigger -> lfsr = 0x7FFF
        # bit0=1, bit1=1 -> xor=0
        self.ch._freq_timer = 1
        self.ch.tick(1)
        self.assertEqual((self.ch._lfsr >> 6) & 1, 0)

    def test_output_inverts_bit0(self):
        """Output should be inverted bit 0 * volume."""
        self.ch.write(2, 0x00)
        self.ch.write(3, 0x80)  # trigger
        # LFSR = 0x7FFF, bit 0 = 1, inverted = 0
        self.assertEqual(self.ch.get_output(), 0)
        # Clock once to change LFSR
        self.ch._freq_timer = 1
        self.ch.tick(1)
        # After first clock, bit0 and bit1 were both 1, xor=0
        # LFSR shifted right, bit14=0, bit0 is now what was bit1 = 1
        # So inverted bit0 = 0, output = 0
        # Let's just verify the formula works
        expected = (~self.ch._lfsr & 1) * self.ch._volume
        self.assertEqual(self.ch.get_output(), expected)


class TestNoiseChannelDivisorTable(unittest.TestCase):
    """Test the divisor table and timer period calculation."""

    def test_all_divisor_codes(self):
        ch = NoiseChannel()
        expected = [8, 16, 32, 48, 64, 80, 96, 112]
        for code in range(8):
            self.assertEqual(ch.DIVISOR_TABLE[code], expected[code])

    def test_timer_period_calculation(self):
        ch = NoiseChannel()
        ch.write(1, 0xF0)  # DAC on
        # Divisor code 0, shift 0: period = 8 << 0 = 8
        ch.write(2, 0x00)
        ch.write(3, 0x80)  # trigger
        self.assertEqual(ch._freq_timer, 8)

    def test_timer_period_with_shift(self):
        ch = NoiseChannel()
        ch.write(1, 0xF0)
        # Divisor code 2 (32), shift 3: period = 32 << 3 = 256
        ch.write(2, 0x32)  # shift=3, divisor=2
        ch.write(3, 0x80)
        self.assertEqual(ch._freq_timer, 256)


class TestNoiseChannelLengthCounter(unittest.TestCase):
    """Test length counter behavior."""

    def setUp(self):
        self.ch = NoiseChannel()
        self.ch.write(1, 0xF0)  # DAC on

    def test_length_countdown(self):
        self.ch.write(0, 0x3E)  # length_load=62, counter=2
        self.ch.write(3, 0xC0)  # trigger, length_enable=True
        self.ch.clock_length()
        self.assertEqual(self.ch._length_counter, 1)
        self.ch.clock_length()
        self.assertFalse(self.ch._enabled)

    def test_length_disabled(self):
        self.ch.write(0, 0x3E)  # counter=2
        self.ch.write(3, 0x80)  # trigger, length_enable=False
        self.ch.clock_length()
        self.ch.clock_length()
        self.assertTrue(self.ch._enabled)

    def test_trigger_reloads_length(self):
        self.ch._length_counter = 0
        self.ch.write(3, 0x80)  # trigger
        self.assertEqual(self.ch._length_counter, 64)


class TestNoiseChannelEnvelope(unittest.TestCase):
    """Test volume envelope behavior."""

    def setUp(self):
        self.ch = NoiseChannel()

    def test_envelope_decrease(self):
        self.ch.write(1, 0xF1)  # vol=15, decrease, pace=1
        self.ch.write(3, 0x80)  # trigger
        self.ch.clock_envelope()
        self.assertEqual(self.ch._volume, 14)

    def test_envelope_increase(self):
        self.ch.write(1, 0x09)  # vol=0, increase, pace=1
        self.ch.write(3, 0x80)
        self.ch.clock_envelope()
        self.assertEqual(self.ch._volume, 1)

    def test_envelope_pace_zero(self):
        self.ch.write(1, 0xF0)  # vol=15, decrease, pace=0
        self.ch.write(3, 0x80)
        self.ch.clock_envelope()
        self.assertEqual(self.ch._volume, 15)  # No change


class TestNoiseChannelTrigger(unittest.TestCase):
    """Test trigger event behavior."""

    def test_trigger_resets_lfsr(self):
        ch = NoiseChannel()
        ch.write(1, 0xF0)
        ch.write(2, 0x00)
        ch.write(3, 0x80)  # trigger
        ch.tick(100)  # Mutate LFSR
        self.assertNotEqual(ch._lfsr, 0x7FFF)
        ch.write(3, 0x80)  # re-trigger
        self.assertEqual(ch._lfsr, 0x7FFF)

    def test_trigger_reloads_envelope(self):
        ch = NoiseChannel()
        ch.write(1, 0xA3)  # vol=10, decrease, pace=3
        ch.write(3, 0x80)
        self.assertEqual(ch._volume, 10)

    def test_trigger_with_dac_off(self):
        ch = NoiseChannel()
        ch.write(1, 0x00)  # DAC off
        ch.write(3, 0x80)
        self.assertFalse(ch._enabled)


class TestNoiseChannelPowerOff(unittest.TestCase):
    """Test power off behavior."""

    def test_power_off_resets_state(self):
        ch = NoiseChannel()
        ch.write(1, 0xF0)
        ch.write(3, 0x80)
        self.assertTrue(ch._enabled)
        ch.power_off()
        self.assertFalse(ch._enabled)
        self.assertFalse(ch._dac_enabled)
        for i in range(4):
            self.assertEqual(ch.read(i), 0)

    def test_power_off_resets_lfsr(self):
        ch = NoiseChannel()
        ch.write(1, 0xF0)
        ch.write(2, 0x00)
        ch.write(3, 0x80)
        ch.tick(50)
        ch.power_off()
        self.assertEqual(ch._lfsr, 0x7FFF)


class TestNoiseChannelIsActive(unittest.TestCase):
    """Test is_active() method."""

    def test_active(self):
        ch = NoiseChannel()
        ch.write(1, 0xF0)
        ch.write(3, 0x80)
        self.assertTrue(ch.is_active())

    def test_inactive_no_trigger(self):
        ch = NoiseChannel()
        ch.write(1, 0xF0)
        self.assertFalse(ch.is_active())

    def test_inactive_dac_off(self):
        ch = NoiseChannel()
        ch.write(1, 0x00)
        self.assertFalse(ch.is_active())


if __name__ == '__main__':
    unittest.main()
