import unittest
from src.cpu.gb_cpu import CPU
from src.memory.gb_memory import Memory


class TestConditionalJP(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(self.memory)

    def test_jp_nz_taken(self):
        """Test JP NZ,a16 when Z=0 (taken, 16 cycles)"""
        self.memory.set_value(0x0000, 0xC2)
        self.memory.set_value(0x0001, 0x00)  # low byte
        self.memory.set_value(0x0002, 0x80)  # high byte -> 0x8000
        self.cpu.set_flag("Z", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=16)
        self.assertEqual(self.cpu.registers.PC, 0x8000)
        self.assertEqual(self.cpu.current_cycles, 16)

    def test_jp_nz_not_taken(self):
        """Test JP NZ,a16 when Z=1 (not taken, 12 cycles)"""
        self.memory.set_value(0x0000, 0xC2)
        self.memory.set_value(0x0001, 0x00)
        self.memory.set_value(0x0002, 0x80)
        self.cpu.set_flag("Z", True)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)
        self.assertEqual(self.cpu.registers.PC, 0x0003)  # past 3-byte instruction
        self.assertEqual(self.cpu.current_cycles, 12)

    def test_jp_z_taken(self):
        """Test JP Z,a16 when Z=1 (taken, 16 cycles)"""
        self.memory.set_value(0x0000, 0xCA)
        self.memory.set_value(0x0001, 0x50)
        self.memory.set_value(0x0002, 0xC0)  # -> 0xC050
        self.cpu.set_flag("Z", True)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=16)
        self.assertEqual(self.cpu.registers.PC, 0xC050)
        self.assertEqual(self.cpu.current_cycles, 16)

    def test_jp_z_not_taken(self):
        """Test JP Z,a16 when Z=0 (not taken, 12 cycles)"""
        self.memory.set_value(0x0000, 0xCA)
        self.memory.set_value(0x0001, 0x50)
        self.memory.set_value(0x0002, 0xC0)
        self.cpu.set_flag("Z", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)
        self.assertEqual(self.cpu.registers.PC, 0x0003)
        self.assertEqual(self.cpu.current_cycles, 12)

    def test_jp_nc_taken(self):
        """Test JP NC,a16 when C=0 (taken, 16 cycles)"""
        self.memory.set_value(0x0000, 0xD2)
        self.memory.set_value(0x0001, 0x00)
        self.memory.set_value(0x0002, 0x40)  # -> 0x4000
        self.cpu.set_flag("C", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=16)
        self.assertEqual(self.cpu.registers.PC, 0x4000)
        self.assertEqual(self.cpu.current_cycles, 16)

    def test_jp_nc_not_taken(self):
        """Test JP NC,a16 when C=1 (not taken, 12 cycles)"""
        self.memory.set_value(0x0000, 0xD2)
        self.memory.set_value(0x0001, 0x00)
        self.memory.set_value(0x0002, 0x40)
        self.cpu.set_flag("C", True)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)
        self.assertEqual(self.cpu.registers.PC, 0x0003)
        self.assertEqual(self.cpu.current_cycles, 12)

    def test_jp_c_taken(self):
        """Test JP C,a16 when C=1 (taken, 16 cycles)"""
        self.memory.set_value(0x0000, 0xDA)
        self.memory.set_value(0x0001, 0xFF)
        self.memory.set_value(0x0002, 0x01)  # -> 0x01FF
        self.cpu.set_flag("C", True)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=16)
        self.assertEqual(self.cpu.registers.PC, 0x01FF)
        self.assertEqual(self.cpu.current_cycles, 16)

    def test_jp_c_not_taken(self):
        """Test JP C,a16 when C=0 (not taken, 12 cycles)"""
        self.memory.set_value(0x0000, 0xDA)
        self.memory.set_value(0x0001, 0xFF)
        self.memory.set_value(0x0002, 0x01)
        self.cpu.set_flag("C", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)
        self.assertEqual(self.cpu.registers.PC, 0x0003)
        self.assertEqual(self.cpu.current_cycles, 12)


class TestADCImmediate(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(self.memory)

    def test_adc_a_n8_no_carry(self):
        """Test ADC A,n8 without carry flag (0xCE, 8 cycles)"""
        self.memory.set_value(0x0000, 0xCE)
        self.memory.set_value(0x0001, 0x10)
        self.cpu.set_register("A", 0x20)
        self.cpu.set_flag("C", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 8)
        self.assertEqual(self.cpu.get_register("A"), 0x30)
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))
        self.assertFalse(self.cpu.get_flag("H"))
        self.assertFalse(self.cpu.get_flag("C"))

    def test_adc_a_n8_with_carry(self):
        """Test ADC A,n8 with carry flag set"""
        self.memory.set_value(0x0000, 0xCE)
        self.memory.set_value(0x0001, 0x10)
        self.cpu.set_register("A", 0x20)
        self.cpu.set_flag("C", True)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)
        self.assertEqual(self.cpu.get_register("A"), 0x31)  # 0x20 + 0x10 + 1

    def test_adc_a_n8_overflow(self):
        """Test ADC A,n8 with carry out"""
        self.memory.set_value(0x0000, 0xCE)
        self.memory.set_value(0x0001, 0x01)
        self.cpu.set_register("A", 0xFF)
        self.cpu.set_flag("C", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)
        self.assertEqual(self.cpu.get_register("A"), 0x00)
        self.assertTrue(self.cpu.get_flag("Z"))
        self.assertTrue(self.cpu.get_flag("H"))
        self.assertTrue(self.cpu.get_flag("C"))

    def test_adc_a_n8_half_carry(self):
        """Test ADC A,n8 half carry from carry flag"""
        self.memory.set_value(0x0000, 0xCE)
        self.memory.set_value(0x0001, 0x0F)
        self.cpu.set_register("A", 0x00)
        self.cpu.set_flag("C", True)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)
        self.assertEqual(self.cpu.get_register("A"), 0x10)
        self.assertTrue(self.cpu.get_flag("H"))  # 0x0 + 0xF + 1 > 0xF
        self.assertFalse(self.cpu.get_flag("C"))


class TestADDSP(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(self.memory)

    def test_add_sp_e8_positive(self):
        """Test ADD SP,e8 with positive offset (0xE8, 16 cycles)"""
        self.memory.set_value(0x0000, 0xE8)
        self.memory.set_value(0x0001, 0x05)  # +5
        self.cpu.registers.SP = 0xFFF0
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=16)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 16)
        self.assertEqual(self.cpu.registers.SP, 0xFFF5)
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))

    def test_add_sp_e8_negative(self):
        """Test ADD SP,e8 with negative offset"""
        self.memory.set_value(0x0000, 0xE8)
        self.memory.set_value(0x0001, 0xFE)  # -2
        self.cpu.registers.SP = 0x1000
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=16)
        self.assertEqual(self.cpu.registers.SP, 0x0FFE)

    def test_add_sp_e8_flags(self):
        """Test ADD SP,e8 half-carry and carry flags"""
        self.memory.set_value(0x0000, 0xE8)
        self.memory.set_value(0x0001, 0x01)
        self.cpu.registers.SP = 0x00FF
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=16)
        self.assertEqual(self.cpu.registers.SP, 0x0100)
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))
        self.assertTrue(self.cpu.get_flag("H"))  # (0xF + 0x1) > 0xF
        self.assertTrue(self.cpu.get_flag("C"))  # (0xFF + 0x01) > 0xFF


class TestDAA(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(self.memory)

    def test_daa_after_add_no_adjust(self):
        """Test DAA after addition needing no adjustment (0x27, 4 cycles)"""
        # 0x15 + 0x22 = 0x37 (valid BCD, no adjust needed)
        self.memory.set_value(0x0000, 0x27)
        self.cpu.set_register("A", 0x37)
        self.cpu.set_flag("N", False)
        self.cpu.set_flag("H", False)
        self.cpu.set_flag("C", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 4)
        self.assertEqual(self.cpu.get_register("A"), 0x37)
        self.assertFalse(self.cpu.get_flag("C"))

    def test_daa_after_add_low_nibble_adjust(self):
        """Test DAA adjusting low nibble after addition"""
        # A = 0x1A (low nibble > 9), should add 0x06 -> 0x20
        self.memory.set_value(0x0000, 0x27)
        self.cpu.set_register("A", 0x1A)
        self.cpu.set_flag("N", False)
        self.cpu.set_flag("H", False)
        self.cpu.set_flag("C", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)
        self.assertEqual(self.cpu.get_register("A"), 0x20)
        self.assertFalse(self.cpu.get_flag("C"))

    def test_daa_after_add_high_nibble_adjust(self):
        """Test DAA adjusting high nibble after addition"""
        # A = 0xA0 (> 0x99), should add 0x60 -> 0x00, C=1
        self.memory.set_value(0x0000, 0x27)
        self.cpu.set_register("A", 0xA0)
        self.cpu.set_flag("N", False)
        self.cpu.set_flag("H", False)
        self.cpu.set_flag("C", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)
        self.assertEqual(self.cpu.get_register("A"), 0x00)
        self.assertTrue(self.cpu.get_flag("Z"))
        self.assertTrue(self.cpu.get_flag("C"))

    def test_daa_after_add_both_adjust(self):
        """Test DAA adjusting both nibbles after addition"""
        # A = 0x9A, should add 0x60 + 0x06 = 0x66 -> 0x00, C=1
        self.memory.set_value(0x0000, 0x27)
        self.cpu.set_register("A", 0x9A)
        self.cpu.set_flag("N", False)
        self.cpu.set_flag("H", False)
        self.cpu.set_flag("C", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)
        self.assertEqual(self.cpu.get_register("A"), 0x00)
        self.assertTrue(self.cpu.get_flag("Z"))
        self.assertTrue(self.cpu.get_flag("C"))

    def test_daa_after_add_with_h_flag(self):
        """Test DAA with H flag set after addition"""
        # H flag set means half-carry occurred, add 0x06
        self.memory.set_value(0x0000, 0x27)
        self.cpu.set_register("A", 0x30)
        self.cpu.set_flag("N", False)
        self.cpu.set_flag("H", True)
        self.cpu.set_flag("C", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)
        self.assertEqual(self.cpu.get_register("A"), 0x36)
        self.assertFalse(self.cpu.get_flag("H"))

    def test_daa_after_sub(self):
        """Test DAA after subtraction with H flag"""
        # After SUB: N=1, H=1 -> subtract 0x06
        self.memory.set_value(0x0000, 0x27)
        self.cpu.set_register("A", 0xFA)  # Result of e.g. 0x00 - 0x06
        self.cpu.set_flag("N", True)
        self.cpu.set_flag("H", True)
        self.cpu.set_flag("C", True)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)
        # 0xFA - 0x60 - 0x06 = 0x94
        self.assertEqual(self.cpu.get_register("A"), 0x94)
        self.assertTrue(self.cpu.get_flag("C"))  # C stays set
        self.assertFalse(self.cpu.get_flag("H"))

    def test_daa_zero_result(self):
        """Test DAA produces zero flag"""
        self.memory.set_value(0x0000, 0x27)
        self.cpu.set_register("A", 0x00)
        self.cpu.set_flag("N", False)
        self.cpu.set_flag("H", False)
        self.cpu.set_flag("C", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)
        self.assertEqual(self.cpu.get_register("A"), 0x00)
        self.assertTrue(self.cpu.get_flag("Z"))


if __name__ == "__main__":
    unittest.main()
