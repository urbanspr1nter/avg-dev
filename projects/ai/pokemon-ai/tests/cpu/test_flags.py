import unittest
from src.cpu.gb_cpu import CPU

class TestFlags(unittest.TestCase):
    def setUp(self):
        self.cpu = CPU()
    
    def test_set_get_flag_z(self):
        """Test setting and getting Zero flag"""
        self.cpu.set_flag('Z', True)
        self.assertTrue(self.cpu.get_flag('Z'))
        
        self.cpu.set_flag('Z', False)
        self.assertFalse(self.cpu.get_flag('Z'))
    
    def test_set_get_flag_n(self):
        """Test setting and getting Subtract flag"""
        self.cpu.set_flag('N', True)
        self.assertTrue(self.cpu.get_flag('N'))
        
        self.cpu.set_flag('N', False)
        self.assertFalse(self.cpu.get_flag('N'))
    
    def test_set_get_flag_h(self):
        """Test setting and getting Half-carry flag"""
        self.cpu.set_flag('H', True)
        self.assertTrue(self.cpu.get_flag('H'))
        
        self.cpu.set_flag('H', False)
        self.assertFalse(self.cpu.get_flag('H'))
    
    def test_set_get_flag_c(self):
        """Test setting and getting Carry flag"""
        self.cpu.set_flag('C', True)
        self.assertTrue(self.cpu.get_flag('C'))
        
        self.cpu.set_flag('C', False)
        self.assertFalse(self.cpu.get_flag('C'))
    
    def test_multiple_flags_independent(self):
        """Test that flags can be set independently"""
        self.cpu.set_flag('Z', True)
        self.cpu.set_flag('C', True)
        
        self.assertTrue(self.cpu.get_flag('Z'))
        self.assertFalse(self.cpu.get_flag('N'))
        self.assertFalse(self.cpu.get_flag('H'))
        self.assertTrue(self.cpu.get_flag('C'))
    
    def test_flags_preserve_a_register(self):
        """Test that flag operations preserve A register value"""
        self.cpu.set_register('A', 0x42)
        self.cpu.set_flag('Z', True)
        self.cpu.set_flag('N', True)
        
        self.assertEqual(self.cpu.get_register('A'), 0x42)
        self.assertTrue(self.cpu.get_flag('Z'))
        self.assertTrue(self.cpu.get_flag('N'))
    
    def test_calc_zero_flag(self):
        """Test zero flag calculation"""
        self.assertTrue(self.cpu.calc_zero_flag(0))
        self.assertTrue(self.cpu.calc_zero_flag(0x100))  # Overflow wraps to 0
        self.assertFalse(self.cpu.calc_zero_flag(1))
        self.assertFalse(self.cpu.calc_zero_flag(0xFF))
    
    def test_calc_half_carry_add_8bit(self):
        """Test half-carry calculation for 8-bit addition"""
        # 0x0F + 0x01 = carry from bit 3 to bit 4
        self.assertTrue(self.cpu.calc_half_carry_add_8bit(0x0F, 0x01))
        
        # 0x0E + 0x01 = no carry from bit 3
        self.assertFalse(self.cpu.calc_half_carry_add_8bit(0x0E, 0x01))
        
        # With carry in: 0x0E + 0x01 + 1 = carry from bit 3
        self.assertTrue(self.cpu.calc_half_carry_add_8bit(0x0E, 0x01, 1))
    
    def test_calc_carry_add_8bit(self):
        """Test carry calculation for 8-bit addition"""
        # 0xFF + 0x01 = carry from bit 7
        self.assertTrue(self.cpu.calc_carry_add_8bit(0xFF, 0x01))
        
        # 0xFE + 0x01 = no carry
        self.assertFalse(self.cpu.calc_carry_add_8bit(0xFE, 0x01))
        
        # With carry in: 0xFE + 0x01 + 1 = carry
        self.assertTrue(self.cpu.calc_carry_add_8bit(0xFE, 0x01, 1))
    
    def test_calc_half_carry_sub_8bit(self):
        """Test half-carry (borrow) calculation for 8-bit subtraction"""
        # 0x00 - 0x01 = borrow from bit 4
        self.assertTrue(self.cpu.calc_half_carry_sub_8bit(0x00, 0x01))
        
        # 0x1F - 0x01 = no borrow from bit 4 (0xF - 0x1 = 0xE, no borrow)
        self.assertFalse(self.cpu.calc_half_carry_sub_8bit(0x1F, 0x01))
        
        # 0x20 - 0x01 = borrow from bit 4 (0x0 - 0x1 = borrow)
        self.assertTrue(self.cpu.calc_half_carry_sub_8bit(0x20, 0x01))
        
        # 0x20 - 0x00 - 1 = borrow from bit 4
        self.assertTrue(self.cpu.calc_half_carry_sub_8bit(0x20, 0x00, 1))
    
    def test_calc_carry_sub_8bit(self):
        """Test carry (borrow) calculation for 8-bit subtraction"""
        # 0x00 - 0x01 = borrow
        self.assertTrue(self.cpu.calc_carry_sub_8bit(0x00, 0x01))
        
        # 0x01 - 0x01 = no borrow
        self.assertFalse(self.cpu.calc_carry_sub_8bit(0x01, 0x01))
        
        # 0x01 - 0x00 - 1 = no borrow
        self.assertFalse(self.cpu.calc_carry_sub_8bit(0x01, 0x00, 1))
    
    def test_calc_half_carry_add_16bit(self):
        """Test half-carry calculation for 16-bit addition"""
        # 0x0FFF + 0x0001 = carry from bit 11 to bit 12
        self.assertTrue(self.cpu.calc_half_carry_add_16bit(0x0FFF, 0x0001))
        
        # 0x0FFE + 0x0001 = no carry from bit 11
        self.assertFalse(self.cpu.calc_half_carry_add_16bit(0x0FFE, 0x0001))
    
    def test_calc_carry_add_16bit(self):
        """Test carry calculation for 16-bit addition"""
        # 0xFFFF + 0x0001 = carry from bit 15
        self.assertTrue(self.cpu.calc_carry_add_16bit(0xFFFF, 0x0001))
        
        # 0xFFFE + 0x0001 = no carry
        self.assertFalse(self.cpu.calc_carry_add_16bit(0xFFFE, 0x0001))

if __name__ == '__main__':
    unittest.main()
