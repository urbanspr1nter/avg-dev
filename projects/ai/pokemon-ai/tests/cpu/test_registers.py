import unittest
from src.cpu.gb_cpu import CPU

class TestRegisters(unittest.TestCase):
    def setUp(self):
        self.cpu = CPU()
    
    def test_get_register_af(self):
        """Test getting AF register"""
        self.cpu.registers.AF = 0x1234
        self.assertEqual(self.cpu.get_register('AF'), 0x1234)
        
    def test_get_register_a(self):
        """Test getting A (high byte of AF)"""
        self.cpu.registers.AF = 0x5678
        self.assertEqual(self.cpu.get_register('A'), 0x56)
        
    def test_get_register_bc(self):
        """Test getting BC register"""
        self.cpu.registers.BC = 0xABCD
        self.assertEqual(self.cpu.get_register('BC'), 0xABCD)
        
    def test_get_register_b(self):
        """Test getting B (high byte of BC)"""
        self.cpu.registers.BC = 0xEF12
        self.assertEqual(self.cpu.get_register('B'), 0xEF)
        
    def test_get_register_c(self):
        """Test getting C (low byte of BC)"""
        self.cpu.registers.BC = 0x3456
        self.assertEqual(self.cpu.get_register('C'), 0x56)
        
    def test_get_register_de(self):
        """Test getting DE register"""
        self.cpu.registers.DE = 0x7890
        self.assertEqual(self.cpu.get_register('DE'), 0x7890)
        
    def test_get_register_d(self):
        """Test getting D (high byte of DE)"""
        self.cpu.registers.DE = 0x1234
        self.assertEqual(self.cpu.get_register('D'), 0x12)
        
    def test_get_register_e(self):
        """Test getting E (low byte of DE)"""
        self.cpu.registers.DE = 0x5678
        self.assertEqual(self.cpu.get_register('E'), 0x78)
        
    def test_get_register_hl(self):
        """Test getting HL register"""
        self.cpu.registers.HL = 0x9ABC
        self.assertEqual(self.cpu.get_register('HL'), 0x9ABC)
        
    def test_get_register_h(self):
        """Test getting H (high byte of HL)"""
        self.cpu.registers.HL = 0xDEF0
        self.assertEqual(self.cpu.get_register('H'), 0xDE)
        
    def test_get_register_l(self):
        """Test getting L (low byte of HL)"""
        self.cpu.registers.HL = 0x1234
        self.assertEqual(self.cpu.get_register('L'), 0x34)
        
    def test_get_register_sp(self):
        """Test getting SP register"""
        self.cpu.registers.SP = 0xFEDC
        self.assertEqual(self.cpu.get_register('SP'), 0xFEDC)
        
    def test_get_register_pc(self):
        """Test getting PC register"""
        self.cpu.registers.PC = 0xBA98
        self.assertEqual(self.cpu.get_register('PC'), 0xBA98)
        
    def test_set_register_af(self):
        """Test setting AF register"""
        self.cpu.set_register('AF', 0x1234)
        self.assertEqual(self.cpu.registers.AF, 0x1234)
        
    def test_set_register_a(self):
        """Test setting A (high byte of AF)"""
        self.cpu.registers.AF = 0xABCD
        self.cpu.set_register('A', 0xEF)
        self.assertEqual(self.cpu.registers.AF, 0xEFCD)
        
    def test_set_register_bc(self):
        """Test setting BC register"""
        self.cpu.set_register('BC', 0x1234)
        self.assertEqual(self.cpu.registers.BC, 0x1234)
        
    def test_set_register_b(self):
        """Test setting B (high byte of BC)"""
        self.cpu.registers.BC = 0xABCD
        self.cpu.set_register('B', 0xEF)
        self.assertEqual(self.cpu.registers.BC, 0xEFCd)
        
    def test_set_register_c(self):
        """Test setting C (low byte of BC)"""
        self.cpu.registers.BC = 0x1234
        self.cpu.set_register('C', 0x56)
        self.assertEqual(self.cpu.registers.BC, 0x1256)
        
    def test_set_register_de(self):
        """Test setting DE register"""
        self.cpu.set_register('DE', 0x5678)
        self.assertEqual(self.cpu.registers.DE, 0x5678)
        
    def test_set_register_d(self):
        """Test setting D (high byte of DE)"""
        self.cpu.registers.DE = 0xABCD
        self.cpu.set_register('D', 0xEF)
        self.assertEqual(self.cpu.registers.DE, 0xEFCd)
        
    def test_set_register_e(self):
        """Test setting E (low byte of DE)"""
        self.cpu.registers.DE = 0x1234
        self.cpu.set_register('E', 0x56)
        self.assertEqual(self.cpu.registers.DE, 0x1256)
        
    def test_set_register_hl(self):
        """Test setting HL register"""
        self.cpu.set_register('HL', 0x9ABC)
        self.assertEqual(self.cpu.registers.HL, 0x9ABC)
        
    def test_set_register_h(self):
        """Test setting H (high byte of HL)"""
        self.cpu.registers.HL = 0xABCD
        self.cpu.set_register('H', 0xEF)
        self.assertEqual(self.cpu.registers.HL, 0xEFCd)
        
    def test_set_register_l(self):
        """Test setting L (low byte of HL)"""
        self.cpu.registers.HL = 0x1234
        self.cpu.set_register('L', 0x56)
        self.assertEqual(self.cpu.registers.HL, 0x1256)
        
    def test_set_register_sp(self):
        """Test setting SP register"""
        self.cpu.set_register('SP', 0xFEDC)
        self.assertEqual(self.cpu.registers.SP, 0xFEDC)
        
    def test_set_register_pc(self):
        """Test setting PC register"""
        self.cpu.set_register('PC', 0xBA98)
        self.assertEqual(self.cpu.registers.PC, 0xBA98)

if __name__ == '__main__':
    unittest.main()
