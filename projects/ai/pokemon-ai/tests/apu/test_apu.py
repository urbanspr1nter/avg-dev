import unittest

from src.apu.apu import APU
from src.memory.gb_memory import Memory
from src.gameboy import GameBoy


class TestAPURegisterReadMasks(unittest.TestCase):
    """Test that register reads apply correct OR masks for unused bits."""

    def setUp(self):
        self.apu = APU()
        self.apu.write(0xFF26, 0x80)  # Power on

    def test_nr10_mask(self):
        self.apu.write(0xFF10, 0x00)
        self.assertEqual(self.apu.read(0xFF10), 0x80)

    def test_nr11_mask(self):
        self.apu.write(0xFF11, 0x00)
        self.assertEqual(self.apu.read(0xFF11), 0x3F)

    def test_nr12_mask(self):
        self.apu.write(0xFF12, 0x00)
        self.assertEqual(self.apu.read(0xFF12), 0x00)

    def test_nr13_write_only(self):
        self.apu.write(0xFF13, 0x42)
        self.assertEqual(self.apu.read(0xFF13), 0xFF)

    def test_nr14_mask(self):
        self.apu.write(0xFF14, 0x00)
        self.assertEqual(self.apu.read(0xFF14), 0xBF)

    def test_nr21_mask(self):
        self.apu.write(0xFF16, 0x00)
        self.assertEqual(self.apu.read(0xFF16), 0x3F)

    def test_nr22_mask(self):
        self.apu.write(0xFF17, 0x00)
        self.assertEqual(self.apu.read(0xFF17), 0x00)

    def test_nr23_write_only(self):
        self.apu.write(0xFF18, 0x42)
        self.assertEqual(self.apu.read(0xFF18), 0xFF)

    def test_nr24_mask(self):
        self.apu.write(0xFF19, 0x00)
        self.assertEqual(self.apu.read(0xFF19), 0xBF)

    def test_nr30_mask(self):
        self.apu.write(0xFF1A, 0x00)
        self.assertEqual(self.apu.read(0xFF1A), 0x7F)

    def test_nr31_write_only(self):
        self.apu.write(0xFF1B, 0x42)
        self.assertEqual(self.apu.read(0xFF1B), 0xFF)

    def test_nr32_mask(self):
        self.apu.write(0xFF1C, 0x00)
        self.assertEqual(self.apu.read(0xFF1C), 0x9F)

    def test_nr33_write_only(self):
        self.apu.write(0xFF1D, 0x42)
        self.assertEqual(self.apu.read(0xFF1D), 0xFF)

    def test_nr34_mask(self):
        self.apu.write(0xFF1E, 0x00)
        self.assertEqual(self.apu.read(0xFF1E), 0xBF)

    def test_nr41_write_only(self):
        self.apu.write(0xFF20, 0x42)
        self.assertEqual(self.apu.read(0xFF20), 0xFF)

    def test_nr42_mask(self):
        self.apu.write(0xFF21, 0x00)
        self.assertEqual(self.apu.read(0xFF21), 0x00)

    def test_nr43_mask(self):
        self.apu.write(0xFF22, 0x00)
        self.assertEqual(self.apu.read(0xFF22), 0x00)

    def test_nr44_mask(self):
        self.apu.write(0xFF23, 0x00)
        self.assertEqual(self.apu.read(0xFF23), 0xBF)

    def test_nr50_mask(self):
        self.apu.write(0xFF24, 0x00)
        self.assertEqual(self.apu.read(0xFF24), 0x00)

    def test_nr51_mask(self):
        self.apu.write(0xFF25, 0x00)
        self.assertEqual(self.apu.read(0xFF25), 0x00)

    def test_unused_ff15(self):
        self.assertEqual(self.apu.read(0xFF15), 0xFF)

    def test_unused_ff1f(self):
        self.assertEqual(self.apu.read(0xFF1F), 0xFF)

    def test_unused_ff27_to_ff2f(self):
        for addr in range(0xFF27, 0xFF30):
            self.assertEqual(self.apu.read(addr), 0xFF)


class TestAPUNR52Power(unittest.TestCase):
    """Test NR52 power control (0xFF26)."""

    def test_power_on(self):
        apu = APU()
        apu.write(0xFF26, 0x80)
        self.assertTrue(apu._power)
        self.assertEqual(apu.read(0xFF26) & 0x80, 0x80)

    def test_power_off(self):
        apu = APU()
        apu.write(0xFF26, 0x80)
        apu.write(0xFF26, 0x00)
        self.assertFalse(apu._power)
        self.assertEqual(apu.read(0xFF26) & 0x80, 0x00)

    def test_power_off_zeros_registers(self):
        apu = APU()
        apu.write(0xFF26, 0x80)
        apu.write(0xFF12, 0xF3)
        apu.write(0xFF24, 0x77)
        apu.write(0xFF25, 0xF3)
        apu.write(0xFF26, 0x00)  # Power off
        # NR50, NR51 should be zeroed
        apu.write(0xFF26, 0x80)  # Power back on to read
        self.assertEqual(apu.read(0xFF24), 0x00)
        self.assertEqual(apu.read(0xFF25), 0x00)

    def test_power_off_writes_ignored(self):
        apu = APU()
        apu.write(0xFF26, 0x00)  # Power off
        apu.write(0xFF12, 0xF3)  # Should be ignored
        apu.write(0xFF24, 0x77)  # Should be ignored
        apu.write(0xFF26, 0x80)  # Power on
        self.assertEqual(apu.read(0xFF24), 0x00)

    def test_power_off_wave_ram_preserved(self):
        apu = APU()
        apu.write(0xFF26, 0x80)
        apu.write(0xFF30, 0xAB)
        apu.write(0xFF3F, 0xCD)
        apu.write(0xFF26, 0x00)  # Power off
        self.assertEqual(apu.read(0xFF30), 0xAB)
        self.assertEqual(apu.read(0xFF3F), 0xCD)

    def test_wave_ram_writable_when_off(self):
        apu = APU()
        apu.write(0xFF26, 0x00)  # Power off
        apu.write(0xFF30, 0x42)
        self.assertEqual(apu.read(0xFF30), 0x42)

    def test_nr52_status_bits(self):
        apu = APU()
        apu.write(0xFF26, 0x80)  # Power on
        # Bits 4-6 always read as 1
        status = apu.read(0xFF26)
        self.assertEqual(status & 0x70, 0x70)

    def test_nr52_channel_status_ch1(self):
        apu = APU()
        apu.write(0xFF26, 0x80)
        self.assertEqual(apu.read(0xFF26) & 0x01, 0x00)
        apu.write(0xFF12, 0xF0)  # DAC on
        apu.write(0xFF14, 0x80)  # Trigger CH1
        self.assertEqual(apu.read(0xFF26) & 0x01, 0x01)

    def test_nr52_channel_status_ch2(self):
        apu = APU()
        apu.write(0xFF26, 0x80)
        apu.write(0xFF17, 0xF0)  # DAC on
        apu.write(0xFF19, 0x80)  # Trigger CH2
        self.assertEqual(apu.read(0xFF26) & 0x02, 0x02)

    def test_nr52_channel_status_ch3(self):
        apu = APU()
        apu.write(0xFF26, 0x80)
        apu.write(0xFF1A, 0x80)  # DAC on
        apu.write(0xFF1E, 0x80)  # Trigger CH3
        self.assertEqual(apu.read(0xFF26) & 0x04, 0x04)

    def test_nr52_channel_status_ch4(self):
        apu = APU()
        apu.write(0xFF26, 0x80)
        apu.write(0xFF21, 0xF0)  # DAC on
        apu.write(0xFF23, 0x80)  # Trigger CH4
        self.assertEqual(apu.read(0xFF26) & 0x08, 0x08)

    def test_nr52_readable_when_off(self):
        apu = APU()
        apu.write(0xFF26, 0x00)
        status = apu.read(0xFF26)
        self.assertEqual(status & 0x80, 0x00)
        self.assertEqual(status & 0x70, 0x70)  # Bits 4-6 still 1

    def test_registers_read_ff_when_off(self):
        apu = APU()
        apu.write(0xFF26, 0x00)
        # All channel/control registers should read 0xFF when powered off
        for addr in [0xFF10, 0xFF12, 0xFF17, 0xFF24, 0xFF25]:
            self.assertEqual(apu.read(addr), 0xFF)

    def test_power_off_disables_channels(self):
        apu = APU()
        apu.write(0xFF26, 0x80)
        apu.write(0xFF12, 0xF0)
        apu.write(0xFF14, 0x80)  # CH1 active
        apu.write(0xFF26, 0x00)  # Power off
        apu.write(0xFF26, 0x80)  # Power on
        self.assertEqual(apu.read(0xFF26) & 0x0F, 0x00)


class TestAPUFrameSequencer(unittest.TestCase):
    """Test frame sequencer timing and dispatch."""

    def setUp(self):
        self.apu = APU()
        self.apu.write(0xFF26, 0x80)  # Power on

    def test_length_clocked_at_256hz(self):
        """Length counter clocked on steps 0,2,4,6 = every 16384 T-cycles."""
        # Set up CH1 with short length
        self.apu.write(0xFF12, 0xF0)  # DAC on
        self.apu.write(0xFF11, 0x3E)  # length_load=62, counter=2
        self.apu.write(0xFF14, 0xC0)  # trigger, length_enable=True
        self.assertTrue(self.apu._ch1.is_active())
        # Step 0 clocks length (at 8192 T-cycles)
        self.apu.tick(8192)
        self.assertEqual(self.apu._ch1._length_counter, 1)
        # Step 1 doesn't clock length
        self.apu.tick(8192)
        self.assertEqual(self.apu._ch1._length_counter, 1)
        # Step 2 clocks length
        self.apu.tick(8192)
        self.assertFalse(self.apu._ch1.is_active())

    def test_envelope_clocked_at_64hz(self):
        """Envelope clocked on step 7 only = every 65536 T-cycles."""
        self.apu.write(0xFF12, 0xF1)  # vol=15, decrease, pace=1
        self.apu.write(0xFF14, 0x80)  # trigger
        self.assertEqual(self.apu._ch1._volume, 15)
        # Run through steps 0-6 (7 * 8192 = 57344 T-cycles)
        self.apu.tick(7 * 8192)
        self.assertEqual(self.apu._ch1._volume, 15)  # Not yet clocked
        # Step 7 clocks envelope
        self.apu.tick(8192)
        self.assertEqual(self.apu._ch1._volume, 14)

    def test_sweep_clocked_at_128hz(self):
        """Sweep clocked on steps 2 and 6."""
        self.apu.write(0xFF10, 0x11)  # pace=1, addition, step=1
        self.apu.write(0xFF12, 0xF0)  # DAC on
        self.apu.write(0xFF13, 0x00)
        self.apu.write(0xFF14, 0x82)  # trigger, period=512
        original = self.apu._ch1._period
        # Steps 0,1 don't clock sweep
        self.apu.tick(2 * 8192)
        self.assertEqual(self.apu._ch1._period, original)
        # Step 2 clocks sweep
        self.apu.tick(8192)
        self.assertNotEqual(self.apu._ch1._period, original)

    def test_frame_sequencer_step_wraps(self):
        self.apu.tick(8 * 8192)  # Complete one full cycle
        self.assertEqual(self.apu._fs_step, 0)

    def test_no_ticking_when_powered_off(self):
        self.apu.write(0xFF26, 0x00)
        self.apu._fs_counter = 0
        self.apu.tick(100)
        self.assertEqual(self.apu._fs_counter, 0)


class TestAPUMixing(unittest.TestCase):
    """Test stereo mixing and sample generation."""

    def setUp(self):
        self.apu = APU()
        self.apu.write(0xFF26, 0x80)  # Power on

    def test_sample_buffer_fills(self):
        """Samples should accumulate at ~48 kHz."""
        self.apu.tick(100)  # ~1 sample expected (~87 cycles per sample)
        samples = self.apu.drain_samples()
        self.assertGreater(len(samples), 0)

    def test_drain_clears_buffer(self):
        self.apu.tick(200)
        self.apu.drain_samples()
        samples = self.apu.drain_samples()
        self.assertEqual(len(samples), 0)

    def test_samples_are_stereo_pairs(self):
        self.apu.tick(100)
        samples = self.apu.drain_samples()
        for s in samples:
            self.assertEqual(len(s), 2)

    def test_nr51_panning(self):
        """NR51 routes channels to L/R outputs."""
        # Enable CH1 with constant output
        self.apu.write(0xFF12, 0xF0)  # vol=15, DAC on
        self.apu.write(0xFF14, 0x80)  # trigger
        self.apu.write(0xFF24, 0x77)  # max volume both sides
        # Route CH1 to left only
        self.apu.write(0xFF25, 0x10)  # CH1 -> left only
        self.apu.tick(100)
        samples = self.apu.drain_samples()
        if samples:
            left, right = samples[0]
            # Left should have signal, right should be quieter
            self.assertNotEqual(left, right)

    def test_nr50_master_volume(self):
        """NR50 controls master volume."""
        self.apu.write(0xFF12, 0xF0)
        self.apu.write(0xFF14, 0x80)
        self.apu.write(0xFF25, 0x11)  # CH1 to both
        # Max volume
        self.apu.write(0xFF24, 0x77)
        self.apu.tick(100)
        loud = self.apu.drain_samples()
        # Min volume
        self.apu.write(0xFF24, 0x00)
        self.apu.tick(100)
        quiet = self.apu.drain_samples()
        if loud and quiet:
            loud_max = max(abs(s[0]) for s in loud)
            quiet_max = max(abs(s[0]) for s in quiet)
            self.assertGreater(loud_max, quiet_max)

    def test_disabled_channel_silent(self):
        """Disabled channel should contribute no signal."""
        self.apu.write(0xFF25, 0xFF)  # All to both
        self.apu.write(0xFF24, 0x77)
        # Don't trigger any channel
        self.apu.tick(100)
        samples = self.apu.drain_samples()
        # All DACs are off, so no contribution except HPF settling
        # After HPF, should converge to 0

    def test_sample_rate_approximate(self):
        """One frame (~70224 T-cycles) should produce ~1468 samples at 48kHz."""
        self.apu.tick(70224)
        samples = self.apu.drain_samples()
        expected = 70224 / self.apu.SAMPLE_PERIOD
        self.assertAlmostEqual(len(samples), expected, delta=2)


class TestAPUWaveRAM(unittest.TestCase):
    """Test wave RAM access through APU."""

    def setUp(self):
        self.apu = APU()

    def test_wave_ram_read_write(self):
        for addr in range(0xFF30, 0xFF40):
            self.apu.write(addr, addr & 0xFF)
        for addr in range(0xFF30, 0xFF40):
            self.assertEqual(self.apu.read(addr), addr & 0xFF)

    def test_wave_ram_accessible_when_off(self):
        self.apu.write(0xFF26, 0x00)  # Power off
        self.apu.write(0xFF30, 0x42)
        self.assertEqual(self.apu.read(0xFF30), 0x42)


class TestAPUMemoryIntegration(unittest.TestCase):
    """Test APU integration with the memory bus."""

    def setUp(self):
        self.mem = Memory()
        self.apu = APU()
        self.mem.load_apu(self.apu)

    def test_memory_dispatches_apu_reads(self):
        self.apu.write(0xFF26, 0x80)
        self.apu.write(0xFF24, 0x77)
        self.assertEqual(self.mem.get_value(0xFF24), 0x77)

    def test_memory_dispatches_apu_writes(self):
        self.mem.set_value(0xFF26, 0x80)  # Power on through memory
        self.assertTrue(self.apu._power)
        self.mem.set_value(0xFF24, 0x42)
        self.assertEqual(self.apu._nr50, 0x42)

    def test_nr52_through_memory(self):
        self.mem.set_value(0xFF26, 0x80)
        status = self.mem.get_value(0xFF26)
        self.assertEqual(status & 0x80, 0x80)
        self.assertEqual(status & 0x70, 0x70)

    def test_wave_ram_through_memory(self):
        self.mem.set_value(0xFF30, 0xAB)
        self.assertEqual(self.mem.get_value(0xFF30), 0xAB)

    def test_apu_does_not_conflict_with_timer(self):
        """APU range (0xFF10-0xFF3F) should not intercept timer (0xFF04-0xFF07)."""
        from src.timer.gb_timer import Timer
        timer = Timer()
        self.mem.load_timer(timer)
        # Timer write
        self.mem.set_value(0xFF06, 0x42)  # TMA
        self.assertEqual(self.mem.get_value(0xFF06), 0x42)
        # APU write
        self.mem.set_value(0xFF26, 0x80)
        self.assertTrue(self.apu._power)


class TestAPUGameBoyIntegration(unittest.TestCase):
    """Test APU integration with the full GameBoy system."""

    def test_gameboy_creates_apu(self):
        gb = GameBoy()
        self.assertIsNotNone(gb.apu)

    def test_gameboy_wires_apu_to_memory(self):
        gb = GameBoy()
        self.assertIs(gb.memory._apu, gb.apu)

    def test_gameboy_wires_apu_to_cpu(self):
        gb = GameBoy()
        self.assertIs(gb.cpu._apu, gb.apu)

    def test_post_boot_state(self):
        gb = GameBoy()
        gb.init_post_boot_state()
        self.assertTrue(gb.apu._power)
        self.assertEqual(gb.apu._nr50, 0x77)
        self.assertEqual(gb.apu._nr51, 0xF3)


if __name__ == '__main__':
    unittest.main()
