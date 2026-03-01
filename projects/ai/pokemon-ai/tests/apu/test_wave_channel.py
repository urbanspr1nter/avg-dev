import unittest

from src.apu.wave_channel import WaveChannel


class TestWaveChannelRegisters(unittest.TestCase):
    """Test register read/write behavior for the wave channel."""

    def setUp(self):
        self.ch = WaveChannel()

    def test_default_register_values(self):
        for i in range(5):
            self.assertEqual(self.ch.read(i), 0)

    def test_nr30_dac_enable(self):
        self.ch.write(0, 0x80)
        self.assertTrue(self.ch._dac_enabled)
        self.ch.write(0, 0x00)
        self.assertFalse(self.ch._dac_enabled)

    def test_nr30_dac_off_disables_channel(self):
        self.ch.write(0, 0x80)  # DAC on
        self.ch.write(4, 0x80)  # trigger
        self.assertTrue(self.ch._enabled)
        self.ch.write(0, 0x00)  # DAC off
        self.assertFalse(self.ch._enabled)

    def test_nr31_length_load(self):
        self.ch.write(1, 100)
        self.assertEqual(self.ch._length_counter, 156)  # 256 - 100

    def test_nr31_length_load_max(self):
        self.ch.write(1, 0)
        self.assertEqual(self.ch._length_counter, 256)

    def test_nr32_volume_code(self):
        self.ch.write(2, 0x60)  # volume code = 3
        self.assertEqual((self.ch._nr32 >> 5) & 0x03, 3)

    def test_nr33_period_low(self):
        self.ch.write(3, 0xAB)
        self.assertEqual(self.ch._period & 0xFF, 0xAB)

    def test_nr34_period_high(self):
        self.ch.write(3, 0xFF)
        self.ch.write(4, 0x07)
        self.assertEqual(self.ch._period, 0x7FF)

    def test_nr34_length_enable(self):
        self.ch.write(4, 0x40)
        self.assertTrue(self.ch._length_enabled)

    def test_nr34_trigger(self):
        self.ch.write(0, 0x80)  # DAC on
        self.ch.write(4, 0x80)  # trigger
        self.assertTrue(self.ch._enabled)

    def test_trigger_with_dac_off(self):
        self.ch.write(0, 0x00)  # DAC off
        self.ch.write(4, 0x80)  # trigger
        self.assertFalse(self.ch._enabled)


class TestWaveRAM(unittest.TestCase):
    """Test wave RAM read/write behavior."""

    def setUp(self):
        self.ch = WaveChannel()

    def test_default_wave_ram_zero(self):
        for addr in range(0xFF30, 0xFF40):
            self.assertEqual(self.ch.read_wave_ram(addr), 0)

    def test_write_read_wave_ram(self):
        for i, addr in enumerate(range(0xFF30, 0xFF40)):
            self.ch.write_wave_ram(addr, i * 17)  # Various values
        for i, addr in enumerate(range(0xFF30, 0xFF40)):
            self.assertEqual(self.ch.read_wave_ram(addr), (i * 17) & 0xFF)

    def test_wave_ram_all_bytes(self):
        for addr in range(0xFF30, 0xFF40):
            self.ch.write_wave_ram(addr, 0xAB)
            self.assertEqual(self.ch.read_wave_ram(addr), 0xAB)

    def test_wave_ram_survives_power_off(self):
        for addr in range(0xFF30, 0xFF40):
            self.ch.write_wave_ram(addr, 0x42)
        self.ch.power_off()
        for addr in range(0xFF30, 0xFF40):
            self.assertEqual(self.ch.read_wave_ram(addr), 0x42)


class TestWaveChannelFrequencyTimer(unittest.TestCase):
    """Test frequency timer and wave position stepping."""

    def setUp(self):
        self.ch = WaveChannel()
        self.ch.write(0, 0x80)  # DAC on
        # Write a recognizable pattern to wave RAM
        # Each byte has upper nibble and lower nibble
        for i in range(16):
            self.ch.write_wave_ram(0xFF30 + i, (i << 4) | i)

    def test_wave_pos_advances(self):
        # Period = 2047: timer period = (2048-2047)*2 = 2 T-cycles
        self.ch.write(3, 0xFF)
        self.ch.write(4, 0x87)  # trigger, period=2047
        self.assertEqual(self.ch._wave_pos, 0)
        self.ch.tick(2)
        self.assertEqual(self.ch._wave_pos, 1)

    def test_wave_pos_wraps_at_32(self):
        self.ch.write(3, 0xFF)
        self.ch.write(4, 0x87)  # trigger, period=2047
        self.ch.tick(2 * 32)  # Full cycle
        self.assertEqual(self.ch._wave_pos, 0)

    def test_reads_correct_nibbles(self):
        # Write 0xAB to first byte: upper=A, lower=B
        self.ch.write_wave_ram(0xFF30, 0xAB)
        self.ch.write(2, 0x20)  # volume code = 1 (100%, no shift)
        self.ch.write(3, 0xFF)
        self.ch.write(4, 0x87)  # trigger, period=2047

        # After trigger, wave_pos = 0, but we need to tick to read sample
        # First tick advances to pos 1 (lower nibble of byte 0)
        self.ch.tick(2)  # pos -> 1
        self.assertEqual(self.ch._sample_buffer, 0x0B)

        self.ch.tick(2)  # pos -> 2 (upper nibble of byte 1)

    def test_slow_period(self):
        # Period = 0: timer period = 2048*2 = 4096 T-cycles
        self.ch.write(3, 0x00)
        self.ch.write(4, 0x80)  # trigger, period=0
        self.ch.tick(4095)
        self.assertEqual(self.ch._wave_pos, 0)
        self.ch.tick(1)
        self.assertEqual(self.ch._wave_pos, 1)

    def test_disabled_channel_no_tick(self):
        self.ch.write(3, 0xFF)
        self.ch.write(4, 0x87)
        self.ch._enabled = False
        self.ch.tick(100)
        self.assertEqual(self.ch._wave_pos, 0)


class TestWaveChannelVolume(unittest.TestCase):
    """Test volume shift behavior."""

    def setUp(self):
        self.ch = WaveChannel()
        self.ch.write(0, 0x80)  # DAC on
        self.ch.write_wave_ram(0xFF30, 0xF0)  # Sample 0 = 0xF, Sample 1 = 0x0

    def _trigger_and_advance(self):
        """Trigger channel and advance to position 1 to read sample 0xF."""
        self.ch.write(3, 0xFF)
        self.ch.write(4, 0x87)  # trigger, period=2047
        # At trigger, wave_pos=0. Need to advance to read sample.
        # After one tick period, pos advances to 1 and reads lower nibble
        # Use position 0 which has upper nibble 0xF
        # Actually after trigger, sample_buffer is 0. The first tick reads pos 1.
        # Let's use a different approach: fill all samples with 0xF
        for i in range(16):
            self.ch.write_wave_ram(0xFF30 + i, 0xFF)
        self.ch.write(3, 0xFF)
        self.ch.write(4, 0x87)  # re-trigger
        self.ch.tick(2)  # Advance to pos 1, sample = 0xF

    def test_volume_code_0_mute(self):
        self._trigger_and_advance()
        self.ch.write(2, 0x00)  # volume code 0 = shift by 4
        self.assertEqual(self.ch.get_output(), 0)  # 0xF >> 4 = 0

    def test_volume_code_1_full(self):
        self._trigger_and_advance()
        self.ch.write(2, 0x20)  # volume code 1 = shift by 0
        self.assertEqual(self.ch.get_output(), 15)  # 0xF >> 0 = 15

    def test_volume_code_2_half(self):
        self._trigger_and_advance()
        self.ch.write(2, 0x40)  # volume code 2 = shift by 1
        self.assertEqual(self.ch.get_output(), 7)  # 0xF >> 1 = 7

    def test_volume_code_3_quarter(self):
        self._trigger_and_advance()
        self.ch.write(2, 0x60)  # volume code 3 = shift by 2
        self.assertEqual(self.ch.get_output(), 3)  # 0xF >> 2 = 3


class TestWaveChannelLengthCounter(unittest.TestCase):
    """Test length counter behavior (8-bit, max 256)."""

    def setUp(self):
        self.ch = WaveChannel()
        self.ch.write(0, 0x80)  # DAC on

    def test_length_countdown(self):
        self.ch.write(1, 254)  # counter = 256 - 254 = 2
        self.ch.write(4, 0xC0)  # trigger, length_enable=True
        self.assertTrue(self.ch._enabled)
        self.ch.clock_length()
        self.assertEqual(self.ch._length_counter, 1)
        self.ch.clock_length()
        self.assertFalse(self.ch._enabled)

    def test_length_disabled(self):
        self.ch.write(1, 254)
        self.ch.write(4, 0x80)  # trigger, length_enable=False
        self.ch.clock_length()
        self.ch.clock_length()
        self.assertTrue(self.ch._enabled)

    def test_trigger_reloads_length_when_zero(self):
        # length_load = 0 -> counter = 256, trigger should keep it
        self.ch.write(1, 0)
        self.ch.write(4, 0x80)
        self.assertEqual(self.ch._length_counter, 256)

    def test_trigger_reloads_length_from_zero_state(self):
        # Set counter to 0 manually, then trigger
        self.ch._length_counter = 0
        self.ch.write(4, 0x80)  # trigger
        self.assertEqual(self.ch._length_counter, 256)


class TestWaveChannelTrigger(unittest.TestCase):
    """Test trigger event behavior."""

    def setUp(self):
        self.ch = WaveChannel()

    def test_trigger_resets_wave_pos(self):
        self.ch.write(0, 0x80)  # DAC on
        self.ch.write(3, 0xFF)
        self.ch.write(4, 0x87)  # trigger
        self.ch.tick(20)  # Advance wave_pos
        self.assertNotEqual(self.ch._wave_pos, 0)
        self.ch.write(4, 0x87)  # re-trigger
        self.assertEqual(self.ch._wave_pos, 0)

    def test_trigger_reloads_freq_timer(self):
        self.ch.write(0, 0x80)
        self.ch.write(3, 0x00)
        self.ch.write(4, 0x80)  # trigger, period=0
        self.assertEqual(self.ch._freq_timer, 2048 * 2)


class TestWaveChannelPowerOff(unittest.TestCase):
    """Test power off behavior."""

    def test_power_off_resets_state(self):
        ch = WaveChannel()
        ch.write(0, 0x80)
        ch.write(4, 0x80)
        self.assertTrue(ch._enabled)
        ch.power_off()
        self.assertFalse(ch._enabled)
        self.assertFalse(ch._dac_enabled)

    def test_power_off_preserves_wave_ram(self):
        ch = WaveChannel()
        ch.write_wave_ram(0xFF30, 0xAB)
        ch.write_wave_ram(0xFF3F, 0xCD)
        ch.power_off()
        self.assertEqual(ch.read_wave_ram(0xFF30), 0xAB)
        self.assertEqual(ch.read_wave_ram(0xFF3F), 0xCD)


if __name__ == '__main__':
    unittest.main()
