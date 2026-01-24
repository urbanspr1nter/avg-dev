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

if __name__ == '__main__':
    unittest.main()
