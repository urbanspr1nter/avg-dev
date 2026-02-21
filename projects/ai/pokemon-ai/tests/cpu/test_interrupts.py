import unittest
from src.cpu.gb_cpu import CPU
from src.memory.gb_memory import Memory


class TestInterrupts(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(self.memory)
        
    def test_di_instruction(self):
        """Test DI instruction disables interrupts"""
        # Set IME to True initially
        self.cpu.interrupts.ime = True
        
        # Execute DI instruction
        self.memory.set_value(0x0000, 0xF3)  # DI opcode
        self.cpu.registers.PC = 0x0000
        
        self.cpu.run(max_cycles=4)
        
        self.assertEqual(self.cpu.current_cycles, 4)
        self.assertFalse(self.cpu.interrupts.ime)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        
    def test_ei_instruction(self):
        """Test EI instruction enables interrupts"""
        # Set IME to False initially
        self.cpu.interrupts.ime = False
        
        # Execute EI instruction
        self.memory.set_value(0x0000, 0xFB)  # EI opcode
        self.cpu.registers.PC = 0x0000
        
        self.cpu.run(max_cycles=4)
        
        self.assertEqual(self.cpu.current_cycles, 4)
        self.assertTrue(self.cpu.interrupts.ime)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        
    def test_halt_instruction(self):
        """Test HALT instruction puts CPU in halt state"""
        # Execute HALT instruction
        self.memory.set_value(0x0000, 0x76)  # HALT opcode
        self.cpu.registers.PC = 0x0000
        
        self.cpu.run(max_cycles=4)
        
        self.assertEqual(self.cpu.current_cycles, 4)
        self.assertTrue(self.cpu.interrupts.halted)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        
    def test_halt_with_pending_interrupt(self):
        """Test HALT with pending interrupt services interrupt immediately"""
        # Set up V-Blank interrupt
        self.memory.set_value(0xFF0F, 0x01)  # IF register - V-Blank pending
        self.memory.set_value(0xFFFF, 0x01)  # IE register - V-Blank enabled
        self.cpu.interrupts.ime = True
        
        # Execute HALT instruction
        self.memory.set_value(0x0000, 0x76)  # HALT opcode
        self.cpu.registers.PC = 0x0000
        
        self.cpu.run(max_cycles=20)  # Just the interrupt service (20 cycles)
        
        self.assertEqual(self.cpu.current_cycles, 20)
        self.assertFalse(self.cpu.interrupts.halted)  # Should be cleared by interrupt
        self.assertFalse(self.cpu.interrupts.ime)  # Should be disabled during interrupt
        self.assertEqual(self.cpu.registers.PC, 0x40)  # V-Blank handler address
        self.assertEqual(self.memory.get_value(0xFF0F), 0x00)  # IF should be cleared
        
    def test_interrupt_service_routine(self):
        """Test basic interrupt service routine"""
        # Set up V-Blank interrupt
        self.memory.set_value(0xFF0F, 0x01)  # IF register - V-Blank pending
        self.memory.set_value(0xFFFF, 0x01)  # IE register - V-Blank enabled
        self.cpu.interrupts.ime = True
        self.cpu.registers.PC = 0x1000
        self.cpu.registers.SP = 0xFFFE
        
        # Run CPU - should service interrupt
        self.cpu.run(max_cycles=20)
        
        self.assertEqual(self.cpu.current_cycles, 20)
        self.assertFalse(self.cpu.interrupts.ime)
        self.assertEqual(self.cpu.registers.PC, 0x40)  # V-Blank handler
        self.assertEqual(self.memory.get_value(0xFF0F), 0x00)  # IF cleared
        
        # Check that return address was pushed to stack
        return_addr_low = self.memory.get_value(0xFFFC)
        return_addr_high = self.memory.get_value(0xFFFD)
        return_addr = (return_addr_high << 8) | return_addr_low
        self.assertEqual(return_addr, 0x1000)
        
    def test_reti_instruction(self):
        """Test RETI instruction returns and enables interrupts"""
        # Set up stack with return address
        self.cpu.registers.SP = 0xFFFC
        self.memory.set_value(0xFFFC, 0x34)  # Low byte
        self.memory.set_value(0xFFFD, 0x12)  # High byte
        
        # Execute RETI instruction
        self.memory.set_value(0x0040, 0xD9)  # RETI opcode at V-Blank handler
        self.cpu.registers.PC = 0x0040
        self.cpu.interrupts.ime = False
        
        self.cpu.run(max_cycles=16)
        
        self.assertEqual(self.cpu.current_cycles, 16)
        self.assertTrue(self.cpu.interrupts.ime)  # Should be re-enabled
        self.assertEqual(self.cpu.registers.PC, 0x1234)
        self.assertEqual(self.cpu.registers.SP, 0xFFFE)
        
    def test_interrupt_priority(self):
        """Test that V-Blank has highest priority"""
        # Set up multiple pending interrupts
        self.memory.set_value(0xFF0F, 0x1F)  # All interrupts pending
        self.memory.set_value(0xFFFF, 0x1F)  # All interrupts enabled
        self.cpu.interrupts.ime = True
        self.cpu.registers.PC = 0x2000
        
        # Run CPU - should service V-Blank (highest priority)
        self.cpu.run(max_cycles=20)
        
        self.assertEqual(self.cpu.current_cycles, 20)
        self.assertEqual(self.cpu.registers.PC, 0x40)  # V-Blank handler
        
        # Check that only V-Blank flag was cleared
        if_reg = self.memory.get_value(0xFF0F)
        self.assertEqual(if_reg & 0x01, 0x00)  # V-Blank cleared
        self.assertEqual(if_reg & 0x1E, 0x1E)  # Other flags still set


if __name__ == "__main__":
    unittest.main()