import unittest
from src.cpu.gb_cpu import CPU
from src.memory.gb_memory import Memory

class TestFetch(unittest.TestCase):
    def setUp(self):
        self.cpu = CPU()
    
    def test_fetch_byte(self):
        """Test fetching a byte from memory"""
        self.cpu.memory.set_value(0x1000, 0xAB)
        result = self.cpu.fetch_byte(0x1000)
        self.assertEqual(result, 0xAB)
    
    def test_fetch_word(self):
        """Test fetching a word from memory (little-endian)"""
        self.cpu.memory.set_value(0x1000, 0xCD)  # Low byte
        self.cpu.memory.set_value(0x1001, 0xEF)  # High byte
        result = self.cpu.fetch_word(0x1000)
        self.assertEqual(result, 0xEFCD)
    
    def test_run_single_unprefixed_opcode(self):
        """Test running a single unprefixed instruction (NOP = 4 cycles)"""
        self.cpu.memory.set_value(0x0000, 0x00)  # NOP
        self.cpu.registers.PC = 0x0000
        
        self.cpu.run(max_cycles=4)
        
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
    
    def test_run_single_cbprefixed_opcode(self):
        """Test running a single CB-prefixed instruction (RLC B = 8 cycles)"""
        self.cpu.memory.set_value(0x0000, 0xCB)  # CB prefix
        self.cpu.memory.set_value(0x0001, 0x00)  # RLC B
        self.cpu.registers.PC = 0x0000
        
        self.cpu.run(max_cycles=8)
        
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 8)
    
    def test_run_mixed_opcodes(self):
        """Test running a mix of unprefixed and CB-prefixed instructions (NOP=4 + RLC=8 + NOP=4 = 16 cycles)"""
        self.cpu.memory.set_value(0x0000, 0x00)  # NOP
        self.cpu.memory.set_value(0x0001, 0xCB)  # CB prefix
        self.cpu.memory.set_value(0x0002, 0x00)  # RLC B
        self.cpu.memory.set_value(0x0003, 0x00)  # NOP
        self.cpu.registers.PC = 0x0000
        
        self.cpu.run(max_cycles=16)
        
        self.assertEqual(self.cpu.registers.PC, 0x0004)
        self.assertEqual(self.cpu.current_cycles, 16)

if __name__ == '__main__':
    unittest.main()
