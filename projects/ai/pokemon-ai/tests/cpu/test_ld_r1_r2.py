"""
Tests for LD r1, r2 instructions (0x40-0x7F).
These tests verify register-to-register and register-to-memory transfers.
"""

import unittest
from src.cpu.gb_cpu import CPU
from src.memory.gb_memory import Memory


class TestLdR1R2(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.memory = Memory()
        self.cpu = CPU(memory=self.memory)

    def test_run_ld_b_b(self):
        """Test running LD B, B instruction (0x40, 4 cycles) - no-op"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x40)  # LD B, B

        # Set B to a known value
        self.cpu.set_register("B", 0x12)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # B should remain unchanged
        self.assertEqual(self.cpu.get_register("B"), 0x12)

    def test_run_ld_b_c(self):
        """Test running LD B, C instruction (0x41, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x41)  # LD B, C

        # Set registers to known values
        self.cpu.set_register("B", 0x33)
        self.cpu.set_register("C", 0x7F)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # B should now contain C's value
        self.assertEqual(self.cpu.get_register("B"), 0x7F)

    def test_run_ld_b_d(self):
        """Test running LD B, D instruction (0x42, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x42)  # LD B, D

        # Set registers to known values
        self.cpu.set_register("B", 0x11)
        self.cpu.set_register("D", 0x80)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # B should now contain D's value
        self.assertEqual(self.cpu.get_register("B"), 0x80)

    def test_run_ld_b_e(self):
        """Test running LD B, E instruction (0x43, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x43)  # LD B, E

        # Set registers to known values
        self.cpu.set_register("B", 0x22)
        self.cpu.set_register("E", 0x99)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # B should now contain E's value
        self.assertEqual(self.cpu.get_register("B"), 0x99)

    def test_run_ld_b_h(self):
        """Test running LD B, H instruction (0x44, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x44)  # LD B, H

        # Set registers to known values
        self.cpu.set_register("B", 0x33)
        self.cpu.set_register("H", 0xAA)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # B should now contain H's value
        self.assertEqual(self.cpu.get_register("B"), 0xAA)

    def test_run_ld_b_l(self):
        """Test running LD B, L instruction (0x45, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x45)  # LD B, L

        # Set registers to known values
        self.cpu.set_register("B", 0x11)
        self.cpu.set_register("L", 0xBB)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # B should now contain L's value
        self.assertEqual(self.cpu.get_register("B"), 0xBB)

    def test_run_ld_b_hl(self):
        """Test running LD B, (HL) instruction (0x46, 8 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x46)  # LD B, (HL)

        # Set HL to point to address 0xC000
        self.cpu.set_register("HL", 0xC000)
        # Write value 0x55 to memory at 0xC000
        self.cpu.memory.set_value(0xC000, 0x55)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        # B should now contain the value from memory at HL
        self.assertEqual(self.cpu.get_register("B"), 0x55)

    def test_run_ld_b_a(self):
        """Test running LD B, A instruction (0x47, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x47)  # LD B, A

        # Set registers to known values
        self.cpu.set_register("B", 0x33)
        self.cpu.set_register("A", 0xCC)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # B should now contain A's value
        self.assertEqual(self.cpu.get_register("B"), 0xCC)

    def test_run_ld_c_b(self):
        """Test running LD C, B instruction (0x48, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x48)  # LD C, B

        # Set registers to known values
        self.cpu.set_register("C", 0x11)
        self.cpu.set_register("B", 0xDD)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # C should now contain B's value
        self.assertEqual(self.cpu.get_register("C"), 0xDD)

    def test_run_ld_d_b(self):
        """Test running LD D, B instruction (0x50, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x50)  # LD D, B

        # Set registers to known values
        self.cpu.set_register("D", 0x22)
        self.cpu.set_register("B", 0xEE)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # D should now contain B's value
        self.assertEqual(self.cpu.get_register("D"), 0xEE)

    def test_run_ld_e_b(self):
        """Test running LD E, B instruction (0x58, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x58)  # LD E, B

        # Set registers to known values
        self.cpu.set_register("E", 0x33)
        self.cpu.set_register("B", 0xFF)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # E should now contain B's value
        self.assertEqual(self.cpu.get_register("E"), 0xFF)

    def test_run_ld_h_b(self):
        """Test running LD H, B instruction (0x60, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x60)  # LD H, B

        # Set registers to known values
        self.cpu.set_register("H", 0x44)
        self.cpu.set_register("B", 0x12)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # H should now contain B's value
        self.assertEqual(self.cpu.get_register("H"), 0x12)

    def test_run_ld_l_b(self):
        """Test running LD L, B instruction (0x68, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x68)  # LD L, B

        # Set registers to known values
        self.cpu.set_register("L", 0x55)
        self.cpu.set_register("B", 0x77)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # L should now contain B's value
        self.assertEqual(self.cpu.get_register("L"), 0x77)

    def test_run_ld_hl_b(self):
        """Test running LD (HL), B instruction (0x70, 8 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x70)  # LD (HL), B

        # Set HL to point to address 0xD000
        self.cpu.set_register("HL", 0xD000)
        # Set B to a known value
        self.cpu.set_register("B", 0x34)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        # Memory at address HL should now contain B's value
        self.assertEqual(self.cpu.memory.get_value(0xD000), 0x34)

    def test_run_ld_a_b(self):
        """Test running LD A, B instruction (0x78, 4 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x78)  # LD A, B

        # Set registers to known values
        self.cpu.set_register("A", 0x11)
        self.cpu.set_register("B", 0x99)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # A should now contain B's value
        self.assertEqual(self.cpu.get_register("A"), 0x99)

    def test_run_multiple_ld_r1_r2_instructions(self):
        """Test running multiple LD r1, r2 instructions in sequence"""
        # Set opcodes at 0x0000-0x0005
        self.cpu.memory.set_value(0x0000, 0x48)  # LD C, B
        self.cpu.memory.set_value(0x0001, 0x79)  # LD A, C
        self.cpu.memory.set_value(0x0002, 0x60)  # LD H, B

        # Set registers to known values
        self.cpu.set_register("B", 0x12)
        self.cpu.set_register("C", 0x34)
        self.cpu.set_register("H", 0x56)
        self.cpu.registers.PC = 0x0000

        # Run for enough cycles to execute all instructions (3 * 4 = 12 cycles)
        self.cpu.run(max_cycles=12)

        # PC should advance by 3 (one opcode each)
        self.assertEqual(self.cpu.registers.PC, 0x0003)
        self.assertEqual(self.cpu.current_cycles, 12)

        # After LD C, B: C = 0x12
        # After LD A, C: A = 0x12 (from C)
        # After LD H, B: H = 0x12 (from B)
        self.assertEqual(self.cpu.get_register("C"), 0x12)
        self.assertEqual(self.cpu.get_register("A"), 0x12)
        self.assertEqual(self.cpu.get_register("H"), 0x12)


if __name__ == "__main__":
    unittest.main()
