import unittest
from src.cpu.gb_cpu import CPU
from src.memory.gb_memory import Memory


class TestFetchWithOperands(unittest.TestCase):
    def setUp(self):
        self.cpu = CPU()

    def test_run_opcode_with_1byte_operand(self):
        """Test running instruction with 1-byte operand (LD B, n8 = 0x06, 8 cycles)"""
        self.cpu.memory.set_value(0x0000, 0x06)  # LD B, n8
        self.cpu.memory.set_value(0x0001, 0x42)  # n8 = 0x42
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 2: opcode (1) + operand (1)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 8)

    def test_run_opcode_with_2byte_operand(self):
        """Test running instruction with 2-byte operand (LD BC, n16 = 0x01, 12 cycles)"""
        self.cpu.memory.set_value(0x0000, 0x01)  # LD BC, n16
        self.cpu.memory.set_value(0x0001, 0x34)  # n16 low byte
        self.cpu.memory.set_value(0x0002, 0x12)  # n16 high byte
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)

        # PC should advance by 3: opcode (1) + operand (2)
        self.assertEqual(self.cpu.registers.PC, 0x0003)
        self.assertEqual(self.cpu.current_cycles, 12)

    def test_run_multiple_opcodes_with_operands(self):
        """Test running multiple instructions with various operand sizes"""
        # LD B, n8 (2 bytes, 8 cycles)
        self.cpu.memory.set_value(0x0000, 0x06)
        self.cpu.memory.set_value(0x0001, 0xFF)
        # LD BC, n16 (3 bytes, 12 cycles)
        self.cpu.memory.set_value(0x0002, 0x01)
        self.cpu.memory.set_value(0x0003, 0xCD)
        self.cpu.memory.set_value(0x0004, 0xAB)
        # NOP (1 byte, 4 cycles)
        self.cpu.memory.set_value(0x0005, 0x00)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=24)  # 8 + 12 + 4 = 24 cycles

        # PC should advance by 6: 2 + 3 + 1
        self.assertEqual(self.cpu.registers.PC, 0x0006)
        self.assertEqual(self.cpu.current_cycles, 24)

    def test_run_mixed_with_and_without_operands(self):
        """Test mix of opcodes with operands, without operands, and CB-prefixed"""
        # NOP (1 byte, 4 cycles)
        self.cpu.memory.set_value(0x0000, 0x00)
        # LD C, n8 (2 bytes, 8 cycles)
        self.cpu.memory.set_value(0x0001, 0x0E)
        self.cpu.memory.set_value(0x0002, 0x55)
        # CB RLC B (2 bytes, 8 cycles)
        self.cpu.memory.set_value(0x0003, 0xCB)
        self.cpu.memory.set_value(0x0004, 0x00)
        # LD DE, n16 (3 bytes, 12 cycles)
        self.cpu.memory.set_value(0x0005, 0x11)
        self.cpu.memory.set_value(0x0006, 0x22)
        self.cpu.memory.set_value(0x0007, 0x11)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=32)  # 4 + 8 + 8 + 12 = 32 cycles

        # PC should advance by 8: 1 + 2 + 2 + 3
        self.assertEqual(self.cpu.registers.PC, 0x0008)
        self.assertEqual(self.cpu.current_cycles, 32)

    def test_run_ld_d_n8(self):
        """Test running LD D, n8 instruction (0x16, 8 cycles)"""
        # LD D, n8 (2 bytes, 8 cycles)
        self.cpu.memory.set_value(0x0000, 0x16)  # LD D, n8
        self.cpu.memory.set_value(0x0001, 0x42)  # n8 = 0x42
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 2: opcode (1) + operand (1)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 8)
        # Verify D register was loaded
        self.assertEqual(self.cpu.get_register("D"), 0x42)

    def test_run_ld_e_n8(self):
        """Test running LD E, n8 instruction (0x1E, 8 cycles)"""
        # LD E, n8 (2 bytes, 8 cycles)
        self.cpu.memory.set_value(0x0000, 0x1E)  # LD E, n8
        self.cpu.memory.set_value(0x0001, 0x7F)  # n8 = 0x7F
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 2: opcode (1) + operand (1)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 8)
        # Verify E register was loaded
        self.assertEqual(self.cpu.get_register("E"), 0x7F)

    def test_run_ld_h_n8(self):
        """Test running LD H, n8 instruction (0x26, 8 cycles)"""
        # LD H, n8 (2 bytes, 8 cycles)
        self.cpu.memory.set_value(0x0000, 0x26)  # LD H, n8
        self.cpu.memory.set_value(0x0001, 0xFF)  # n8 = 0xFF
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 2: opcode (1) + operand (1)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 8)
        # Verify H register was loaded
        self.assertEqual(self.cpu.get_register("H"), 0xFF)

    def test_run_ld_l_n8(self):
        """Test running LD L, n8 instruction (0x2E, 8 cycles)"""
        # LD L, n8 (2 bytes, 8 cycles)
        self.cpu.memory.set_value(0x0000, 0x2E)  # LD L, n8
        self.cpu.memory.set_value(0x0001, 0x7F)  # n8 = 0x7F
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 2: opcode (1) + operand (1)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 8)
        # Verify L register was loaded
        self.assertEqual(self.cpu.get_register("L"), 0x7F)

    def test_run_ld_a_n8(self):
        """Test running LD A, n8 instruction (0x3E, 8 cycles)"""
        # LD A, n8 (2 bytes, 8 cycles)
        self.cpu.memory.set_value(0x0000, 0x3E)  # LD A, n8
        self.cpu.memory.set_value(0x0001, 0x99)  # n8 = 0x99
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 2: opcode (1) + operand (1)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 8)
        # Verify A register was loaded
        self.assertEqual(self.cpu.get_register("A"), 0x99)

    def test_run_inc_b(self):
        """Test running INC B instruction (0x04, 4 cycles)"""
        # Set B to 0x7F initially
        self.cpu.set_register("B", 0x7F)

        # INC B (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x04)  # INC B
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify B was incremented
        self.assertEqual(self.cpu.get_register("B"), 0x80)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag("Z"))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag("N"))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag("H"))

    def test_run_inc_b_zero_flag(self):
        """Test running INC B instruction with Zero flag set (0x04, 4 cycles)"""
        # Set B to 0xFF which will wrap to 0x00 after increment
        self.cpu.set_register("B", 0xFF)

        # INC B (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x04)  # INC B
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify B was incremented and wrapped to 0
        self.assertEqual(self.cpu.get_register("B"), 0x00)
        # Verify Zero flag is set (result is zero)
        self.assertTrue(self.cpu.get_flag("Z"))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag("N"))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag("H"))

    def test_run_inc_c(self):
        """Test running INC C instruction (0x0C, 4 cycles)"""
        # Set C to 0x7F initially
        self.cpu.set_register("C", 0x7F)

        # INC C (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x0C)  # INC C
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify C was incremented
        self.assertEqual(self.cpu.get_register("C"), 0x80)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag("Z"))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag("N"))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag("H"))

    def test_run_inc_d(self):
        """Test running INC D instruction (0x14, 4 cycles)"""
        # Set D to 0x7F initially
        self.cpu.set_register("D", 0x7F)

        # INC D (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x14)  # INC D
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify D was incremented
        self.assertEqual(self.cpu.get_register("D"), 0x80)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag("Z"))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag("N"))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag("H"))

    def test_run_inc_e(self):
        """Test running INC E instruction (0x1C, 4 cycles)"""
        # Set E to 0x7F initially
        self.cpu.set_register("E", 0x7F)

        # INC E (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x1C)  # INC E
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify E was incremented
        self.assertEqual(self.cpu.get_register("E"), 0x80)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag("Z"))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag("N"))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag("H"))

    def test_run_inc_h(self):
        """Test running INC H instruction (0x24, 4 cycles)"""
        # Set H to 0x7F initially
        self.cpu.set_register("H", 0x7F)

        # INC H (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x24)  # INC H
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify H was incremented
        self.assertEqual(self.cpu.get_register("H"), 0x80)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag("Z"))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag("N"))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag("H"))

    def test_run_inc_h_zero_flag(self):
        """Test running INC H instruction with Zero flag set (0x24, 4 cycles)"""
        # Set H to 0xFF which will wrap to 0x00 after increment
        self.cpu.set_register("H", 0xFF)

        # INC H (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x24)  # INC H
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify H was incremented and wrapped to 0
        self.assertEqual(self.cpu.get_register("H"), 0x00)
        # Verify Zero flag is set (result is zero)
        self.assertTrue(self.cpu.get_flag("Z"))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag("N"))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag("H"))

    def test_run_inc_l(self):
        """Test running INC L instruction (0x2C, 4 cycles)"""
        # Set L to 0x7F initially
        self.cpu.set_register("L", 0x7F)

        # INC L (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x2C)  # INC L
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify L was incremented
        self.assertEqual(self.cpu.get_register("L"), 0x80)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag("Z"))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag("N"))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag("H"))

    def test_run_inc_a(self):
        """Test running INC A instruction (0x3C, 4 cycles)"""
        # Set A to 0x7F initially
        self.cpu.set_register("A", 0x7F)

        # INC A (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x3C)  # INC A
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify A was incremented
        self.assertEqual(self.cpu.get_register("A"), 0x80)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag("Z"))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag("N"))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag("H"))

    def test_run_inc_l_zero_flag(self):
        """Test running INC L instruction with Zero flag set (0x2C, 4 cycles)"""
        # Set L to 0xFF which will wrap to 0x00 after increment
        self.cpu.set_register("L", 0xFF)

        # INC L (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x2C)  # INC L
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify L was incremented and wrapped to 0
        self.assertEqual(self.cpu.get_register("L"), 0x00)
        # Verify Zero flag is set (result is zero)
        self.assertTrue(self.cpu.get_flag("Z"))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag("N"))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag("H"))

    def test_run_inc_a_zero_flag(self):
        """Test running INC A instruction with Zero flag set (0x3C, 4 cycles)"""
        # Set A to 0xFF which will wrap to 0x00 after increment
        self.cpu.set_register("A", 0xFF)

        # INC A (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x3C)  # INC A
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify A was incremented and wrapped to 0
        self.assertEqual(self.cpu.get_register("A"), 0x00)
        # Verify Zero flag is set (result is zero)
        self.assertTrue(self.cpu.get_flag("Z"))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag("N"))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag("H"))

    def test_run_dec_b(self):
        """Test running DEC B instruction (0x05, 4 cycles)"""
        # Set B to 0x80 initially
        self.cpu.set_register("B", 0x80)

        # DEC B (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x05)  # DEC B
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify B was decremented
        self.assertEqual(self.cpu.get_register("B"), 0x7F)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag("Z"))
        # Verify Negative flag is set (always 1 for DEC)
        self.assertTrue(self.cpu.get_flag("N"))
        # Verify Half-carry flag is set (borrow from bit 4: 0x8 -> 0x7)
        self.assertTrue(self.cpu.get_flag("H"))

    def test_run_dec_c(self):
        """Test running DEC C instruction (0x0D, 4 cycles)"""
        # Set C to 0x80 initially
        self.cpu.set_register("C", 0x80)

        # DEC C (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x0D)  # DEC C
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify C was decremented
        self.assertEqual(self.cpu.get_register("C"), 0x7F)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag("Z"))
        # Verify Negative flag is set (always 1 for DEC)
        self.assertTrue(self.cpu.get_flag("N"))
        # Verify Half-carry flag is set (borrow from bit 4: 0x8 -> 0x7)
        self.assertTrue(self.cpu.get_flag("H"))

    def test_run_dec_d(self):
        """Test running DEC D instruction (0x15, 4 cycles)"""
        # Set D to 0x80 initially
        self.cpu.set_register("D", 0x80)

        # DEC D (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x15)  # DEC D
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify D was decremented
        self.assertEqual(self.cpu.get_register("D"), 0x7F)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag("Z"))
        # Verify Negative flag is set (always 1 for DEC)
        self.assertTrue(self.cpu.get_flag("N"))
        # Verify Half-carry flag is set (borrow from bit 4: 0x8 -> 0x7)
        self.assertTrue(self.cpu.get_flag("H"))

    def test_run_dec_e(self):
        """Test running DEC E instruction (0x1D, 4 cycles)"""
        # Set E to 0x80 initially
        self.cpu.set_register("E", 0x80)

        # DEC E (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x1D)  # DEC E
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify E was decremented
        self.assertEqual(self.cpu.get_register("E"), 0x7F)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag("Z"))
        # Verify Negative flag is set (always 1 for DEC)
        self.assertTrue(self.cpu.get_flag("N"))
        # Verify Half-carry flag is set (borrow from bit 4: 0x8 -> 0x7)
        self.assertTrue(self.cpu.get_flag("H"))

    def test_run_dec_h(self):
        """Test running DEC H instruction (0x25, 4 cycles)"""
        # Set H to 0x80 initially
        self.cpu.set_register("H", 0x80)

        # DEC H (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x25)  # DEC H
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify H was decremented
        self.assertEqual(self.cpu.get_register("H"), 0x7F)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag("Z"))
        # Verify Negative flag is set (always 1 for DEC)
        self.assertTrue(self.cpu.get_flag("N"))
        # Verify Half-carry flag is set (borrow from bit 4: 0x8 -> 0x7)
        self.assertTrue(self.cpu.get_flag("H"))

    def test_run_dec_l(self):
        """Test running DEC L instruction (0x2D, 4 cycles)"""
        # Set L to 0x80 initially
        self.cpu.set_register("L", 0x80)

        # DEC L (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x2D)  # DEC L
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify L was decremented
        self.assertEqual(self.cpu.get_register("L"), 0x7F)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag("Z"))
        # Verify Negative flag is set (always 1 for DEC)
        self.assertTrue(self.cpu.get_flag("N"))
        # Verify Half-carry flag is set (borrow from bit 4: 0x8 -> 0x7)
        self.assertTrue(self.cpu.get_flag("H"))

    def test_run_dec_a(self):
        """Test running DEC A instruction (0x3D, 4 cycles)"""
        # Set A to 0x80 initially
        self.cpu.set_register("A", 0x80)

        # DEC A (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x3D)  # DEC A
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify A was decremented
        self.assertEqual(self.cpu.get_register("A"), 0x7F)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag("Z"))
        # Verify Negative flag is set (always 1 for DEC)
        self.assertTrue(self.cpu.get_flag("N"))
        # Verify Half-carry flag is set (borrow from bit 4: 0x8 -> 0x7)
        self.assertTrue(self.cpu.get_flag("H"))

    def test_run_dec_a_zero_flag(self):
        """Test running DEC A instruction with Zero flag set (0x3D, 4 cycles)"""
        # Set A to 0x01 which will become 0x00 after decrement
        self.cpu.set_register("A", 0x01)

        # DEC A (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x3D)  # DEC A
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify A was decremented to zero
        self.assertEqual(self.cpu.get_register("A"), 0x00)
        # Verify Zero flag is set (result is zero)
        self.assertTrue(self.cpu.get_flag("Z"))
        # Verify Negative flag is set (always 1 for DEC)
        self.assertTrue(self.cpu.get_flag("N"))
        # Verify Half-carry flag is not set (no borrow from bit 4: 0x0 -> 0xF)
        self.assertFalse(self.cpu.get_flag("H"))

    def test_run_inc_bc(self):
        """Test running INC BC instruction (0x03, 8 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x03)  # INC BC
        # Set BC to 0x1234
        self.cpu.set_register("BC", 0x1234)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        # BC should be incremented to 0x1235
        self.assertEqual(self.cpu.get_register("BC"), 0x1235)

    def test_run_dec_bc(self):
        """Test running DEC BC instruction (0x0B, 8 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x0B)  # DEC BC
        # Set BC to 0x1234
        self.cpu.set_register("BC", 0x1234)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        # BC should be decremented to 0x1233
        self.assertEqual(self.cpu.get_register("BC"), 0x1233)

    def test_run_inc_de(self):
        """Test running INC DE instruction (0x13, 8 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x13)  # INC DE
        # Set DE to 0x5678
        self.cpu.set_register("DE", 0x5678)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        # DE should be incremented to 0x5679
        self.assertEqual(self.cpu.get_register("DE"), 0x5679)

    def test_run_dec_de(self):
        """Test running DEC DE instruction (0x1B, 8 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x1B)  # DEC DE
        # Set DE to 0x5678
        self.cpu.set_register("DE", 0x5678)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        # DE should be decremented to 0x5677
        self.assertEqual(self.cpu.get_register("DE"), 0x5677)

    def test_run_inc_hl(self):
        """Test running INC HL instruction (0x23, 8 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x23)  # INC HL
        # Set HL to 0xABCD
        self.cpu.set_register("HL", 0xABCD)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        # HL should be incremented to 0xABCE
        self.assertEqual(self.cpu.get_register("HL"), 0xABCE)

    def test_run_dec_hl(self):
        """Test running DEC HL instruction (0x2B, 8 cycles)"""
        # Set DEC HL opcode at address 0
        self.cpu.memory.set_value(0x0000, 0x2B)  # DEC HL
        # Set HL to 0x9ABC
        self.cpu.set_register("HL", 0x9ABC)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        # HL should be decremented to 0x9ABB
        self.assertEqual(self.cpu.get_register("HL"), 0x9ABB)

    def test_run_ld_hl_n8(self):
        """Test running LD (HL), n8 instruction (0x36, 12 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x36)  # LD (HL), n8
        # Set operand value to 0x7F
        self.cpu.memory.set_value(0x0001, 0x7F)
        # Set HL to point to address 0xC000
        self.cpu.set_register("HL", 0xC000)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)

        # PC should advance by 2: opcode (1) + operand (1)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 12)
        # Memory at address 0xC000 should contain 0x7F
        self.assertEqual(self.cpu.memory.get_value(0xC000), 0x7F)

    def test_run_inc_sp(self):
        """Test running INC SP instruction (0x33, 8 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x33)  # INC SP
        # Set SP to 0xABCD
        self.cpu.registers.SP = 0xABCD
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        # SP should be incremented to 0xABCE
        self.assertEqual(self.cpu.get_register("SP"), 0xABCE)

    def test_run_dec_sp(self):
        """Test running DEC SP instruction (0x3B, 8 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x3B)  # DEC SP
        # Set SP to 0x9ABC
        self.cpu.registers.SP = 0x9ABC
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        # SP should be decremented to 0x9ABB
        self.assertEqual(self.cpu.get_register("SP"), 0x9ABB)

    def test_run_inc_hl_indirect(self):
        """Test running INC (HL) instruction (0x34, 12 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x34)  # INC (HL)
        # Set HL to point to address 0xC000
        self.cpu.set_register("HL", 0xC000)
        # Set memory at 0xC000 to 0x7F
        self.cpu.memory.set_value(0xC000, 0x7F)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 12)
        # Memory at address 0xC000 should be incremented to 0x80
        self.assertEqual(self.cpu.memory.get_value(0xC000), 0x80)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag("Z"))
        # Verify Negative flag is not set (always 0 for INC)
        self.assertFalse(self.cpu.get_flag("N"))

    def test_run_inc_hl_indirect_zero_flag(self):
        """Test running INC (HL) instruction with Zero flag set (0x34, 12 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x34)  # INC (HL)
        # Set HL to point to address 0xC000
        self.cpu.set_register("HL", 0xC000)
        # Set memory at 0xC000 to 0xFF which will become 0x00 after increment
        self.cpu.memory.set_value(0xC000, 0xFF)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 12)
        # Memory at address 0xC000 should be incremented to 0x00
        self.assertEqual(self.cpu.memory.get_value(0xC000), 0x00)
        # Verify Zero flag is set (result is zero)
        self.assertTrue(self.cpu.get_flag("Z"))

    def test_run_dec_hl_indirect(self):
        """Test running DEC (HL) instruction (0x35, 12 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x35)  # DEC (HL)
        # Set HL to point to address 0xC000
        self.cpu.set_register("HL", 0xC000)
        # Set memory at 0xC000 to 0x80
        self.cpu.memory.set_value(0xC000, 0x80)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 12)
        # Memory at address 0xC000 should be decremented to 0x7F
        self.assertEqual(self.cpu.memory.get_value(0xC000), 0x7F)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag("Z"))
        # Verify Negative flag is set (always 1 for DEC)
        self.assertTrue(self.cpu.get_flag("N"))

    def test_run_dec_hl_indirect_zero_flag(self):
        """Test running DEC (HL) instruction with Zero flag set (0x35, 12 cycles)"""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x35)  # DEC (HL)
        # Set HL to point to address 0xC000
        self.cpu.set_register("HL", 0xC000)
        # Set memory at 0xC000 to 0x01 which will become 0x00 after decrement
        self.cpu.memory.set_value(0xC000, 0x01)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)

        # PC should advance by 1 (no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 12)
        # Memory at address 0xC000 should be decremented to 0x00
        self.assertEqual(self.cpu.memory.get_value(0xC000), 0x00)
        # Verify Zero flag is set (result is zero)
        self.assertTrue(self.cpu.get_flag("Z"))


if __name__ == "__main__":
    unittest.main()
