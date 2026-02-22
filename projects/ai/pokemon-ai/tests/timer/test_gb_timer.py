import unittest

from src.timer.gb_timer import Timer
from src.memory.gb_memory import Memory


class TestTimerRegisters(unittest.TestCase):
    """Test basic timer register read/write."""

    def setUp(self):
        self.timer = Timer()

    def test_div_default_zero(self):
        self.assertEqual(self.timer.read(0xFF04), 0x00)

    def test_tima_default_zero(self):
        self.assertEqual(self.timer.read(0xFF05), 0x00)

    def test_tma_default_zero(self):
        self.assertEqual(self.timer.read(0xFF06), 0x00)

    def test_tac_default_reads_f8(self):
        """TAC upper 5 bits read as 1, lower 3 as 0."""
        self.assertEqual(self.timer.read(0xFF07), 0xF8)

    def test_write_read_tima(self):
        self.timer.write(0xFF05, 0x42)
        self.assertEqual(self.timer.read(0xFF05), 0x42)

    def test_write_read_tma(self):
        self.timer.write(0xFF06, 0xAB)
        self.assertEqual(self.timer.read(0xFF06), 0xAB)

    def test_write_read_tac(self):
        self.timer.write(0xFF07, 0x07)
        self.assertEqual(self.timer.read(0xFF07), 0xFF)  # 0x07 | 0xF8

    def test_tac_masks_to_3_bits(self):
        self.timer.write(0xFF07, 0xFF)
        self.assertEqual(self.timer._tac, 0x07)

    def test_write_div_resets_counter(self):
        """Writing ANY value to DIV resets the internal counter to 0."""
        self.timer.tick(512)  # Advance counter
        self.assertNotEqual(self.timer.read(0xFF04), 0)
        self.timer.write(0xFF04, 0x42)  # Value doesn't matter
        self.assertEqual(self.timer.read(0xFF04), 0)
        self.assertEqual(self.timer._internal_counter, 0)


class TestDIVCounter(unittest.TestCase):
    """Test DIV register (upper 8 bits of internal counter)."""

    def setUp(self):
        self.timer = Timer()

    def test_div_increments_every_256_cycles(self):
        """DIV is bits 8-15 of internal counter, so it increments every 256 T-cycles."""
        self.timer.tick(256)
        self.assertEqual(self.timer.read(0xFF04), 1)

    def test_div_increments_twice_at_512(self):
        self.timer.tick(512)
        self.assertEqual(self.timer.read(0xFF04), 2)

    def test_div_not_incremented_at_255(self):
        self.timer.tick(255)
        self.assertEqual(self.timer.read(0xFF04), 0)

    def test_div_wraps_at_256(self):
        """DIV is 8-bit, wraps from 0xFF to 0x00."""
        self.timer.tick(256 * 256)  # 65536 cycles -> DIV wraps
        self.assertEqual(self.timer.read(0xFF04), 0)

    def test_div_ticks_regardless_of_timer_enable(self):
        """DIV always ticks, even when TAC timer is disabled."""
        self.timer.write(0xFF07, 0x00)  # Timer disabled
        self.timer.tick(256)
        self.assertEqual(self.timer.read(0xFF04), 1)


class TestTIMAClockRates(unittest.TestCase):
    """Test TIMA incrementing at each TAC clock rate."""

    def setUp(self):
        self.timer = Timer()
        self.mem = Memory()
        self.mem.load_timer(self.timer)

    def test_tima_rate_1024_cycles(self):
        """TAC=0b100 (enabled, clock 00): TIMA ticks every 1024 T-cycles."""
        self.timer.write(0xFF07, 0x04)  # Enable, clock select 00
        self.timer.tick(1024)
        self.assertEqual(self.timer.read(0xFF05), 1)

    def test_tima_rate_16_cycles(self):
        """TAC=0b101 (enabled, clock 01): TIMA ticks every 16 T-cycles."""
        self.timer.write(0xFF07, 0x05)  # Enable, clock select 01
        self.timer.tick(16)
        self.assertEqual(self.timer.read(0xFF05), 1)

    def test_tima_rate_64_cycles(self):
        """TAC=0b110 (enabled, clock 10): TIMA ticks every 64 T-cycles."""
        self.timer.write(0xFF07, 0x06)  # Enable, clock select 10
        self.timer.tick(64)
        self.assertEqual(self.timer.read(0xFF05), 1)

    def test_tima_rate_256_cycles(self):
        """TAC=0b111 (enabled, clock 11): TIMA ticks every 256 T-cycles."""
        self.timer.write(0xFF07, 0x07)  # Enable, clock select 11
        self.timer.tick(256)
        self.assertEqual(self.timer.read(0xFF05), 1)

    def test_tima_not_before_threshold(self):
        """TIMA should NOT increment before the clock threshold."""
        self.timer.write(0xFF07, 0x04)  # Enable, clock select 00 (1024)
        self.timer.tick(1023)
        self.assertEqual(self.timer.read(0xFF05), 0)

    def test_tima_multiple_ticks(self):
        """TIMA increments multiple times over many cycles."""
        self.timer.write(0xFF07, 0x05)  # Enable, clock select 01 (16)
        self.timer.tick(16 * 5)
        self.assertEqual(self.timer.read(0xFF05), 5)

    def test_tima_disabled(self):
        """TIMA does NOT increment when timer is disabled."""
        self.timer.write(0xFF07, 0x01)  # Disabled, clock select 01
        self.timer.tick(1024)
        self.assertEqual(self.timer.read(0xFF05), 0)


class TestTIMAOverflow(unittest.TestCase):
    """Test TIMA overflow -> TMA reload and interrupt."""

    def setUp(self):
        self.timer = Timer()
        self.mem = Memory()
        self.mem.load_timer(self.timer)

    def test_tima_overflow_reloads_from_tma(self):
        """When TIMA overflows past 0xFF, it reloads from TMA."""
        self.timer.write(0xFF06, 0x80)  # TMA = 0x80
        self.timer.write(0xFF05, 0xFF)  # TIMA = 0xFF (about to overflow)
        self.timer.write(0xFF07, 0x05)  # Enable, clock select 01 (16 cycles)
        self.timer.tick(16)  # One tick -> TIMA overflows
        self.assertEqual(self.timer.read(0xFF05), 0x80)  # Reloaded from TMA

    def test_tima_overflow_sets_if_bit2(self):
        """TIMA overflow sets bit 2 of IF register (timer interrupt)."""
        self.timer.write(0xFF05, 0xFF)
        self.timer.write(0xFF07, 0x05)  # Enable, 16-cycle rate
        self.timer.tick(16)
        if_val = self.mem.memory[0xFF0F]
        self.assertTrue(if_val & 0x04, "Timer interrupt (IF bit 2) should be set")

    def test_tima_overflow_preserves_other_if_bits(self):
        """Timer interrupt should not clear other IF bits."""
        self.mem.memory[0xFF0F] = 0x01  # V-Blank already pending
        self.timer.write(0xFF05, 0xFF)
        self.timer.write(0xFF07, 0x05)
        self.timer.tick(16)
        if_val = self.mem.memory[0xFF0F]
        self.assertEqual(if_val & 0x05, 0x05)  # Both V-Blank and Timer set

    def test_tima_no_overflow_no_interrupt(self):
        """No overflow -> no interrupt."""
        self.timer.write(0xFF05, 0xFE)  # One below overflow
        self.timer.write(0xFF07, 0x05)
        self.timer.tick(16)
        self.assertEqual(self.timer.read(0xFF05), 0xFF)
        self.assertEqual(self.mem.memory[0xFF0F] & 0x04, 0)


class TestTimerMemoryIntegration(unittest.TestCase):
    """Test timer through the Memory dispatch."""

    def test_memory_dispatches_timer_reads(self):
        mem = Memory()
        timer = Timer()
        mem.load_timer(timer)

        timer.tick(256)
        self.assertEqual(mem.get_value(0xFF04), 1)  # DIV

    def test_memory_dispatches_timer_writes(self):
        mem = Memory()
        timer = Timer()
        mem.load_timer(timer)

        mem.set_value(0xFF06, 0x42)  # TMA
        self.assertEqual(timer.read(0xFF06), 0x42)

    def test_div_reset_through_memory(self):
        mem = Memory()
        timer = Timer()
        mem.load_timer(timer)

        timer.tick(512)
        self.assertEqual(mem.get_value(0xFF04), 2)
        mem.set_value(0xFF04, 0x00)  # Reset DIV
        self.assertEqual(mem.get_value(0xFF04), 0)


class TestTimerCPUIntegration(unittest.TestCase):
    """Test that the CPU run loop ticks the timer."""

    def test_cpu_ticks_timer(self):
        """Timer should advance when CPU executes instructions."""
        from src.cpu.gb_cpu import CPU

        mem = Memory()
        cpu = CPU(memory=mem)

        timer = Timer()
        mem.load_timer(timer)  # Must be after CPU creation so _cpu ref exists

        # Place a NOP (0x00) at address 0x0000 — 4 T-cycles
        mem.memory[0x0000] = 0x00

        cpu.registers.PC = 0x0000
        cpu.run(max_cycles=4)

        # NOP is 4 cycles, so internal counter should be 4
        self.assertEqual(timer._internal_counter, 4)

    def test_timer_interrupt_fires_through_cpu(self):
        """Full integration: timer overflow -> IF bit -> CPU services interrupt."""
        from src.cpu.gb_cpu import CPU

        mem = Memory()
        cpu = CPU(memory=mem)

        timer = Timer()
        mem.load_timer(timer)  # Must be after CPU creation so _cpu ref exists

        # Enable timer at fastest rate (16 T-cycles per TIMA tick)
        timer.write(0xFF07, 0x05)
        timer.write(0xFF05, 0xFF)  # TIMA about to overflow
        timer.write(0xFF06, 0x00)  # TMA = 0

        # Enable timer interrupt in IE, enable IME
        cpu.interrupts.ime = True
        mem.memory[0xFFFF] = 0x04  # IE: timer interrupt enabled

        # Place NOPs as filler, and a simple handler at 0x0050 (timer vector)
        # Handler: just a NOP + infinite loop won't matter, we just check IF clears
        for i in range(0x100):
            mem.memory[i] = 0x00  # NOP everywhere

        cpu.registers.PC = 0x0000
        # Run enough cycles for timer to overflow (16 cycles = 4 NOPs)
        # then interrupt service (20 cycles)
        cpu.run(max_cycles=40)

        # Timer interrupt should have been serviced (IF bit 2 cleared)
        self.assertEqual(mem.memory[0xFF0F] & 0x04, 0)
        # PC should have jumped to timer vector 0x0050
        # (or past it if NOPs were executed there)
        self.assertGreaterEqual(cpu.registers.PC, 0x0050)


if __name__ == "__main__":
    unittest.main()
