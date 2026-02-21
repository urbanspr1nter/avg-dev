import unittest
from src.cpu.gb_cpu import CPU
from src.memory.gb_memory import Memory


class TestLoadStore(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(self.memory)

    def test_ld_a_bc(self):
        """Test LD A,(BC) instruction (0x0A, 8 cycles)"""
        self.memory.set_value(0x0000, 0x0A)
        self.cpu.set_register("BC", 0xC000)
        self.memory.set_value(0xC000, 0x42)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        self.assertEqual(self.cpu.get_register("A"), 0x42)

    def test_ld_a_de(self):
        """Test LD A,(DE) instruction (0x1A, 8 cycles)"""
        self.memory.set_value(0x0000, 0x1A)
        self.cpu.set_register("DE", 0xC100)
        self.memory.set_value(0xC100, 0x7F)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        self.assertEqual(self.cpu.get_register("A"), 0x7F)

    def test_ld_de_a(self):
        """Test LD (DE),A instruction (0x12, 8 cycles)"""
        self.memory.set_value(0x0000, 0x12)
        self.cpu.set_register("DE", 0xC200)
        self.cpu.set_register("A", 0xAB)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        self.assertEqual(self.memory.get_value(0xC200), 0xAB)

    def test_ld_sp_hl(self):
        """Test LD SP,HL instruction (0xF9, 8 cycles)"""
        self.memory.set_value(0x0000, 0xF9)
        self.cpu.set_register("HL", 0xDFF0)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        self.assertEqual(self.cpu.registers.SP, 0xDFF0)

    def test_ld_hli_a(self):
        """Test LD (HL+),A instruction (0x22, 8 cycles)"""
        self.memory.set_value(0x0000, 0x22)
        self.cpu.set_register("HL", 0xC000)
        self.cpu.set_register("A", 0x55)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        self.assertEqual(self.memory.get_value(0xC000), 0x55)
        self.assertEqual(self.cpu.get_register("HL"), 0xC001)  # HL incremented

    def test_ld_a_hli(self):
        """Test LD A,(HL+) instruction (0x2A, 8 cycles)"""
        self.memory.set_value(0x0000, 0x2A)
        self.cpu.set_register("HL", 0xC000)
        self.memory.set_value(0xC000, 0x99)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        self.assertEqual(self.cpu.get_register("A"), 0x99)
        self.assertEqual(self.cpu.get_register("HL"), 0xC001)  # HL incremented

    def test_ld_hld_a(self):
        """Test LD (HL-),A instruction (0x32, 8 cycles)"""
        self.memory.set_value(0x0000, 0x32)
        self.cpu.set_register("HL", 0xC005)
        self.cpu.set_register("A", 0x77)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        self.assertEqual(self.memory.get_value(0xC005), 0x77)
        self.assertEqual(self.cpu.get_register("HL"), 0xC004)  # HL decremented

    def test_ld_a_hld(self):
        """Test LD A,(HL-) instruction (0x3A, 8 cycles)"""
        self.memory.set_value(0x0000, 0x3A)
        self.cpu.set_register("HL", 0xC005)
        self.memory.set_value(0xC005, 0xBB)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 8)
        self.assertEqual(self.cpu.get_register("A"), 0xBB)
        self.assertEqual(self.cpu.get_register("HL"), 0xC004)  # HL decremented

    def test_ld_hl_n16(self):
        """Test LD HL,n16 instruction (0x21, 12 cycles)"""
        self.memory.set_value(0x0000, 0x21)
        self.memory.set_value(0x0001, 0x50)  # Low byte
        self.memory.set_value(0x0002, 0xC0)  # High byte
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)
        self.assertEqual(self.cpu.registers.PC, 0x0003)  # 3-byte instruction
        self.assertEqual(self.cpu.current_cycles, 12)
        self.assertEqual(self.cpu.get_register("HL"), 0xC050)

    def test_ld_sp_n16(self):
        """Test LD SP,n16 instruction (0x31, 12 cycles)"""
        self.memory.set_value(0x0000, 0x31)
        self.memory.set_value(0x0001, 0xFE)  # Low byte
        self.memory.set_value(0x0002, 0xFF)  # High byte
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)
        self.assertEqual(self.cpu.registers.PC, 0x0003)  # 3-byte instruction
        self.assertEqual(self.cpu.current_cycles, 12)
        self.assertEqual(self.cpu.registers.SP, 0xFFFE)

    def test_ld_a16_a(self):
        """Test LD (a16),A instruction (0xEA, 16 cycles)"""
        self.memory.set_value(0x0000, 0xEA)
        self.memory.set_value(0x0001, 0x00)  # Low byte of address
        self.memory.set_value(0x0002, 0xC0)  # High byte of address
        self.cpu.set_register("A", 0xDD)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=16)
        self.assertEqual(self.cpu.registers.PC, 0x0003)  # 3-byte instruction
        self.assertEqual(self.cpu.current_cycles, 16)
        self.assertEqual(self.memory.get_value(0xC000), 0xDD)

    def test_ld_a_a16(self):
        """Test LD A,(a16) instruction (0xFA, 16 cycles)"""
        self.memory.set_value(0x0000, 0xFA)
        self.memory.set_value(0x0001, 0x00)  # Low byte of address
        self.memory.set_value(0x0002, 0xC0)  # High byte of address
        self.memory.set_value(0xC000, 0xEE)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=16)
        self.assertEqual(self.cpu.registers.PC, 0x0003)  # 3-byte instruction
        self.assertEqual(self.cpu.current_cycles, 16)
        self.assertEqual(self.cpu.get_register("A"), 0xEE)

    def test_ld_a16_sp(self):
        """Test LD (a16),SP instruction (0x08, 20 cycles)"""
        self.memory.set_value(0x0000, 0x08)
        self.memory.set_value(0x0001, 0x00)  # Low byte of address
        self.memory.set_value(0x0002, 0xC0)  # High byte of address
        self.cpu.registers.SP = 0xFFF8
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=20)
        self.assertEqual(self.cpu.registers.PC, 0x0003)  # 3-byte instruction
        self.assertEqual(self.cpu.current_cycles, 20)
        # SP stored little-endian: low byte at addr, high byte at addr+1
        self.assertEqual(self.memory.get_value(0xC000), 0xF8)  # SP low
        self.assertEqual(self.memory.get_value(0xC001), 0xFF)  # SP high

    def test_ld_hl_sp_e8_positive(self):
        """Test LD HL,SP+e8 with positive offset (0xF8, 12 cycles)"""
        self.memory.set_value(0x0000, 0xF8)
        self.memory.set_value(0x0001, 0x05)  # e8 = +5
        self.cpu.registers.SP = 0xFFF0
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)
        self.assertEqual(self.cpu.registers.PC, 0x0002)  # 2-byte instruction
        self.assertEqual(self.cpu.current_cycles, 12)
        self.assertEqual(self.cpu.get_register("HL"), 0xFFF5)  # 0xFFF0 + 5
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))

    def test_ld_hl_sp_e8_negative(self):
        """Test LD HL,SP+e8 with negative offset (0xF8, 12 cycles)"""
        self.memory.set_value(0x0000, 0xF8)
        self.memory.set_value(0x0001, 0xFE)  # e8 = -2 (signed)
        self.cpu.registers.SP = 0x1000
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 12)
        self.assertEqual(self.cpu.get_register("HL"), 0x0FFE)  # 0x1000 - 2
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))

    def test_ld_hl_sp_e8_flags(self):
        """Test LD HL,SP+e8 half-carry and carry flags"""
        self.memory.set_value(0x0000, 0xF8)
        self.memory.set_value(0x0001, 0x01)  # e8 = +1
        self.cpu.registers.SP = 0x00FF  # SP low byte = 0xFF
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)
        self.assertEqual(self.cpu.get_register("HL"), 0x0100)
        self.assertFalse(self.cpu.get_flag("Z"))
        self.assertFalse(self.cpu.get_flag("N"))
        self.assertTrue(self.cpu.get_flag("H"))  # (0xF + 0x1) > 0xF
        self.assertTrue(self.cpu.get_flag("C"))  # (0xFF + 0x01) > 0xFF


if __name__ == "__main__":
    unittest.main()
