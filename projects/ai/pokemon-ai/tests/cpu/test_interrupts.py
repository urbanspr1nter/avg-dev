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
        """Test EI instruction sets pending flag"""
        # Set IME to False initially
        self.cpu.interrupts.ime = False
        
        # Execute EI instruction
        self.memory.set_value(0x0000, 0xFB)  # EI opcode
        self.cpu.registers.PC = 0x0000
        
        self.cpu.run(max_cycles=4)
        
        self.assertEqual(self.cpu.current_cycles, 4)
        self.assertFalse(self.cpu.interrupts.ime)  # Should still be False
        self.assertTrue(self.cpu.interrupts.ime_pending)  # Should be pending
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

    def test_ei_delayed_enable(self):
        """Test EI instruction has 1-instruction delay"""
        # Set up V-Blank interrupt
        self.memory.set_value(0xFF0F, 0x01)  # IF register - V-Blank pending
        self.memory.set_value(0xFFFF, 0x01)  # IE register - V-Blank enabled
        self.cpu.interrupts.ime = False
        self.cpu.registers.PC = 0x0000

        # Set up program: EI followed by NOP
        self.memory.set_value(0x0000, 0xFB)  # EI opcode
        self.memory.set_value(0x0001, 0x00)  # NOP opcode
        self.memory.set_value(0x0002, 0x00)  # Another NOP to see if interrupt fires

        # Run EI instruction only - should not service interrupt yet
        self.cpu.run(max_cycles=4)
        self.assertEqual(self.cpu.current_cycles, 4)
        self.assertFalse(self.cpu.interrupts.ime)  # Should still be disabled
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertTrue(self.cpu.interrupts.ime_pending)  # Should be pending

        # Run NOP instruction - should enable interrupts and service interrupt
        self.cpu.run(max_cycles=24)  # 4 for NOP + 20 for interrupt
        self.assertEqual(self.cpu.current_cycles, 28)  # 4 + 4 + 20
        self.assertFalse(self.cpu.interrupts.ime)  # Should be disabled during interrupt service
        self.assertFalse(self.cpu.interrupts.ime_pending)  # Should be cleared
        self.assertEqual(self.cpu.registers.PC, 0x40)  # V-Blank handler

    def test_ei_delay_with_multiple_instructions(self):
        """Test EI delay with multiple instructions"""
        # Set up V-Blank interrupt
        self.memory.set_value(0xFF0F, 0x01)  # IF register - V-Blank pending
        self.memory.set_value(0xFFFF, 0x01)  # IE register - V-Blank enabled
        self.cpu.interrupts.ime = False
        self.cpu.registers.PC = 0x0000

        # Set up program: EI, INC A, NOP
        self.memory.set_value(0x0000, 0xFB)  # EI opcode
        self.memory.set_value(0x0001, 0x3C)  # INC A opcode
        self.memory.set_value(0x0002, 0x00)  # NOP opcode

        # Run EI instruction
        self.cpu.run(max_cycles=4)
        self.assertFalse(self.cpu.interrupts.ime)
        self.assertTrue(self.cpu.interrupts.ime_pending)
        self.assertEqual(self.cpu.registers.PC, 0x0001)

        # Run INC A instruction - should enable interrupts after this
        self.cpu.run(max_cycles=8)  # 4 more cycles for INC A
        self.assertTrue(self.cpu.interrupts.ime)  # Should be enabled after INC A
        self.assertFalse(self.cpu.interrupts.ime_pending)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.get_register("A"), 0x01)  # A should be incremented

        # Now interrupt should be serviced on next instruction
        self.cpu.run(max_cycles=24)  # 20 for interrupt service
        self.assertEqual(self.cpu.current_cycles, 28)  # 4 + 4 + 20
        self.assertEqual(self.cpu.registers.PC, 0x40)  # V-Blank handler

    def test_ei_no_pending_interrupt(self):
        """Test EI delay when no interrupts are pending"""
        self.cpu.interrupts.ime = False
        self.cpu.registers.PC = 0x0000
        self.cpu.set_register("A", 0x00)

        # Set up program: EI followed by INC A
        self.memory.set_value(0x0000, 0xFB)  # EI opcode
        self.memory.set_value(0x0001, 0x3C)  # INC A opcode
        self.memory.set_value(0x0002, 0x00)  # NOP opcode

        # Run both instructions
        self.cpu.run(max_cycles=8)
        self.assertEqual(self.cpu.current_cycles, 8)
        self.assertTrue(self.cpu.interrupts.ime)  # Should be enabled
        self.assertFalse(self.cpu.interrupts.ime_pending)  # Should be cleared
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.get_register("A"), 0x01)  # A should be incremented

    def test_ei_delay_with_multi_byte_instruction(self):
        """Test EI delay with multi-byte instruction (JP nn)"""
        # Set up V-Blank interrupt
        self.memory.set_value(0xFF0F, 0x01)  # IF register - V-Blank pending
        self.memory.set_value(0xFFFF, 0x01)  # IE register - V-Blank enabled
        self.cpu.interrupts.ime = False
        self.cpu.registers.PC = 0x0000

        # Set up program: EI followed by JP 0x1000
        self.memory.set_value(0x0000, 0xFB)  # EI opcode
        self.memory.set_value(0x0001, 0xC3)  # JP opcode
        self.memory.set_value(0x0002, 0x00)  # Low byte of address
        self.memory.set_value(0x0003, 0x10)  # High byte of address

        # Run EI instruction
        self.cpu.run(max_cycles=4)
        self.assertFalse(self.cpu.interrupts.ime)
        self.assertTrue(self.cpu.interrupts.ime_pending)
        self.assertEqual(self.cpu.registers.PC, 0x0001)

        # Run JP instruction - should enable interrupts after this
        self.cpu.run(max_cycles=16)  # 16 cycles for JP
        self.assertTrue(self.cpu.interrupts.ime)  # Should be enabled after JP
        self.assertFalse(self.cpu.interrupts.ime_pending)
        self.assertEqual(self.cpu.registers.PC, 0x1000)

        # Now interrupt should be serviced on next instruction
        self.cpu.run(max_cycles=24)  # 20 for interrupt service
        self.assertEqual(self.cpu.current_cycles, 40)  # 4 + 16 + 20
        self.assertEqual(self.cpu.registers.PC, 0x40)  # V-Blank handler

    @unittest.skip("CB-prefixed instructions not yet implemented")
    def test_ei_delay_with_cb_prefixed_instruction(self):
        """Test EI delay with CB-prefixed instruction"""
        # Set up V-Blank interrupt
        self.memory.set_value(0xFF0F, 0x01)  # IF register - V-Blank pending
        self.memory.set_value(0xFFFF, 0x01)  # IE register - V-Blank enabled
        self.cpu.interrupts.ime = False
        self.cpu.registers.PC = 0x0000
        self.cpu.set_register("A", 0x55)

        # Set up program: EI followed by CB 0x37 (SWAP A)
        self.memory.set_value(0x0000, 0xFB)  # EI opcode
        self.memory.set_value(0x0001, 0xCB)  # CB prefix
        self.memory.set_value(0x0002, 0x37)  # SWAP A opcode

        # Run EI instruction
        self.cpu.run(max_cycles=4)
        self.assertFalse(self.cpu.interrupts.ime)
        self.assertTrue(self.cpu.interrupts.ime_pending)
        self.assertEqual(self.cpu.registers.PC, 0x0001)

        # Run CB-prefixed instruction - should enable interrupts after this
        # Note: CB instructions take 8 cycles
        self.cpu.run(max_cycles=8)
        self.assertTrue(self.cpu.interrupts.ime)  # Should be enabled after CB instruction
        self.assertFalse(self.cpu.interrupts.ime_pending)
        self.assertEqual(self.cpu.registers.PC, 0x0003)
        self.assertEqual(self.cpu.get_register("A"), 0x55)  # SWAP A of 0x55 = 0x55

        # Now interrupt should be serviced on next instruction
        self.cpu.run(max_cycles=24)  # 20 for interrupt service
        self.assertEqual(self.cpu.current_cycles, 24)  # 4 + 8 + 20
        self.assertEqual(self.cpu.registers.PC, 0x40)  # V-Blank handler

    def test_ei_delay_interrupt_during_delay(self):
        """Test EI delay when interrupt is triggered during the delay period"""
        # Set up V-Blank interrupt
        self.memory.set_value(0xFF0F, 0x01)  # IF register - V-Blank pending
        self.memory.set_value(0xFFFF, 0x01)  # IE register - V-Blank enabled
        self.cpu.interrupts.ime = False
        self.cpu.registers.PC = 0x0000

        # Set up program: EI followed by long sequence
        self.memory.set_value(0x0000, 0xFB)  # EI opcode
        self.memory.set_value(0x0001, 0x00)  # NOP
        self.memory.set_value(0x0002, 0x00)  # NOP
        self.memory.set_value(0x0003, 0x00)  # NOP

        # Run EI instruction
        self.cpu.run(max_cycles=4)
        self.assertFalse(self.cpu.interrupts.ime)
        self.assertTrue(self.cpu.interrupts.ime_pending)
        self.assertEqual(self.cpu.registers.PC, 0x0001)

        # Run first NOP - should enable interrupts after this
        self.cpu.current_cycles = 0  # Reset for step-by-step testing
        self.cpu.run(max_cycles=4)
        self.assertTrue(self.cpu.interrupts.ime)  # Should be enabled after NOP
        self.assertFalse(self.cpu.interrupts.ime_pending)
        self.assertEqual(self.cpu.registers.PC, 0x0002)

        # Now interrupt should be serviced immediately (before next NOP)
        self.cpu.run(max_cycles=24)  # 20 for interrupt service
        self.assertEqual(self.cpu.current_cycles, 24)  # 4 + 4 + 20
        self.assertEqual(self.cpu.registers.PC, 0x40)  # V-Blank handler

    def test_ei_delay_with_halt_interaction(self):
        """Test EI delay interaction with HALT instruction"""
        # Set up V-Blank interrupt
        self.memory.set_value(0xFF0F, 0x01)  # IF register - V-Blank pending
        self.memory.set_value(0xFFFF, 0x01)  # IE register - V-Blank enabled
        self.cpu.interrupts.ime = False
        self.cpu.registers.PC = 0x0000

        # Set up program: EI followed by HALT
        self.memory.set_value(0x0000, 0xFB)  # EI opcode
        self.memory.set_value(0x0001, 0x76)  # HALT opcode

        # Run EI instruction
        self.cpu.run(max_cycles=4)
        self.assertFalse(self.cpu.interrupts.ime)
        self.assertTrue(self.cpu.interrupts.ime_pending)
        self.assertEqual(self.cpu.registers.PC, 0x0001)

        # Run HALT instruction - should enable interrupts and service interrupt
        self.cpu.run(max_cycles=24)  # 4 for HALT + 20 for interrupt
        self.assertFalse(self.cpu.interrupts.ime)  # Should be disabled during interrupt service
        self.assertFalse(self.cpu.interrupts.ime_pending)
        self.assertFalse(self.cpu.interrupts.halted)  # Should be cleared by interrupt
        self.assertEqual(self.cpu.current_cycles, 28)  # 4 + 4 + 20
        self.assertEqual(self.cpu.registers.PC, 0x40)  # V-Blank handler

    def test_ei_delay_complex_sequence(self):
        """Test EI delay with complex instruction sequence"""
        # Set up V-Blank interrupt
        self.memory.set_value(0xFF0F, 0x01)  # IF register - V-Blank pending
        self.memory.set_value(0xFFFF, 0x01)  # IE register - V-Blank enabled
        self.cpu.interrupts.ime = False
        self.cpu.registers.PC = 0x0000
        self.cpu.set_register("A", 0x00)
        self.cpu.set_register("B", 0x05)

        # Set up program: EI, LD A, B, DEC B, JR NZ, -2
        self.memory.set_value(0x0000, 0xFB)  # EI opcode
        self.memory.set_value(0x0001, 0x78)  # LD A, B
        self.memory.set_value(0x0002, 0x05)  # DEC B
        self.memory.set_value(0x0003, 0x20)  # JR NZ, -2
        self.memory.set_value(0x0004, 0xFC)  # -4 offset (2's complement)

        # Run EI instruction
        self.cpu.run(max_cycles=4)
        self.assertFalse(self.cpu.interrupts.ime)
        self.assertTrue(self.cpu.interrupts.ime_pending)
        self.assertEqual(self.cpu.registers.PC, 0x0001)

        # Run LD A, B instruction - should enable interrupts after this
        self.cpu.current_cycles = 0  # Reset for step-by-step testing
        self.cpu.run(max_cycles=4)
        self.assertTrue(self.cpu.interrupts.ime)  # Should be enabled after LD
        self.assertFalse(self.cpu.interrupts.ime_pending)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.get_register("A"), 0x05)  # A should be 5

        # Now interrupt should be serviced immediately (before DEC B)
        self.cpu.run(max_cycles=24)  # 20 for interrupt service
        self.assertEqual(self.cpu.current_cycles, 24)  # 4 + 4 + 20
        self.assertEqual(self.cpu.registers.PC, 0x40)  # V-Blank handler

    def test_ei_delay_different_interrupt_types(self):
        """Test EI delay with different interrupt types"""
        for interrupt_bit, handler_addr in [(0x01, 0x40), (0x02, 0x48), (0x04, 0x50), (0x08, 0x58), (0x10, 0x60)]:
            with self.subTest(interrupt_bit=hex(interrupt_bit)):
                # Clear memory
                self.setUp()
                
                # Set up specific interrupt
                self.memory.set_value(0xFF0F, interrupt_bit)  # IF register
                self.memory.set_value(0xFFFF, interrupt_bit)  # IE register
                self.cpu.interrupts.ime = False
                self.cpu.registers.PC = 0x0000

                # Set up program: EI followed by NOP
                self.memory.set_value(0x0000, 0xFB)  # EI opcode
                self.memory.set_value(0x0001, 0x00)  # NOP opcode

                # Run both instructions and interrupt service
                self.cpu.run(max_cycles=28)  # 4 + 4 + 20
                self.assertEqual(self.cpu.current_cycles, 28)
                self.assertEqual(self.cpu.registers.PC, handler_addr)  # Correct handler
                self.assertEqual(self.memory.get_value(0xFF0F), 0x00)  # IF cleared

    def test_ei_delay_timing_validation(self):
        """Test precise timing of EI delay mechanism"""
        # Set up V-Blank interrupt
        self.memory.set_value(0xFF0F, 0x01)  # IF register - V-Blank pending
        self.memory.set_value(0xFFFF, 0x01)  # IE register - V-Blank enabled
        self.cpu.interrupts.ime = False
        self.cpu.registers.PC = 0x0000

        # Set up program: EI, NOP, NOP
        self.memory.set_value(0x0000, 0xFB)  # EI opcode
        self.memory.set_value(0x0001, 0x00)  # NOP opcode
        self.memory.set_value(0x0002, 0x00)  # NOP opcode

        # Execute EI instruction (4 cycles)
        cycles_used = self.cpu.run(max_cycles=4)
        self.assertEqual(cycles_used, 4)
        self.assertEqual(self.cpu.current_cycles, 4)
        self.assertFalse(self.cpu.interrupts.ime)
        self.assertTrue(self.cpu.interrupts.ime_pending)
        self.assertEqual(self.cpu.registers.PC, 0x0001)

        # Execute first NOP - should enable interrupts and service interrupt
        cycles_used = self.cpu.run(max_cycles=24)  # 4 for NOP + 20 for interrupt
        self.assertEqual(cycles_used, 24)
        self.assertEqual(self.cpu.current_cycles, 28)  # 4 + 4 + 20
        self.assertFalse(self.cpu.interrupts.ime)  # Should be disabled during interrupt service
        self.assertFalse(self.cpu.interrupts.ime_pending)  # Should be cleared
        self.assertEqual(self.cpu.registers.PC, 0x40)  # V-Blank handler

    def test_ei_delay_edge_case_no_interrupt_after_enable(self):
        """Test EI delay when no interrupt is pending after enable"""
        self.cpu.interrupts.ime = False
        self.cpu.registers.PC = 0x0000
        self.cpu.set_register("A", 0x00)

        # Set up program: EI, INC A, INC A, INC A
        self.memory.set_value(0x0000, 0xFB)  # EI opcode
        self.memory.set_value(0x0001, 0x3C)  # INC A
        self.memory.set_value(0x0002, 0x3C)  # INC A
        self.memory.set_value(0x0003, 0x3C)  # INC A

        # Run all instructions
        self.cpu.run(max_cycles=16)  # 4 + 4 + 4 + 4
        self.assertEqual(self.cpu.current_cycles, 16)
        self.assertTrue(self.cpu.interrupts.ime)  # Should be enabled
        self.assertFalse(self.cpu.interrupts.ime_pending)
        self.assertEqual(self.cpu.registers.PC, 0x0004)
        self.assertEqual(self.cpu.get_register("A"), 0x03)  # A should be 3


if __name__ == "__main__":
    unittest.main()