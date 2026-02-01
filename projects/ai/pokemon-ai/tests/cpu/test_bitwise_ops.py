"""
Test cases for bitwise operations (AND, OR, XOR, CP).

These tests verify the implementation of:
- AND A, xx instructions (0xA0-0xA7, 0xE6)
- OR A, xx instructions (0xB0-0xB7, 0xF6)
- XOR A, xx instructions (0xA8-0xAF, 0xEE)
- CP A, xx instructions (0xB8-0xBF, 0xFE)
"""

import unittest
from src.cpu.gb_cpu import CPU


class TestBitwiseOperations(unittest.TestCase):
    """Test bitwise operations on the Gameboy CPU."""

    def setUp(self):
        """Set up a fresh CPU instance for each test."""
        self.cpu = CPU()

    # AND A, xx tests (0xA0-0xA7, 0xE6)

    def test_run_and_a_b(self):
        """Test running AND A, B instruction (0xA0, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xA0)  # AND A, B
        # Set A to 0xFF and B to 0x55 (01010101)
        self.cpu.set_register("A", 0xFF)
        self.cpu.set_register("B", 0x55)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should be 0x55 (11111111 & 01010101 = 01010101)
        self.assertEqual(self.cpu.get_register("A"), 0x55)

    def test_run_and_a_c(self):
        """Test running AND A, C instruction (0xA1, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xA1)  # AND A, C
        # Set A to 0xFF and C to 0x33 (00110011)
        self.cpu.set_register("A", 0xFF)
        self.cpu.set_register("C", 0x33)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should be 0x33 (11111111 & 00110011 = 00110011)
        self.assertEqual(self.cpu.get_register("A"), 0x33)

    def test_run_and_a_d(self):
        """Test running AND A, D instruction (0xA2, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xA2)  # AND A, D
        # Set A to 0xFF and D to 0x7F (01111111)
        self.cpu.set_register("A", 0xFF)
        self.cpu.set_register("D", 0x7F)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should be 0x7F (11111111 & 01111111 = 01111111)
        self.assertEqual(self.cpu.get_register("A"), 0x7F)

    def test_run_and_a_e(self):
        """Test running AND A, E instruction (0xA3, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xA3)  # AND A, E
        # Set A to 0xFF and E to 0x55 (01010101)
        self.cpu.set_register("A", 0xFF)
        self.cpu.set_register("E", 0x55)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should be 0x55 (11111111 & 01010101 = 01010101)
        self.assertEqual(self.cpu.get_register("A"), 0x55)

    def test_run_and_a_h(self):
        """Test running AND A, H instruction (0xA4, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xA4)  # AND A, H
        # Set A to 0xFF and H to 0x77 (01110111)
        self.cpu.set_register("A", 0xFF)
        self.cpu.set_register("H", 0x77)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should be 0x77 (11111111 & 01110111 = 01110111)
        self.assertEqual(self.cpu.get_register("A"), 0x77)

    def test_run_and_a_l(self):
        """Test running AND A, L instruction (0xA5, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xA5)  # AND A, L
        # Set A to 0xFF and L to 0x88 (10001000)
        self.cpu.set_register("A", 0xFF)
        self.cpu.set_register("L", 0x88)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should be 0x88 (11111111 & 10001000 = 10001000)
        self.assertEqual(self.cpu.get_register("A"), 0x88)

    def test_run_and_a_hl(self):
        """Test running AND A, (HL) instruction (0xA6, 8 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xA6)  # AND A, (HL)
        # Set A to 0xFF
        self.cpu.set_register("A", 0xFF)
        # Set HL to point to address 0xC000 and set memory value to 0x33
        self.cpu.set_register("HL", 0xC000)
        self.cpu.memory.set_value(0xC000, 0x33)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        # A should be 0x33 (11111111 & 00110011 = 00110011)
        self.assertEqual(self.cpu.get_register("A"), 0x33)

    def test_run_and_a_a(self):
        """Test running AND A, A instruction (0xA7, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xA7)  # AND A, A
        # Set A to 0xFF
        self.cpu.set_register("A", 0xFF)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should remain 0xFF (11111111 & 11111111 = 11111111)
        self.assertEqual(self.cpu.get_register("A"), 0xFF)

    def test_run_and_a_n8(self):
        """Test running AND A, n8 instruction (0xE6, 8 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xE6)  # AND A, n8
        # Set operand value to 0x55
        self.cpu.memory.set_value(0x0001, 0x55)
        # Set A to 0xFF
        self.cpu.set_register("A", 0xFF)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 2: opcode (1) + operand (1)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 8)
        # A should be 0x55 (11111111 & 01010101 = 01010101)
        self.assertEqual(self.cpu.get_register("A"), 0x55)

    # OR A, xx tests (0xB0-0xB7, 0xF6)

    def test_run_or_a_b(self):
        """Test running OR A, B instruction (0xB0, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xB0)  # OR A, B
        # Set A to 0xFF and B to 0x55 (01010101)
        self.cpu.set_register("A", 0xFF)
        self.cpu.set_register("B", 0x55)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should remain 0xFF (11111111 | 01010101 = 11111111)
        self.assertEqual(self.cpu.get_register("A"), 0xFF)

    def test_run_or_a_c(self):
        """Test running OR A, C instruction (0xB1, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xB1)  # OR A, C
        # Set A to 0xFF and C to 0x33 (00110011)
        self.cpu.set_register("A", 0xFF)
        self.cpu.set_register("C", 0x33)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should remain 0xFF (11111111 | 00110011 = 11111111)
        self.assertEqual(self.cpu.get_register("A"), 0xFF)

    def test_run_or_a_d(self):
        """Test running OR A, D instruction (0xB2, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xB2)  # OR A, D
        # Set A to 0xFF and D to 0x7F (01111111)
        self.cpu.set_register("A", 0xFF)
        self.cpu.set_register("D", 0x7F)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should remain 0xFF (11111111 | 01111111 = 11111111)
        self.assertEqual(self.cpu.get_register("A"), 0xFF)

    def test_run_or_a_e(self):
        """Test running OR A, E instruction (0xB3, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xB3)  # OR A, E
        # Set A to 0xFF and E to 0x00
        self.cpu.set_register("A", 0xFF)
        self.cpu.set_register("E", 0x00)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should remain 0xFF (11111111 | 00000000 = 11111111)
        self.assertEqual(self.cpu.get_register("A"), 0xFF)

    def test_run_or_a_h(self):
        """Test running OR A, H instruction (0xB4, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xB4)  # OR A, H
        # Set A to 0xFF and H to 0x77 (01110111)
        self.cpu.set_register("A", 0xFF)
        self.cpu.set_register("H", 0x77)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should remain 0xFF (11111111 | 01110111 = 11111111)
        self.assertEqual(self.cpu.get_register("A"), 0xFF)

    def test_run_or_a_l(self):
        """Test running OR A, L instruction (0xB5, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xB5)  # OR A, L
        # Set A to 0xFF and L to 0x88 (10001000)
        self.cpu.set_register("A", 0xFF)
        self.cpu.set_register("L", 0x88)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should remain 0xFF (11111111 | 10001000 = 11111111)
        self.assertEqual(self.cpu.get_register("A"), 0xFF)

    def test_run_or_a_hl(self):
        """Test running OR A, (HL) instruction (0xB6, 8 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xB6)  # OR A, (HL)
        # Set A to 0xF0
        self.cpu.set_register("A", 0xF0)
        # Set HL to point to address 0xC000 and set memory value to 0x0F
        self.cpu.set_register("HL", 0xC000)
        self.cpu.memory.set_value(0xC000, 0x0F)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        # A should be 0xFF (11110000 | 00001111 = 11111111)
        self.assertEqual(self.cpu.get_register("A"), 0xFF)

    def test_run_or_a_a(self):
        """Test running OR A, A instruction (0xB7, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xB7)  # OR A, A
        # Set A to 0xFF
        self.cpu.set_register("A", 0xFF)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should remain 0xFF (11111111 | 11111111 = 11111111)
        self.assertEqual(self.cpu.get_register("A"), 0xFF)

    def test_run_or_a_n8(self):
        """Test running OR A, n8 instruction (0xF6, 8 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xF6)  # OR A, n8
        # Set operand value to 0x55
        self.cpu.memory.set_value(0x0001, 0x55)
        # Set A to 0xAA
        self.cpu.set_register("A", 0xAA)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 2: opcode (1) + operand (1)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 8)
        # A should be 0xFF (10101010 | 01010101 = 11111111)
        self.assertEqual(self.cpu.get_register("A"), 0xFF)

    # XOR A, xx tests (0xA8-0xAF, 0xEE)

    def test_run_xor_a_b(self):
        """Test running XOR A, B instruction (0xA8, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xA8)  # XOR A, B
        # Set A to 0xFF and B to 0x55 (01010101)
        self.cpu.set_register("A", 0xFF)
        self.cpu.set_register("B", 0x55)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should be 0xAA (11111111 ^ 01010101 = 10101010)
        self.assertEqual(self.cpu.get_register("A"), 0xAA)

    def test_run_xor_a_c(self):
        """Test running XOR A, C instruction (0xA9, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xA9)  # XOR A, C
        # Set A to 0xAA and C to 0x33 (00110011)
        self.cpu.set_register("A", 0xAA)
        self.cpu.set_register("C", 0x33)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should be 0x99 (10101010 ^ 00110011 = 10011001)
        self.assertEqual(self.cpu.get_register("A"), 0x99)

    def test_run_xor_a_d(self):
        """Test running XOR A, D instruction (0xAA, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xAA)  # XOR A, D
        # Set A to 0x7F and D to 0x80 (10000000)
        self.cpu.set_register("A", 0x7F)
        self.cpu.set_register("D", 0x80)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should be 0xFF (01111111 ^ 10000000 = 11111111)
        self.assertEqual(self.cpu.get_register("A"), 0xFF)

    def test_run_xor_a_e(self):
        """Test running XOR A, E instruction (0xAB, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xAB)  # XOR A, E
        # Set A to 0xFF and E to 0x55 (01010101)
        self.cpu.set_register("A", 0xFF)
        self.cpu.set_register("E", 0x55)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should be 0xAA (11111111 ^ 01010101 = 10101010)
        self.assertEqual(self.cpu.get_register("A"), 0xAA)

    def test_run_xor_a_h(self):
        """Test running XOR A, H instruction (0xAC, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xAC)  # XOR A, H
        # Set A to 0xFF and H to 0x77 (01110111)
        self.cpu.set_register("A", 0xFF)
        self.cpu.set_register("H", 0x77)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should be 0x88 (11111111 ^ 01110111 = 10001000)
        self.assertEqual(self.cpu.get_register("A"), 0x88)

    def test_run_xor_a_l(self):
        """Test running XOR A, L instruction (0xAD, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xAD)  # XOR A, L
        # Set A to 0xFF and L to 0x88 (10001000)
        self.cpu.set_register("A", 0xFF)
        self.cpu.set_register("L", 0x88)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should be 0x77 (11111111 ^ 10001000 = 01110111)
        self.assertEqual(self.cpu.get_register("A"), 0x77)

    def test_run_xor_a_hl(self):
        """Test running XOR A, (HL) instruction (0xAE, 8 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xAE)  # XOR A, (HL)
        # Set A to 0xFF
        self.cpu.set_register("A", 0xFF)
        # Set HL to point to address 0xC000 and set memory value to 0x33
        self.cpu.set_register("HL", 0xC000)
        self.cpu.memory.set_value(0xC000, 0x33)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        # A should be 0xCC (11111111 ^ 00110011 = 11001100)
        self.assertEqual(self.cpu.get_register("A"), 0xCC)

    def test_run_xor_a_a(self):
        """Test running XOR A, A instruction (0xAF, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xAF)  # XOR A, A
        # Set A to 0xFF
        self.cpu.set_register("A", 0xFF)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should be 0x00 (11111111 ^ 11111111 = 00000000)
        self.assertEqual(self.cpu.get_register("A"), 0x00)

    def test_run_xor_a_n8(self):
        """Test running XOR A, n8 instruction (0xEE, 8 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xEE)  # XOR A, n8
        # Set operand value to 0x55
        self.cpu.memory.set_value(0x0001, 0x55)
        # Set A to 0xFF
        self.cpu.set_register("A", 0xFF)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 2: opcode (1) + operand (1)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 8)
        # A should be 0xAA (11111111 ^ 01010101 = 10101010)
        self.assertEqual(self.cpu.get_register("A"), 0xAA)

    # CP A, xx tests (0xB8-0xBF, 0xFE)

    def test_run_cp_a_b(self):
        """Test running CP A, B instruction (0xB8, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xB8)  # CP A, B
        # Set A to 0x10 and B to 0x20 (A > B)
        self.cpu.set_register("A", 0x10)
        self.cpu.set_register("B", 0x20)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should remain unchanged
        self.assertEqual(self.cpu.get_register("A"), 0x10)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag("Z"))
        # Verify Negative flag is set (always 1 for CP)
        self.assertTrue(self.cpu.get_flag("N"))
        # Verify Carry flag is set (borrow occurred: A < B)
        self.assertTrue(self.cpu.get_flag("C"))

    def test_run_cp_a_b_equal(self):
        """Test running CP A, B instruction with equal values (0xB8, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xB8)  # CP A, B
        # Set A to 0x30 and B to 0x30 (A == B)
        self.cpu.set_register("A", 0x30)
        self.cpu.set_register("B", 0x30)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should remain unchanged
        self.assertEqual(self.cpu.get_register("A"), 0x30)
        # Verify Zero flag is set (result is zero: A - B = 0)
        self.assertTrue(self.cpu.get_flag("Z"))
        # Verify Negative flag is set (always 1 for CP)
        self.assertTrue(self.cpu.get_flag("N"))
        # Verify Carry flag is not set (no borrow when equal)
        self.assertFalse(self.cpu.get_flag("C"))

    def test_run_cp_a_c(self):
        """Test running CP A, C instruction (0xB9, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xB9)  # CP A, C
        # Set A to 0x50 and C to 0x30 (A > B)
        self.cpu.set_register("A", 0x50)
        self.cpu.set_register("C", 0x30)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should remain unchanged
        self.assertEqual(self.cpu.get_register("A"), 0x50)
        # Verify Carry flag is not set (no borrow: A > B)
        self.assertFalse(self.cpu.get_flag("C"))

    def test_run_cp_a_d(self):
        """Test running CP A, D instruction (0xBA, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xBA)  # CP A, D
        # Set A to 0x25 and D to 0x30 (A < B)
        self.cpu.set_register("A", 0x25)
        self.cpu.set_register("D", 0x30)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should remain unchanged
        self.assertEqual(self.cpu.get_register("A"), 0x25)
        # Verify Carry flag is set (borrow occurred: A < B)
        self.assertTrue(self.cpu.get_flag("C"))

    def test_run_cp_a_e(self):
        """Test running CP A, E instruction (0xBB, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xBB)  # CP A, E
        # Set A to 0x7F and E to 0x80 (A < B)
        self.cpu.set_register("A", 0x7F)
        self.cpu.set_register("E", 0x80)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should remain unchanged
        self.assertEqual(self.cpu.get_register("A"), 0x7F)
        # Verify Carry flag is set (borrow occurred: A < B)
        self.assertTrue(self.cpu.get_flag("C"))

    def test_run_cp_a_h(self):
        """Test running CP A, H instruction (0xBC, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xBC)  # CP A, H
        # Set A to 0xFF and H to 0x7F (A > B)
        self.cpu.set_register("A", 0xFF)
        self.cpu.set_register("H", 0x7F)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should remain unchanged
        self.assertEqual(self.cpu.get_register("A"), 0xFF)
        # Verify Carry flag is not set (no borrow: A > B)
        self.assertFalse(self.cpu.get_flag("C"))

    def test_run_cp_a_l(self):
        """Test running CP A, L instruction (0xBD, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xBD)  # CP A, L
        # Set A to 0x80 and L to 0xFF (A < B)
        self.cpu.set_register("A", 0x80)
        self.cpu.set_register("L", 0xFF)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should remain unchanged
        self.assertEqual(self.cpu.get_register("A"), 0x80)
        # Verify Carry flag is set (borrow occurred: A < B)
        self.assertTrue(self.cpu.get_flag("C"))

    def test_run_cp_a_hl(self):
        """Test running CP A, (HL) instruction (0xBE, 8 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xBE)  # CP A, (HL)
        # Set A to 0x55
        self.cpu.set_register("A", 0x55)
        # Set HL to point to address 0xC000 and set memory value to 0x30
        self.cpu.set_register("HL", 0xC000)
        self.cpu.memory.set_value(0xC000, 0x30)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        # A should remain unchanged
        self.assertEqual(self.cpu.get_register("A"), 0x55)
        # Verify Carry flag is not set (no borrow: A > memory)
        self.assertFalse(self.cpu.get_flag("C"))

    def test_run_cp_a_a(self):
        """Test running CP A, A instruction (0xBF, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xBF)  # CP A, A
        # Set A to 0xFF
        self.cpu.set_register("A", 0xFF)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should remain unchanged
        self.assertEqual(self.cpu.get_register("A"), 0xFF)
        # Verify Zero flag is set (result is zero: A - A = 0)
        self.assertTrue(self.cpu.get_flag("Z"))
        # Verify Negative flag is set (always 1 for CP)
        self.assertTrue(self.cpu.get_flag("N"))

    def test_run_cp_a_n8(self):
        """Test running CP A, n8 instruction (0xFE, 8 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xFE)  # CP A, n8
        # Set operand value to 0x30
        self.cpu.memory.set_value(0x0001, 0x30)
        # Set A to 0x50 (A > n8)
        self.cpu.set_register("A", 0x50)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 2: opcode (1) + operand (1)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 8)
        # A should remain unchanged
        self.assertEqual(self.cpu.get_register("A"), 0x50)
        # Verify Carry flag is not set (no borrow: A > n8)
        self.assertFalse(self.cpu.get_flag("C"))

    def test_run_cp_a_n8_less(self):
        """Test running CP A, n8 instruction with A < n8 (0xFE, 8 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xFE)  # CP A, n8
        # Set operand value to 0x50
        self.cpu.memory.set_value(0x0001, 0x50)
        # Set A to 0x30 (A < n8)
        self.cpu.set_register("A", 0x30)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 2: opcode (1) + operand (1)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 8)
        # A should remain unchanged
        self.assertEqual(self.cpu.get_register("A"), 0x30)
        # Verify Carry flag is set (borrow occurred: A < n8)
        self.assertTrue(self.cpu.get_flag("C"))
