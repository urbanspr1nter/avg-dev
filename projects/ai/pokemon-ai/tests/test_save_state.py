import pickle
import unittest

from src.apu.pulse_channel import PulseChannel
from src.apu.wave_channel import WaveChannel
from src.apu.noise_channel import NoiseChannel
from src.apu.apu import APU
from src.timer.gb_timer import Timer
from src.serial.serial import Serial
from src.joypad.joypad import Joypad
from src.ppu.ppu import PPU
from src.memory.gb_memory import Memory
from src.cpu.gb_cpu import CPU
from src.cartridge.mbc import NoMBC, MBC1, MBC3, MBC5
from src.gameboy import GameBoy


class TestPulseChannelSaveState(unittest.TestCase):
    def test_round_trip_ch1(self):
        ch = PulseChannel(has_sweep=True)
        ch.write(0, 0x37)  # sweep
        ch.write(1, 0xC0)  # duty 75%, length
        ch.write(2, 0xF3)  # vol 15, dec, pace 3
        ch.write(3, 0xAB)  # period low
        ch.write(4, 0x87)  # trigger, period high
        ch.tick(100)

        state = ch.save_state()
        ch2 = PulseChannel(has_sweep=True)
        ch2.load_state(state)

        self.assertEqual(ch2._enabled, ch._enabled)
        self.assertEqual(ch2._volume, ch._volume)
        self.assertEqual(ch2._period, ch._period)
        self.assertEqual(ch2._duty_pos, ch._duty_pos)
        self.assertEqual(ch2._sweep_shadow, ch._sweep_shadow)
        self.assertEqual(ch2._sweep_enabled, ch._sweep_enabled)

    def test_round_trip_ch2(self):
        ch = PulseChannel(has_sweep=False)
        ch.write(2, 0xA1)
        ch.write(4, 0x80)  # trigger
        state = ch.save_state()
        self.assertNotIn('sweep_shadow', state)

        ch2 = PulseChannel(has_sweep=False)
        ch2.load_state(state)
        self.assertEqual(ch2._volume, ch._volume)

    def test_pickle_round_trip(self):
        ch = PulseChannel(has_sweep=True)
        ch.write(2, 0xF0)
        ch.write(4, 0x80)
        data = pickle.dumps(ch.save_state())
        state = pickle.loads(data)
        ch2 = PulseChannel(has_sweep=True)
        ch2.load_state(state)
        self.assertEqual(ch2._enabled, ch._enabled)


class TestWaveChannelSaveState(unittest.TestCase):
    def test_round_trip(self):
        ch = WaveChannel()
        ch.write(0, 0x80)  # DAC on
        for i in range(16):
            ch.write_wave_ram(0xFF30 + i, i * 17)
        ch.write(3, 0xFF)
        ch.write(4, 0x87)  # trigger
        ch.tick(10)

        state = ch.save_state()
        ch2 = WaveChannel()
        ch2.load_state(state)

        self.assertEqual(ch2._enabled, ch._enabled)
        self.assertEqual(ch2._wave_pos, ch._wave_pos)
        self.assertEqual(ch2._period, ch._period)
        for i in range(16):
            self.assertEqual(ch2._wave_ram[i], ch._wave_ram[i])

    def test_wave_ram_preserved(self):
        ch = WaveChannel()
        for i in range(16):
            ch.write_wave_ram(0xFF30 + i, 0xAB)
        state = ch.save_state()
        ch2 = WaveChannel()
        ch2.load_state(state)
        for i in range(16):
            self.assertEqual(ch2.read_wave_ram(0xFF30 + i), 0xAB)


class TestNoiseChannelSaveState(unittest.TestCase):
    def test_round_trip(self):
        ch = NoiseChannel()
        ch.write(1, 0xF0)  # DAC on
        ch.write(2, 0xB5)
        ch.write(3, 0x80)  # trigger
        ch.tick(50)

        state = ch.save_state()
        ch2 = NoiseChannel()
        ch2.load_state(state)

        self.assertEqual(ch2._lfsr, ch._lfsr)
        self.assertEqual(ch2._volume, ch._volume)
        self.assertEqual(ch2._clock_shift, ch._clock_shift)
        self.assertEqual(ch2._enabled, ch._enabled)


class TestAPUSaveState(unittest.TestCase):
    def test_round_trip(self):
        apu = APU()
        apu.write(0xFF26, 0x80)  # power on
        apu.write(0xFF24, 0x77)
        apu.write(0xFF25, 0xF3)
        apu.write(0xFF12, 0xF3)
        apu.write(0xFF14, 0x80)  # trigger CH1
        apu.tick(1000)

        state = apu.save_state()
        apu2 = APU()
        apu2.load_state(state)

        self.assertEqual(apu2._power, apu._power)
        self.assertEqual(apu2._nr50, apu._nr50)
        self.assertEqual(apu2._nr51, apu._nr51)
        self.assertEqual(apu2._fs_step, apu._fs_step)
        self.assertEqual(apu2._fs_counter, apu._fs_counter)

    def test_sample_buffer_cleared(self):
        apu = APU()
        apu.write(0xFF26, 0x80)
        apu.tick(1000)
        self.assertGreater(len(apu._sample_buffer), 0)

        state = apu.save_state()
        apu2 = APU()
        apu2.load_state(state)
        self.assertEqual(len(apu2._sample_buffer), 0)


class TestTimerSaveState(unittest.TestCase):
    def test_round_trip(self):
        t = Timer()
        t.write(0xFF06, 0x42)  # TMA
        t.write(0xFF07, 0x05)  # TAC enabled, 262144 Hz
        t.tick(100)

        state = t.save_state()
        t2 = Timer()
        t2.load_state(state)

        self.assertEqual(t2._internal_counter, t._internal_counter)
        self.assertEqual(t2._tima, t._tima)
        self.assertEqual(t2._tma, t._tma)
        self.assertEqual(t2._tac, t._tac)


class TestSerialSaveState(unittest.TestCase):
    def test_round_trip(self):
        s = Serial()
        s.write(0xFF01, 0x41)  # 'A'
        s.write(0xFF02, 0x81)  # transfer

        state = s.save_state()
        s2 = Serial()
        s2.load_state(state)

        self.assertEqual(s2._sb, s._sb)
        self.assertEqual(s2._sc, s._sc)
        self.assertEqual(s2._output_buffer, s._output_buffer)


class TestJoypadSaveState(unittest.TestCase):
    def test_round_trip(self):
        j = Joypad()
        j.press('a')
        j.press('up')

        state = j.save_state()
        j2 = Joypad()
        j2.load_state(state)

        self.assertEqual(j2._dpad, j._dpad)
        self.assertEqual(j2._buttons, j._buttons)
        self.assertEqual(j2._select, j._select)


class TestPPUSaveState(unittest.TestCase):
    def test_round_trip(self):
        ppu = PPU()
        ppu._lcdc = 0x91
        ppu._ly = 42
        ppu._dot = 200
        ppu._mode = 3
        ppu._window_line = 5

        state = ppu.save_state()
        ppu2 = PPU()
        ppu2.load_state(state)

        self.assertEqual(ppu2._lcdc, 0x91)
        self.assertEqual(ppu2._ly, 42)
        self.assertEqual(ppu2._dot, 200)
        self.assertEqual(ppu2._mode, 3)
        self.assertEqual(ppu2._window_line, 5)

    def test_framebuffer_cleared(self):
        ppu = PPU()
        ppu._framebuffer[0][0] = 3
        state = ppu.save_state()
        ppu2 = PPU()
        ppu2.load_state(state)
        self.assertEqual(ppu2._framebuffer[0][0], 0)


class TestMemorySaveState(unittest.TestCase):
    def test_round_trip(self):
        mem = Memory()
        mem.memory[0xC000] = 0x42
        mem.memory[0xFF80] = 0xAB
        mem.memory[0xFFFF] = 0x1F

        state = mem.save_state()
        mem2 = Memory()
        mem2.load_state(state)

        self.assertEqual(mem2.memory[0xC000], 0x42)
        self.assertEqual(mem2.memory[0xFF80], 0xAB)
        self.assertEqual(mem2.memory[0xFFFF], 0x1F)

    def test_compact_bytes(self):
        mem = Memory()
        state = mem.save_state()
        self.assertIsInstance(state['memory'], bytes)
        self.assertEqual(len(state['memory']), 65536)


class TestMBCSaveState(unittest.TestCase):
    def test_no_mbc(self):
        mbc = NoMBC(b'\x00' * 0x8000)
        state = mbc.save_state()
        self.assertEqual(state, {})
        mbc.load_state(state)  # should not raise

    def test_mbc1(self):
        rom = b'\x00' * (0x4000 * 4)
        mbc = MBC1(rom, 4, 8192)
        mbc.write(0x2000, 0x02)  # ROM bank 2
        mbc.write(0xA000, 0x42)  # Write to disabled RAM (ignored)
        mbc.write(0x0000, 0x0A)  # Enable RAM
        mbc.write(0xA000, 0x42)  # Write to RAM

        state = mbc.save_state()
        mbc2 = MBC1(rom, 4, 8192)
        mbc2.load_state(state)

        self.assertEqual(mbc2._rom_bank, 2)
        self.assertEqual(mbc2._ram_enabled, True)
        self.assertEqual(mbc2._ram[0], 0x42)

    def test_mbc3(self):
        rom = b'\x00' * (0x4000 * 4)
        mbc = MBC3(rom, 4, 8192, has_rtc=True)
        mbc.start_rtc()
        mbc.write(0x2000, 0x03)
        mbc.write(0x0000, 0x0A)
        mbc.write(0xA000, 0x99)

        state = mbc.save_state()
        mbc2 = MBC3(rom, 4, 8192, has_rtc=True)
        mbc2.load_state(state)

        self.assertEqual(mbc2._rom_bank, 3)
        self.assertEqual(mbc2._ram[0], 0x99)
        self.assertIsNotNone(mbc2._rtc_base_timestamp)

    def test_mbc5(self):
        rom = b'\x00' * (0x4000 * 4)
        mbc = MBC5(rom, 4, 8192, has_rumble=True)
        mbc.write(0x2000, 0x02)
        mbc.write(0x0000, 0x0A)
        mbc.write(0xA000, 0x55)

        state = mbc.save_state()
        mbc2 = MBC5(rom, 4, 8192, has_rumble=True)
        mbc2.load_state(state)

        self.assertEqual(mbc2._rom_bank, 2)
        self.assertEqual(mbc2._ram[0], 0x55)

    def test_mbc_ram_preserved(self):
        rom = b'\x00' * (0x4000 * 4)
        mbc = MBC1(rom, 4, 8192)
        mbc.write(0x0000, 0x0A)
        for i in range(256):
            mbc.write(0xA000 + i, i)

        state = mbc.save_state()
        mbc2 = MBC1(rom, 4, 8192)
        mbc2.load_state(state)

        for i in range(256):
            self.assertEqual(mbc2._ram[i], i)


class TestCPUSaveState(unittest.TestCase):
    def test_round_trip(self):
        cpu = CPU()
        cpu.registers.AF = 0x01B0
        cpu.registers.BC = 0x0013
        cpu.registers.PC = 0x0100
        cpu.registers.SP = 0xFFFE
        cpu.current_cycles = 12345
        cpu.interrupts.ime = True
        cpu.interrupts.halted = True

        state = cpu.save_state()
        cpu2 = CPU()
        cpu2.load_state(state)

        self.assertEqual(cpu2.registers.AF, 0x01B0)
        self.assertEqual(cpu2.registers.BC, 0x0013)
        self.assertEqual(cpu2.registers.PC, 0x0100)
        self.assertEqual(cpu2.registers.SP, 0xFFFE)
        self.assertEqual(cpu2.current_cycles, 12345)
        self.assertTrue(cpu2.interrupts.ime)
        self.assertTrue(cpu2.interrupts.halted)

    def test_operand_values_cleared(self):
        cpu = CPU()
        cpu.operand_values = [1, 2, 3]
        state = cpu.save_state()
        cpu2 = CPU()
        cpu2.load_state(state)
        self.assertEqual(cpu2.operand_values, [])


class TestGameBoySaveState(unittest.TestCase):
    def test_round_trip(self):
        gb = GameBoy()
        gb.init_post_boot_state()

        # Modify some state
        gb.cpu.set_register('A', 0x42)
        gb.memory.memory[0xC000] = 0x99
        gb.timer.write(0xFF06, 0x55)

        state = gb.save_state()
        self.assertEqual(state['version'], 1)

        # Create fresh GameBoy and load state
        gb2 = GameBoy()
        gb2.load_state(state)

        self.assertEqual(gb2.cpu.registers.AF & 0xFF00, 0x4200)
        self.assertEqual(gb2.memory.memory[0xC000], 0x99)
        self.assertEqual(gb2.timer._tma, 0x55)

    def test_version_mismatch(self):
        gb = GameBoy()
        state = gb.save_state()
        state['version'] = 999
        gb2 = GameBoy()
        with self.assertRaises(ValueError):
            gb2.load_state(state)

    def test_pickle_round_trip(self):
        gb = GameBoy()
        gb.init_post_boot_state()

        state = gb.save_state()
        data = pickle.dumps(state)
        loaded = pickle.loads(data)

        gb2 = GameBoy()
        gb2.load_state(loaded)
        self.assertEqual(gb2.cpu.registers.PC, 0x0100)

    def test_save_load_preserves_execution(self):
        """Save state, run more cycles, load state, verify state matches save point."""
        gb = GameBoy()
        gb.init_post_boot_state()
        # Write a simple program: NOP slide
        for i in range(16):
            gb.memory.memory[0x0100 + i] = 0x00  # NOP
        gb.run(max_cycles=20)

        state = gb.save_state()
        saved_pc = gb.cpu.registers.PC
        saved_cycles = gb.cpu.current_cycles

        # Run more cycles
        gb.run(max_cycles=gb.cpu.current_cycles + 100)
        self.assertNotEqual(gb.cpu.registers.PC, saved_pc)

        # Load state and verify we're back at the save point
        gb.load_state(state)
        self.assertEqual(gb.cpu.registers.PC, saved_pc)
        self.assertEqual(gb.cpu.current_cycles, saved_cycles)

    def test_no_cartridge(self):
        gb = GameBoy()
        state = gb.save_state()
        self.assertIsNone(state['cartridge'])
        gb2 = GameBoy()
        gb2.load_state(state)  # should not raise


if __name__ == '__main__':
    unittest.main()
