import unittest
from src.cpu.gb_cpu import CPU

class TestStack(unittest.TestCase):
    def setUp(self):
        self.cpu = CPU()
    
    def test_push_word_basic(self):
        """Test pushing a single word onto the stack"""
        self.cpu.registers.SP = 0xFFFE
        self.cpu.push_word(0x1234)
        
        # SP should decrement by 2
        self.assertEqual(self.cpu.registers.SP, 0xFFFC)
        
        # Check memory (little-endian: low byte at lower address)
        self.assertEqual(self.cpu.memory.get_value(0xFFFC), 0x34)  # Low byte
        self.assertEqual(self.cpu.memory.get_value(0xFFFD), 0x12)  # High byte
    
    def test_pop_word_basic(self):
        """Test popping a single word from the stack"""
        self.cpu.registers.SP = 0xFFFC
        self.cpu.memory.set_value(0xFFFC, 0x34)  # Low byte
        self.cpu.memory.set_value(0xFFFD, 0x12)  # High byte
        
        value = self.cpu.pop_word()
        
        # SP should increment by 2
        self.assertEqual(self.cpu.registers.SP, 0xFFFE)
        
        # Should read correct value
        self.assertEqual(value, 0x1234)
    
    def test_push_pop_roundtrip(self):
        """Test that push followed by pop returns the same value"""
        self.cpu.registers.SP = 0xFFFE
        original_value = 0xABCD
        
        self.cpu.push_word(original_value)
        popped_value = self.cpu.pop_word()
        
        self.assertEqual(popped_value, original_value)
        self.assertEqual(self.cpu.registers.SP, 0xFFFE)  # SP back to original
    
    def test_push_multiple_words(self):
        """Test pushing multiple words onto the stack"""
        self.cpu.registers.SP = 0xFFFE
        
        self.cpu.push_word(0x1111)
        self.cpu.push_word(0x2222)
        self.cpu.push_word(0x3333)
        
        # SP should decrement by 6 (3 words × 2 bytes)
        self.assertEqual(self.cpu.registers.SP, 0xFFF8)
        
        # Check memory layout (stack grows downward)
        # Most recent push (0x3333) at lowest address
        self.assertEqual(self.cpu.memory.get_value(0xFFF8), 0x33)
        self.assertEqual(self.cpu.memory.get_value(0xFFF9), 0x33)
        self.assertEqual(self.cpu.memory.get_value(0xFFFA), 0x22)
        self.assertEqual(self.cpu.memory.get_value(0xFFFB), 0x22)
        self.assertEqual(self.cpu.memory.get_value(0xFFFC), 0x11)
        self.assertEqual(self.cpu.memory.get_value(0xFFFD), 0x11)
    
    def test_pop_multiple_words(self):
        """Test popping multiple words from the stack"""
        self.cpu.registers.SP = 0xFFF8
        
        # Set up stack (most recent at lowest address)
        self.cpu.memory.set_value(0xFFF8, 0x33)
        self.cpu.memory.set_value(0xFFF9, 0x33)
        self.cpu.memory.set_value(0xFFFA, 0x22)
        self.cpu.memory.set_value(0xFFFB, 0x22)
        self.cpu.memory.set_value(0xFFFC, 0x11)
        self.cpu.memory.set_value(0xFFFD, 0x11)
        
        # Pop in LIFO order
        value1 = self.cpu.pop_word()
        value2 = self.cpu.pop_word()
        value3 = self.cpu.pop_word()
        
        self.assertEqual(value1, 0x3333)
        self.assertEqual(value2, 0x2222)
        self.assertEqual(value3, 0x1111)
        self.assertEqual(self.cpu.registers.SP, 0xFFFE)
    
    def test_stack_wrap_around_on_push(self):
        """Test that SP wraps around correctly when pushing at boundary"""
        self.cpu.registers.SP = 0x0001
        self.cpu.push_word(0x5678)
        
        # SP should wrap: 0x0001 → 0x0000 → 0xFFFF
        self.assertEqual(self.cpu.registers.SP, 0xFFFF)
        
        # Check memory
        self.assertEqual(self.cpu.memory.get_value(0xFFFF), 0x78)  # Low byte
        self.assertEqual(self.cpu.memory.get_value(0x0000), 0x56)  # High byte
    
    def test_stack_wrap_around_on_pop(self):
        """Test that SP wraps around correctly when popping at boundary"""
        self.cpu.registers.SP = 0xFFFF
        self.cpu.memory.set_value(0xFFFF, 0x78)  # Low byte
        self.cpu.memory.set_value(0x0000, 0x56)  # High byte
        
        value = self.cpu.pop_word()
        
        # SP should wrap: 0xFFFF → 0x0000 → 0x0001
        self.assertEqual(self.cpu.registers.SP, 0x0001)
        self.assertEqual(value, 0x5678)
    
    def test_push_pop_preserves_other_registers(self):
        """Test that stack operations don't affect other registers"""
        self.cpu.registers.SP = 0xFFFE
        self.cpu.registers.AF = 0x1234
        self.cpu.registers.BC = 0x5678
        self.cpu.registers.DE = 0x9ABC
        self.cpu.registers.HL = 0xDEF0
        self.cpu.registers.PC = 0x0100
        
        self.cpu.push_word(0xAAAA)
        self.cpu.pop_word()
        
        # All other registers should be unchanged
        self.assertEqual(self.cpu.registers.AF, 0x1234)
        self.assertEqual(self.cpu.registers.BC, 0x5678)
        self.assertEqual(self.cpu.registers.DE, 0x9ABC)
        self.assertEqual(self.cpu.registers.HL, 0xDEF0)
        self.assertEqual(self.cpu.registers.PC, 0x0100)
        self.assertEqual(self.cpu.registers.SP, 0xFFFE)  # Back to original

if __name__ == '__main__':
    unittest.main()
