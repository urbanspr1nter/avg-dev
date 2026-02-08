"""
Test cases for rotation and shift operations on register A.

Tests cover:
- RLC (Rotate Left through Carry)
- RRC (Rotate Right through Carry)
- RL (Rotate Left)
- RR (Rotate Right)
"""

import unittest
from src.cpu.gb_cpu import CPU


class TestRotateOperations(unittest.TestCase):
    def setUp(self):
        """Set up a fresh CPU instance for each test."""
        self.cpu = CPU()

    def test_run_rlc_a_basic(self):
        """Test running RLC A instruction (0x07, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x07)  # RLC A
        self.cpu.registers.PC = 0x0000

        # Set A to 0b11001010 (0xCA)
        self.cpu.set_register("A", 0xCA)

        self.cpu.run(max_cycles=4)

        # PC should advance by 1: opcode only
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)

        # RLC A: rotate left through carry
        # 0b11001010 -> 0b10010101 (bit 7 moves to bit 0)
        self.assertEqual(self.cpu.get_register("A"), 0x95)

        # Flags: Z=0, N=0, H=0, C=1 (old bit 7 was 1)
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))
        self.assertFalse(self.cpu.get_flag("H"))
        self.assertTrue(self.cpu.get_flag("C"))

    def test_run_rlc_a_zero_result(self):
        """Test running RLC A with result that would be zero (0x07, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x07)  # RLC A
        self.cpu.registers.PC = 0x0000

        # Set A to 0b10000000 (0x80)
        self.cpu.set_register("A", 0x80)

        self.cpu.run(max_cycles=4)

        # PC should advance by 1: opcode only
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)

        # RLC A: rotate left through carry
        # 0b10000000 -> 0b00000001 (bit 7 moves to bit 0)
        self.assertEqual(self.cpu.get_register("A"), 0x01)

        # Flags: Z=0, N=0, H=0, C=1 (old bit 7 was 1)
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))
        self.assertFalse(self.cpu.get_flag("H"))
        self.assertTrue(self.cpu.get_flag("C"))

    def test_run_rlc_a_carry_zero(self):
        """Test running RLC A with carry flag resulting in 0 (0x07, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x07)  # RLC A
        self.cpu.registers.PC = 0x0000

        # Set A to 0b01000000 (0x40)
        self.cpu.set_register("A", 0x40)

        self.cpu.run(max_cycles=4)

        # PC should advance by 1: opcode only
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)

        # RLC A: rotate left through carry
        # 0b01000000 -> 0b10000000 (bit 7 moves to bit 0)
        self.assertEqual(self.cpu.get_register("A"), 0x80)

        # Flags: Z=0, N=0, H=0, C=0 (old bit 7 was 0)
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))
        self.assertFalse(self.cpu.get_flag("H"))
        self.assertFalse(self.cpu.get_flag("C"))

    def test_run_rrc_a_basic(self):
        """Test running RRC A instruction (0x0F, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x0F)  # RRC A
        self.cpu.registers.PC = 0x0000

        # Set A to 0b11001010 (0xCA)
        self.cpu.set_register("A", 0xCA)

        self.cpu.run(max_cycles=4)

        # PC should advance by 1: opcode only
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)

        # RRC A: rotate right through carry
        # 0b11001010 -> 0b01100101 (bit 0 moves to bit 7)
        self.assertEqual(self.cpu.get_register("A"), 0x65)

        # Flags: Z=0, N=0, H=0, C=0 (bit 0 of input was 0)
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))
        self.assertFalse(self.cpu.get_flag("H"))
        self.assertFalse(self.cpu.get_flag("C"))

    def test_run_rrc_a_carry_zero(self):
        """Test running RRC A with carry flag resulting in 0 (0x0F, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x0F)  # RRC A
        self.cpu.registers.PC = 0x0000

        # Set A to 0b11001011 (0xCB)
        self.cpu.set_register("A", 0xCB)

        self.cpu.run(max_cycles=4)

        # PC should advance by 1: opcode only
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)

        # RRC A: rotate right through carry
        # 0b11001011 -> 0b11100101 (bit 0 moves to bit 7)
        self.assertEqual(self.cpu.get_register("A"), 0xE5)

        # Flags: Z=0, N=0, H=0, C=1 (bit 0 of input was 1)
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))
        self.assertFalse(self.cpu.get_flag("H"))
        self.assertTrue(self.cpu.get_flag("C"))

    def test_run_rl_a_basic(self):
        """Test running RL A instruction (0x17, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x17)  # RL A
        self.cpu.registers.PC = 0x0000

        # Set A to 0b11001010 (0xCA)
        self.cpu.set_register("A", 0xCA)

        self.cpu.run(max_cycles=4)

        # PC should advance by 1: opcode only
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)

        # RL A: rotate left through carry (carry flag is initially 0)
        # 0b11001010 -> 0b10010100 (bit 7 moves to CF, old CF goes to bit 0)
        self.assertEqual(self.cpu.get_register("A"), 0x94)

        # Flags: Z=0, N=0, H=0, C=1 (old bit 7 was 1)
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))
        self.assertFalse(self.cpu.get_flag("H"))
        self.assertTrue(self.cpu.get_flag("C"))

    def test_run_rl_a_with_carry(self):
        """Test running RL A instruction with carry flag set (0x17, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x17)  # RL A
        self.cpu.registers.PC = 0x0000

        # Set A to 0b11001010 (0xCA)
        self.cpu.set_register("A", 0xCA)
        # Set carry flag to 1
        self.cpu.set_flag("C", True)

        self.cpu.run(max_cycles=4)

        # PC should advance by 1: opcode only
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)

        # RL A: rotate left through carry (carry flag is 1)
        # 0b11001010 -> 0b10010101 (bit 7 moves to CF, old CF goes to bit 0)
        self.assertEqual(self.cpu.get_register("A"), 0x95)

        # Flags: Z=0, N=0, H=0, C=1 (old bit 7 was 1)
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))
        self.assertFalse(self.cpu.get_flag("H"))
        self.assertTrue(self.cpu.get_flag("C"))

    def test_run_rr_a_basic(self):
        """Test running RR A instruction (0x1F, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x1F)  # RR A
        self.cpu.registers.PC = 0x0000

        # Set A to 0b11001001 (0xC9)
        self.cpu.set_register("A", 0xC9)

        self.cpu.run(max_cycles=4)

        # PC should advance by 1: opcode only
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)

        # RR A: rotate right through carry (carry flag is initially 0)
        # 0b11001001 -> 0b01100100 (bit 0 moves to CF, old CF goes to bit 7)
        self.assertEqual(self.cpu.get_register("A"), 0x64)

        # Flags: Z=0, N=0, H=0, C=0 (bit 0 of input was 0)
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))
        self.assertFalse(self.cpu.get_flag("H"))
        self.assertTrue(self.cpu.get_flag("C"))

    def test_run_rr_a_with_carry(self):
        """Test running RR A instruction with carry flag set (0x1F, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x1F)  # RR A
        self.cpu.registers.PC = 0x0000

        # Set A to 0b11001010 (0xCA)
        self.cpu.set_register("A", 0xCA)
        # Set carry flag to 1
        self.cpu.set_flag("C", True)

        self.cpu.run(max_cycles=4)

        # PC should advance by 1: opcode only
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)

        # RR A: rotate right through carry (carry flag is 1)
        # 0b11001010 -> 0b11100101 (bit 0 moves to CF, old CF goes to bit 7)
        self.assertEqual(self.cpu.get_register("A"), 0xE5)

        # Flags: Z=0, N=0, H=0, C=0 (bit 0 of input was 0)
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))
        self.assertFalse(self.cpu.get_flag("H"))
        self.assertFalse(self.cpu.get_flag("C"))

    def test_run_rla_a_basic(self):
        """Test running RLA A instruction (0x27, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x27)  # RLA A
        self.cpu.registers.PC = 0x0000

        # Set A to 0b11001010 (0xCA)
        self.cpu.set_register("A", 0xCA)

        self.cpu.run(max_cycles=4)

        # PC should advance by 1: opcode only
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)

        # RLA A: rotate left through carry (carry flag is initially 0)
        # 0b11001010 -> 0b10010100 (bit 7 moves to CF, old CF goes to bit 0)
        self.assertEqual(self.cpu.get_register("A"), 0x94)

        # Flags: Z=0, N=0, H=0, C=1 (old bit 7 was 1)
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))
        self.assertFalse(self.cpu.get_flag("H"))
        self.assertTrue(self.cpu.get_flag("C"))

    def test_run_rla_a_with_carry(self):
        """Test running RLA A instruction with carry flag set (0x27, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x27)  # RLA A
        self.cpu.registers.PC = 0x0000

        # Set A to 0b11001010 (0xCA)
        self.cpu.set_register("A", 0xCA)
        # Set carry flag to 1
        self.cpu.set_flag("C", True)

        self.cpu.run(max_cycles=4)

        # PC should advance by 1: opcode only
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)

        # RLA A: rotate left through carry (carry flag is 1)
        # 0b11001010 -> 0b10010101 (bit 7 moves to CF, old CF goes to bit 0)
        self.assertEqual(self.cpu.get_register("A"), 0x95)

        # Flags: Z=0, N=0, H=0, C=1 (old bit 7 was 1)
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))
        self.assertFalse(self.cpu.get_flag("H"))
        self.assertTrue(self.cpu.get_flag("C"))

    def test_run_rla_a_carry_zero(self):
        """Test running RLA A with carry flag resulting in 0 (0x27, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x27)  # RLA A
        self.cpu.registers.PC = 0x0000

        # Set A to 0b01000000 (0x40)
        self.cpu.set_register("A", 0x40)

        self.cpu.run(max_cycles=4)

        # PC should advance by 1: opcode only
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)

        # RLA A: rotate left through carry (carry flag is initially 0)
        # 0b01000000 -> 0b10000000 (bit 7 moves to CF, old CF goes to bit 0)
        self.assertEqual(self.cpu.get_register("A"), 0x80)

        # Flags: Z=0, N=0, H=0, C=0 (old bit 7 was 0)
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))
        self.assertFalse(self.cpu.get_flag("H"))
        self.assertFalse(self.cpu.get_flag("C"))

    def test_run_rra_a_basic(self):
        """Test running RRA A instruction (0x2F, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x2F)  # RRA A
        self.cpu.registers.PC = 0x0000

        # Set A to 0b11001001 (0xC9)
        self.cpu.set_register("A", 0xC9)

        self.cpu.run(max_cycles=4)

        # PC should advance by 1: opcode only
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)

        # RRA A: rotate right through carry (carry flag is initially 0)
        # 0b11001001 -> 0b01100100 (bit 0 moves to CF, old CF goes to bit 7)
        self.assertEqual(self.cpu.get_register("A"), 0x64)

        # Flags: Z=0, N=0, H=0, C=1 (bit 0 of input was 1)
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))
        self.assertFalse(self.cpu.get_flag("H"))
        self.assertTrue(self.cpu.get_flag("C"))

    def test_run_rra_a_with_carry(self):
        """Test running RRA A instruction with carry flag set (0x2F, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x2F)  # RRA A
        self.cpu.registers.PC = 0x0000

        # Set A to 0b11001010 (0xCA)
        self.cpu.set_register("A", 0xCA)
        # Set carry flag to 1
        self.cpu.set_flag("C", True)

        self.cpu.run(max_cycles=4)

        # PC should advance by 1: opcode only
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)

        # RRA A: rotate right through carry (carry flag is 1)
        # 0b11001010 -> 0b11100101 (bit 0 moves to CF, old CF goes to bit 7)
        self.assertEqual(self.cpu.get_register("A"), 0xE5)

        # Flags: Z=0, N=0, H=0, C=0 (bit 0 of input was 0)
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))
        self.assertFalse(self.cpu.get_flag("H"))
        self.assertFalse(self.cpu.get_flag("C"))

    def test_run_rra_a_carry_zero(self):
        """Test running RRA A with carry flag resulting in 0 (0x2F, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x2F)  # RRA A
        self.cpu.registers.PC = 0x0000

        # Set A to 0b11001011 (0xCB)
        self.cpu.set_register("A", 0xCB)

        self.cpu.run(max_cycles=4)

        # PC should advance by 1: opcode only
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)

        # RRA A: rotate right through carry (carry flag is initially 0)
        # 0b11001011 -> 0b01100101 (bit 0 moves to CF, old CF goes to bit 7)
        self.assertEqual(self.cpu.get_register("A"), 0x65)

        # Flags: Z=0, N=0, H=0, C=1 (bit 0 of input was 1)
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))
        self.assertFalse(self.cpu.get_flag("H"))
        self.assertTrue(self.cpu.get_flag("C"))

    def test_run_multiple_rotate_instructions(self):
        """Test running multiple rotate instructions in sequence"""
        # Set opcodes at 0x0000-0x0003
        self.cpu.memory.set_value(0x0000, 0x07)  # RLC A
        self.cpu.memory.set_value(0x0001, 0x0F)  # RRC A
        self.cpu.memory.set_value(0x0002, 0x17)  # RL A
        self.cpu.memory.set_value(0x0003, 0x1F)  # RR A
        self.cpu.registers.PC = 0x0000

        # Set A to 0b00001111 (0x0F)
        self.cpu.set_register("A", 0x0F)

        self.cpu.run(max_cycles=16)  # 4 instructions * 4 cycles each

        # PC should advance by 4: opcode only
        self.assertEqual(self.cpu.registers.PC, 0x0004)
        self.assertEqual(self.cpu.current_cycles, 16)
