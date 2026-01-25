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
        self.assertEqual(self.cpu.get_register('D'), 0x42)

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
        self.assertEqual(self.cpu.get_register('E'), 0x7F)
    
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
        self.assertEqual(self.cpu.get_register('H'), 0xFF)

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
        self.assertEqual(self.cpu.get_register('L'), 0x7F)

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
        self.assertEqual(self.cpu.get_register('A'), 0x99)

    def test_run_inc_b(self):
        """Test running INC B instruction (0x04, 4 cycles)"""
        # Set B to 0x7F initially
        self.cpu.set_register('B', 0x7F)
        
        # INC B (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x04)  # INC B
        self.cpu.registers.PC = 0x0000
        
        self.cpu.run(max_cycles=4)
        
        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify B was incremented
        self.assertEqual(self.cpu.get_register('B'), 0x80)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag('Z'))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag('N'))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag('H'))

    def test_run_inc_b_zero_flag(self):
        """Test running INC B instruction with Zero flag set (0x04, 4 cycles)"""
        # Set B to 0xFF which will wrap to 0x00 after increment
        self.cpu.set_register('B', 0xFF)
        
        # INC B (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x04)  # INC B
        self.cpu.registers.PC = 0x0000
        
        self.cpu.run(max_cycles=4)
        
        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify B was incremented and wrapped to 0
        self.assertEqual(self.cpu.get_register('B'), 0x00)
        # Verify Zero flag is set (result is zero)
        self.assertTrue(self.cpu.get_flag('Z'))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag('N'))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag('H'))

    def test_run_inc_c(self):
        """Test running INC C instruction (0x0C, 4 cycles)"""
        # Set C to 0x7F initially
        self.cpu.set_register('C', 0x7F)
        
        # INC C (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x0C)  # INC C
        self.cpu.registers.PC = 0x0000
        
        self.cpu.run(max_cycles=4)
        
        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify C was incremented
        self.assertEqual(self.cpu.get_register('C'), 0x80)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag('Z'))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag('N'))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag('H'))

    def test_run_inc_d(self):
        """Test running INC D instruction (0x14, 4 cycles)"""
        # Set D to 0x7F initially
        self.cpu.set_register('D', 0x7F)
        
        # INC D (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x14)  # INC D
        self.cpu.registers.PC = 0x0000
        
        self.cpu.run(max_cycles=4)
        
        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify D was incremented
        self.assertEqual(self.cpu.get_register('D'), 0x80)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag('Z'))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag('N'))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag('H'))

    def test_run_inc_e(self):
        """Test running INC E instruction (0x1C, 4 cycles)"""
        # Set E to 0x7F initially
        self.cpu.set_register('E', 0x7F)
        
        # INC E (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x1C)  # INC E
        self.cpu.registers.PC = 0x0000
        
        self.cpu.run(max_cycles=4)
        
        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify E was incremented
        self.assertEqual(self.cpu.get_register('E'), 0x80)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag('Z'))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag('N'))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag('H'))

    def test_run_inc_h(self):
        """Test running INC H instruction (0x24, 4 cycles)"""
        # Set H to 0x7F initially
        self.cpu.set_register('H', 0x7F)
        
        # INC H (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x24)  # INC H
        self.cpu.registers.PC = 0x0000
        
        self.cpu.run(max_cycles=4)
        
        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify H was incremented
        self.assertEqual(self.cpu.get_register('H'), 0x80)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag('Z'))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag('N'))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag('H'))

    def test_run_inc_h_zero_flag(self):
        """Test running INC H instruction with Zero flag set (0x24, 4 cycles)"""
        # Set H to 0xFF which will wrap to 0x00 after increment
        self.cpu.set_register('H', 0xFF)
        
        # INC H (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x24)  # INC H
        self.cpu.registers.PC = 0x0000
        
        self.cpu.run(max_cycles=4)
        
        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify H was incremented and wrapped to 0
        self.assertEqual(self.cpu.get_register('H'), 0x00)
        # Verify Zero flag is set (result is zero)
        self.assertTrue(self.cpu.get_flag('Z'))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag('N'))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag('H'))

    def test_run_inc_l(self):
        """Test running INC L instruction (0x2C, 4 cycles)"""
        # Set L to 0x7F initially
        self.cpu.set_register('L', 0x7F)
        
        # INC L (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x2C)  # INC L
        self.cpu.registers.PC = 0x0000
        
        self.cpu.run(max_cycles=4)
        
        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify L was incremented
        self.assertEqual(self.cpu.get_register('L'), 0x80)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag('Z'))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag('N'))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag('H'))

    def test_run_inc_a(self):
        """Test running INC A instruction (0x3C, 4 cycles)"""
        # Set A to 0x7F initially
        self.cpu.set_register('A', 0x7F)
        
        # INC A (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x3C)  # INC A
        self.cpu.registers.PC = 0x0000
        
        self.cpu.run(max_cycles=4)
        
        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify A was incremented
        self.assertEqual(self.cpu.get_register('A'), 0x80)
        # Verify Zero flag is not set (result is not zero)
        self.assertFalse(self.cpu.get_flag('Z'))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag('N'))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag('H'))

    def test_run_inc_l_zero_flag(self):
        """Test running INC L instruction with Zero flag set (0x2C, 4 cycles)"""
        # Set L to 0xFF which will wrap to 0x00 after increment
        self.cpu.set_register('L', 0xFF)
        
        # INC L (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x2C)  # INC L
        self.cpu.registers.PC = 0x0000
        
        self.cpu.run(max_cycles=4)
        
        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify L was incremented and wrapped to 0
        self.assertEqual(self.cpu.get_register('L'), 0x00)
        # Verify Zero flag is set (result is zero)
        self.assertTrue(self.cpu.get_flag('Z'))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag('N'))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag('H'))

    def test_run_inc_a_zero_flag(self):
        """Test running INC A instruction with Zero flag set (0x3C, 4 cycles)"""
        # Set A to 0xFF which will wrap to 0x00 after increment
        self.cpu.set_register('A', 0xFF)
        
        # INC A (1 byte opcode, no operands in instruction stream)
        self.cpu.memory.set_value(0x0000, 0x3C)  # INC A
        self.cpu.registers.PC = 0x0000
        
        self.cpu.run(max_cycles=4)
        
        # PC should advance by 1 (opcode only)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        # Verify A was incremented and wrapped to 0
        self.assertEqual(self.cpu.get_register('A'), 0x00)
        # Verify Zero flag is set (result is zero)
        self.assertTrue(self.cpu.get_flag('Z'))
        # Verify Negative flag is clear (always 0 for INC)
        self.assertFalse(self.cpu.get_flag('N'))
        # Verify Half-carry flag is set (overflow from bit 3 to 4: 0xF -> 0x10)
        self.assertTrue(self.cpu.get_flag('H'))

if __name__ == '__main__':
    unittest.main()
