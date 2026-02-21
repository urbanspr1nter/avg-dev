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


    def test_ei_then_di_cancels_pending(self):
        """Test EI followed by DI cancels the pending interrupt enable"""
        # Set up V-Blank interrupt
        self.memory.set_value(0xFF0F, 0x01)  # V-Blank pending
        self.memory.set_value(0xFFFF, 0x01)  # V-Blank enabled
        self.cpu.interrupts.ime = False
        self.cpu.registers.PC = 0x0000

        # Program: EI, DI, NOP
        self.memory.set_value(0x0000, 0xFB)  # EI
        self.memory.set_value(0x0001, 0xF3)  # DI
        self.memory.set_value(0x0002, 0x00)  # NOP

        # Run all three instructions
        self.cpu.run(max_cycles=12)  # 4 + 4 + 4
        self.assertEqual(self.cpu.current_cycles, 12)
        self.assertFalse(self.cpu.interrupts.ime)  # DI should have cancelled
        self.assertFalse(self.cpu.interrupts.ime_pending)  # Pending should be cleared
        self.assertEqual(self.cpu.registers.PC, 0x0003)  # No interrupt, normal flow

    def test_di_then_ei_still_has_delay(self):
        """Test DI followed by EI still has 1-instruction delay"""
        # Set up V-Blank interrupt, start with IME disabled
        self.memory.set_value(0xFF0F, 0x01)  # V-Blank pending
        self.memory.set_value(0xFFFF, 0x01)  # V-Blank enabled
        self.cpu.interrupts.ime = False
        self.cpu.registers.PC = 0x0000

        # Program: DI, EI, NOP
        self.memory.set_value(0x0000, 0xF3)  # DI
        self.memory.set_value(0x0001, 0xFB)  # EI
        self.memory.set_value(0x0002, 0x00)  # NOP (EI delay resolves after this)

        # Run DI — redundant since IME already False
        self.cpu.run(max_cycles=4)
        self.assertFalse(self.cpu.interrupts.ime)
        self.assertEqual(self.cpu.registers.PC, 0x0001)

        # Run EI — sets pending, doesn't enable yet
        self.cpu.run(max_cycles=8)
        self.assertFalse(self.cpu.interrupts.ime)
        self.assertTrue(self.cpu.interrupts.ime_pending)
        self.assertEqual(self.cpu.registers.PC, 0x0002)

        # Run NOP — enables IME, then interrupt fires
        self.cpu.run(max_cycles=28)  # 4 (NOP) + 20 (interrupt)
        self.assertFalse(self.cpu.interrupts.ime)  # Disabled during service
        self.assertEqual(self.cpu.registers.PC, 0x40)  # V-Blank handler

    def test_double_ei(self):
        """Test EI, EI still only has 1-instruction delay"""
        # Set up V-Blank interrupt
        self.memory.set_value(0xFF0F, 0x01)  # V-Blank pending
        self.memory.set_value(0xFFFF, 0x01)  # V-Blank enabled
        self.cpu.interrupts.ime = False
        self.cpu.registers.PC = 0x0000

        # Program: EI, EI, NOP
        self.memory.set_value(0x0000, 0xFB)  # EI
        self.memory.set_value(0x0001, 0xFB)  # EI (second one)
        self.memory.set_value(0x0002, 0x00)  # NOP

        # Run first EI
        self.cpu.run(max_cycles=4)
        self.assertFalse(self.cpu.interrupts.ime)
        self.assertTrue(self.cpu.interrupts.ime_pending)

        # Run second EI — first EI's delay resolves, enabling IME
        # Second EI re-sets pending, but post-instruction logic consumed it
        self.cpu.run(max_cycles=8)
        self.assertTrue(self.cpu.interrupts.ime)  # Enabled from first EI's delay

        # Interrupt fires immediately since IME is now true
        self.cpu.run(max_cycles=28)  # 20 (interrupt service)
        self.assertEqual(self.cpu.registers.PC, 0x40)  # V-Blank handler

    def test_halt_bug_ime_disabled_pending_interrupt(self):
        """Test HALT bug: IME=0 with pending interrupt, next byte read twice"""
        # Set up V-Blank interrupt but keep IME disabled
        self.memory.set_value(0xFF0F, 0x01)  # V-Blank pending
        self.memory.set_value(0xFFFF, 0x01)  # V-Blank enabled
        self.cpu.interrupts.ime = False
        self.cpu.registers.PC = 0x0000
        self.cpu.set_register("A", 0x00)

        # Program: HALT, INC A, INC A
        self.memory.set_value(0x0000, 0x76)  # HALT
        self.memory.set_value(0x0001, 0x3C)  # INC A
        self.memory.set_value(0x0002, 0x3C)  # INC A

        # Run HALT — should trigger HALT bug (not actually halt)
        self.cpu.run(max_cycles=4)
        self.assertEqual(self.cpu.current_cycles, 4)
        self.assertFalse(self.cpu.interrupts.halted)  # Should NOT be halted
        self.assertFalse(self.cpu.interrupts.ime)  # IME stays disabled

        # Run next instructions — first INC A is read twice due to HALT bug
        # PC doesn't advance after the first fetch, so INC A at 0x0001 executes,
        # then INC A at 0x0001 executes again, then INC A at 0x0002
        self.cpu.run(max_cycles=16)  # 3 x INC A = 12 cycles, current_cycles reaches 16
        self.assertEqual(self.cpu.current_cycles, 16)  # 4 (HALT) + 12 (3 INC A)
        self.assertEqual(self.cpu.get_register("A"), 0x03)  # Three increments

    def test_halt_stays_halted_until_interrupt(self):
        """Test HALT with no interrupt idles, then wakes when interrupt arrives"""
        # No interrupts pending
        self.memory.set_value(0xFF0F, 0x00)
        self.memory.set_value(0xFFFF, 0x01)  # V-Blank enabled
        self.cpu.interrupts.ime = True
        self.cpu.registers.PC = 0x0000

        # Program: HALT, NOP
        self.memory.set_value(0x0000, 0x76)  # HALT
        self.memory.set_value(0x0001, 0x00)  # NOP (reached after wake)

        # Run HALT — enters halt state, no interrupt to wake
        self.cpu.run(max_cycles=4)
        self.assertEqual(self.cpu.current_cycles, 4)
        self.assertTrue(self.cpu.interrupts.halted)

        # Run more cycles — CPU is halted, should idle (consume cycles but not execute)
        self.cpu.run(max_cycles=20)  # 4 idle cycles each iteration: 4→8→12→16→20
        self.assertTrue(self.cpu.interrupts.halted)  # Still halted
        self.assertEqual(self.cpu.registers.PC, 0x0001)  # PC unchanged

        # Now trigger V-Blank interrupt externally
        self.memory.set_value(0xFF0F, 0x01)

        # Run again — CPU wakes, services interrupt
        self.cpu.run(max_cycles=40)  # wake + 20 (interrupt service)
        self.assertFalse(self.cpu.interrupts.halted)  # Woke up
        self.assertEqual(self.cpu.registers.PC, 0x40)  # V-Blank handler

    def test_halt_wake_ime_disabled(self):
        """Test HALT wakes on interrupt even with IME=0, but doesn't service"""
        # No interrupts pending initially
        self.memory.set_value(0xFF0F, 0x00)
        self.memory.set_value(0xFFFF, 0x01)  # V-Blank enabled
        self.cpu.interrupts.ime = False
        self.cpu.registers.PC = 0x0000

        # Program: HALT, NOP
        self.memory.set_value(0x0000, 0x76)  # HALT
        self.memory.set_value(0x0001, 0x00)  # NOP

        # Run HALT — no pending interrupt AND IME=0, so enters halt
        self.cpu.run(max_cycles=4)
        self.assertTrue(self.cpu.interrupts.halted)

        # Trigger V-Blank interrupt externally
        self.memory.set_value(0xFF0F, 0x01)

        # Run — CPU wakes but does NOT service (IME=0), executes NOP
        self.cpu.run(max_cycles=8)  # wake + 4 (NOP)
        self.assertFalse(self.cpu.interrupts.halted)  # Woke up
        self.assertFalse(self.cpu.interrupts.ime)  # Still disabled
        self.assertEqual(self.cpu.registers.PC, 0x0002)  # Executed NOP, not interrupt handler


    # ===== Phase 5: Advanced Interrupt Scenarios =====

    def test_nested_interrupt_prevented_by_ime(self):
        """Test that IME=False during interrupt service prevents nested interrupts"""
        # Set up V-Blank + Timer pending
        self.memory.set_value(0xFF0F, 0x05)  # V-Blank (0x01) + Timer (0x04)
        self.memory.set_value(0xFFFF, 0x05)  # Both enabled
        self.cpu.interrupts.ime = True
        self.cpu.registers.PC = 0x0000
        self.cpu.registers.SP = 0xFFFE

        # NOP at 0x0000 (never reached), NOP at V-Blank handler 0x40
        self.memory.set_value(0x0000, 0x00)
        self.memory.set_value(0x0040, 0x00)  # NOP at V-Blank handler

        # Run — V-Blank fires (highest priority), Timer stays pending
        self.cpu.run(max_cycles=20)  # 20 for interrupt service
        self.assertEqual(self.cpu.registers.PC, 0x40)
        self.assertFalse(self.cpu.interrupts.ime)  # Disabled during service

        # Execute NOP at handler — Timer should NOT fire (IME=False)
        self.cpu.run(max_cycles=24)  # 4 more for NOP
        self.assertEqual(self.cpu.registers.PC, 0x41)  # Just advanced past NOP
        self.assertFalse(self.cpu.interrupts.ime)  # Still disabled
        # Timer IF bit still pending
        self.assertEqual(self.memory.get_value(0xFF0F) & 0x04, 0x04)

    def test_interrupt_chain_after_reti(self):
        """Test V-Blank fires, RETI re-enables IME, Timer fires next"""
        # V-Blank + Timer both pending
        self.memory.set_value(0xFF0F, 0x05)  # V-Blank (0x01) + Timer (0x04)
        self.memory.set_value(0xFFFF, 0x05)  # Both enabled
        self.cpu.interrupts.ime = True
        self.cpu.registers.PC = 0x0000
        self.cpu.registers.SP = 0xFFFE

        self.memory.set_value(0x0000, 0x00)  # NOP (return target after RETI)
        self.memory.set_value(0x0040, 0xD9)  # RETI at V-Blank handler

        # V-Blank fires: push 0x0000, jump to 0x40, 20 cycles
        # RETI at 0x40: pop 0x0000, IME=True, 16 cycles
        # Timer fires: push 0x0000, jump to 0x50, 20 cycles
        self.cpu.run(max_cycles=56)  # 20 + 16 + 20
        self.assertEqual(self.cpu.current_cycles, 56)
        self.assertEqual(self.cpu.registers.PC, 0x50)  # Timer handler
        self.assertFalse(self.cpu.interrupts.ime)  # Disabled during Timer service
        # Both IF bits now cleared
        self.assertEqual(self.memory.get_value(0xFF0F) & 0x05, 0x00)

    def test_halt_wakes_on_each_interrupt_type(self):
        """Test HALT wakes and services each of the 5 interrupt types"""
        for interrupt_bit, handler_addr in [(0x01, 0x40), (0x02, 0x48), (0x04, 0x50), (0x08, 0x58), (0x10, 0x60)]:
            with self.subTest(interrupt_bit=hex(interrupt_bit)):
                self.setUp()

                # No interrupt pending initially
                self.memory.set_value(0xFF0F, 0x00)
                self.memory.set_value(0xFFFF, interrupt_bit)
                self.cpu.interrupts.ime = True
                self.cpu.registers.PC = 0x0000

                self.memory.set_value(0x0000, 0x76)  # HALT

                # Execute HALT — enters halt state (no pending interrupt)
                self.cpu.run(max_cycles=4)
                self.assertTrue(self.cpu.interrupts.halted)

                # Trigger interrupt externally
                self.memory.set_value(0xFF0F, interrupt_bit)

                # CPU wakes, services interrupt
                self.cpu.run(max_cycles=24)  # wake + 20 service
                self.assertFalse(self.cpu.interrupts.halted)
                self.assertEqual(self.cpu.registers.PC, handler_addr)
                self.assertEqual(self.memory.get_value(0xFF0F) & interrupt_bit, 0x00)

    def test_halt_wakes_on_lcd_stat_ime_disabled(self):
        """Test HALT with IME=0 wakes on LCD STAT but doesn't service"""
        self.memory.set_value(0xFF0F, 0x00)
        self.memory.set_value(0xFFFF, 0x02)  # LCD STAT enabled
        self.cpu.interrupts.ime = False
        self.cpu.registers.PC = 0x0000

        self.memory.set_value(0x0000, 0x76)  # HALT
        self.memory.set_value(0x0001, 0x00)  # NOP

        # Execute HALT — no pending interrupt, enters halt
        self.cpu.run(max_cycles=4)
        self.assertTrue(self.cpu.interrupts.halted)

        # Trigger LCD STAT externally
        self.memory.set_value(0xFF0F, 0x02)

        # CPU wakes, does NOT service (IME=0), executes NOP
        self.cpu.run(max_cycles=8)  # wake + 4 NOP
        self.assertFalse(self.cpu.interrupts.halted)
        self.assertFalse(self.cpu.interrupts.ime)
        self.assertEqual(self.cpu.registers.PC, 0x0002)  # Past NOP, not handler
        # IF bit still set (not serviced)
        self.assertEqual(self.memory.get_value(0xFF0F) & 0x02, 0x02)

    def test_interrupt_service_stack_near_hram(self):
        """Test interrupt service with default SP doesn't corrupt IF/IE"""
        # SP at default 0xFFFE, PC at 0x0100
        self.cpu.registers.SP = 0xFFFE
        self.cpu.registers.PC = 0x0100
        self.memory.set_value(0xFF0F, 0x01)  # V-Blank pending
        self.memory.set_value(0xFFFF, 0x01)  # V-Blank enabled
        self.cpu.interrupts.ime = True

        # Record IE before
        ie_before = self.memory.get_value(0xFFFF)

        # Service interrupt — pushes PC (0x0100) to stack at 0xFFFC/0xFFFD
        self.cpu.run(max_cycles=20)
        self.assertEqual(self.cpu.registers.PC, 0x40)

        # Verify stack contents
        self.assertEqual(self.cpu.registers.SP, 0xFFFC)
        self.assertEqual(self.memory.get_value(0xFFFC), 0x00)  # Low byte of 0x0100
        self.assertEqual(self.memory.get_value(0xFFFD), 0x01)  # High byte of 0x0100

        # Verify IE register is unchanged
        self.assertEqual(self.memory.get_value(0xFFFF), ie_before)
        # Verify IF V-Blank bit was cleared (not corrupted by stack)
        self.assertEqual(self.memory.get_value(0xFF0F) & 0x01, 0x00)

    def test_interrupt_service_stack_wrap_corrupts_ie(self):
        """Test that stack wrap around 0xFFFF correctly writes through IE handler"""
        # SP at 0x0001 — push will wrap: high byte at 0x0000, low byte at 0xFFFF
        self.cpu.registers.SP = 0x0001
        self.cpu.registers.PC = 0x0100
        self.memory.set_value(0xFF0F, 0x01)  # V-Blank pending
        self.memory.set_value(0xFFFF, 0x01)  # V-Blank enabled
        self.cpu.interrupts.ime = True

        # Service interrupt — push_word(0x0100):
        # SP=0x0000, write high byte 0x01 to 0x0000
        # SP=0xFFFF, write low byte 0x00 to 0xFFFF (IE register!)
        self.cpu.run(max_cycles=20)
        self.assertEqual(self.cpu.registers.PC, 0x40)
        self.assertEqual(self.cpu.registers.SP, 0xFFFF)

        # IE register was overwritten with 0x00 (low byte of PC)
        # This is correct hardware behavior — stack can corrupt IE
        self.assertEqual(self.memory.get_value(0xFFFF), 0x00)

    def test_multiple_pending_clears_only_serviced(self):
        """Test that servicing one interrupt only clears its IF bit"""
        # V-Blank + LCD STAT + Timer all pending and enabled
        self.memory.set_value(0xFF0F, 0x07)  # bits 0,1,2
        self.memory.set_value(0xFFFF, 0x07)
        self.cpu.interrupts.ime = True
        self.cpu.registers.PC = 0x0000
        self.cpu.registers.SP = 0xFFFE

        # V-Blank fires (highest priority)
        self.cpu.run(max_cycles=20)
        self.assertEqual(self.cpu.registers.PC, 0x40)  # V-Blank handler

        # V-Blank IF cleared, LCD STAT + Timer still pending
        if_reg = self.memory.get_value(0xFF0F)
        self.assertEqual(if_reg & 0x01, 0x00)  # V-Blank cleared
        self.assertEqual(if_reg & 0x02, 0x02)  # LCD STAT still set
        self.assertEqual(if_reg & 0x04, 0x04)  # Timer still set

    def test_partial_ie_mask(self):
        """Test that only IE-enabled interrupts fire, even if others are in IF"""
        # All 5 IF bits set, but only Timer enabled in IE
        self.memory.set_value(0xFF0F, 0x1F)  # All pending
        self.memory.set_value(0xFFFF, 0x04)  # Only Timer enabled
        self.cpu.interrupts.ime = True
        self.cpu.registers.PC = 0x0000
        self.cpu.registers.SP = 0xFFFE

        # Only Timer should fire (it's the only one enabled)
        self.cpu.run(max_cycles=20)
        self.assertEqual(self.cpu.registers.PC, 0x50)  # Timer handler at 0x50

        # Timer IF cleared, others still set
        if_reg = self.memory.get_value(0xFF0F)
        self.assertEqual(if_reg & 0x04, 0x00)  # Timer cleared
        self.assertEqual(if_reg & 0x1B, 0x1B)  # All others still set


if __name__ == "__main__":
    unittest.main()