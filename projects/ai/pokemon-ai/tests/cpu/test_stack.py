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
        self.cpu.registers.SP = 0x0002
        self.cpu.push_word(0x5678)

        # SP should wrap: 0x0002 → 0x0001 → 0x0000
        self.assertEqual(self.cpu.registers.SP, 0x0000)

        # Check memory
        self.assertEqual(self.cpu.memory.get_value(0x0000), 0x78)  # Low byte
        self.assertEqual(self.cpu.memory.get_value(0x0001), 0x56)  # High byte

    def test_stack_wrap_around_on_pop(self):
        """Test that SP wraps around correctly when popping at boundary"""
        self.cpu.registers.SP = 0xFFFC
        self.cpu.memory.set_value(0xFFFC, 0x78)  # Low byte
        self.cpu.memory.set_value(0xFFFD, 0x56)  # High byte

        value = self.cpu.pop_word()

        # SP should increment by 2: 0xFFFC → 0xFFFD → 0xFFFE
        self.assertEqual(self.cpu.registers.SP, 0xFFFE)
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

    def test_run_push_af(self):
        """Test running PUSH AF instruction (0xF5, 16 cycles)"""
        self.cpu.set_register("AF", 0xABCD)
        self.cpu.registers.SP = 0xFFFE
        self.cpu.registers.PC = 0x0000

        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xF5)  # PUSH AF

        self.cpu.run(max_cycles=16)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 16)

        # SP should decrement by 2
        self.assertEqual(self.cpu.registers.SP, 0xFFFC)

        # Check memory (little-endian: low byte at lower address)
        # AF 0xABCD is stored as 0xABC0 (lower 4 bits of F always 0)
        self.assertEqual(self.cpu.memory.get_value(0xFFFC), 0xC0)  # Low byte (F with lower 4 bits masked)
        self.assertEqual(self.cpu.memory.get_value(0xFFFD), 0xAB)  # High byte

    def test_run_pop_af(self):
        """Test running POP AF instruction (0xF1, 12 cycles)"""
        self.cpu.registers.SP = 0xFFFC
        self.cpu.memory.set_value(0xFFFC, 0x78)  # Low byte
        self.cpu.memory.set_value(0xFFFD, 0x56)  # High byte
        self.cpu.registers.PC = 0x0000

        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xF1)  # POP AF

        self.cpu.run(max_cycles=12)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 12)

        # SP should increment by 2
        self.assertEqual(self.cpu.registers.SP, 0xFFFE)

        # AF should be set to popped value (lower 4 bits of F masked to 0)
        self.assertEqual(self.cpu.get_register("AF"), 0x5670)

    def test_run_push_bc(self):
        """Test running PUSH BC instruction (0xC5, 16 cycles)"""
        self.cpu.set_register("BC", 0x1234)
        self.cpu.registers.SP = 0xFFFE
        self.cpu.registers.PC = 0x0000

        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xC5)  # PUSH BC

        self.cpu.run(max_cycles=16)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 16)

        # SP should decrement by 2
        self.assertEqual(self.cpu.registers.SP, 0xFFFC)

        # Check memory (little-endian: low byte at lower address)
        self.assertEqual(self.cpu.memory.get_value(0xFFFC), 0x34)  # Low byte
        self.assertEqual(self.cpu.memory.get_value(0xFFFD), 0x12)  # High byte

    def test_run_pop_bc(self):
        """Test running POP BC instruction (0xC1, 12 cycles)"""
        self.cpu.registers.SP = 0xFFFC
        self.cpu.memory.set_value(0xFFFC, 0x56)  # Low byte
        self.cpu.memory.set_value(0xFFFD, 0x34)  # High byte
        self.cpu.registers.PC = 0x0000

        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xC1)  # POP BC

        self.cpu.run(max_cycles=12)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 12)

        # SP should increment by 2
        self.assertEqual(self.cpu.registers.SP, 0xFFFE)

        # BC should be set to popped value
        self.assertEqual(self.cpu.get_register("BC"), 0x3456)

    def test_run_push_de(self):
        """Test running PUSH DE instruction (0xD5, 16 cycles)"""
        self.cpu.set_register("DE", 0x9ABC)
        self.cpu.registers.SP = 0xFFFE
        self.cpu.registers.PC = 0x0000

        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xD5)  # PUSH DE

        self.cpu.run(max_cycles=16)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 16)

        # SP should decrement by 2
        self.assertEqual(self.cpu.registers.SP, 0xFFFC)

        # Check memory (little-endian: low byte at lower address)
        self.assertEqual(self.cpu.memory.get_value(0xFFFC), 0xBC)  # Low byte
        self.assertEqual(self.cpu.memory.get_value(0xFFFD), 0x9A)  # High byte

    def test_run_pop_de(self):
        """Test running POP DE instruction (0xD1, 12 cycles)"""
        self.cpu.registers.SP = 0xFFFC
        self.cpu.memory.set_value(0xFFFC, 0xDE)  # Low byte
        self.cpu.memory.set_value(0xFFFD, 0xAD)  # High byte
        self.cpu.registers.PC = 0x0000

        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xD1)  # POP DE

        self.cpu.run(max_cycles=12)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 12)

        # SP should increment by 2
        self.assertEqual(self.cpu.registers.SP, 0xFFFE)

        # DE should be set to popped value
        self.assertEqual(self.cpu.get_register("DE"), 0xADDE)

    def test_run_push_hl(self):
        """Test running PUSH HL instruction (0xE5, 16 cycles)"""
        self.cpu.set_register("HL", 0xDEF0)
        self.cpu.registers.SP = 0xFFFE
        self.cpu.registers.PC = 0x0000

        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xE5)  # PUSH HL

        self.cpu.run(max_cycles=16)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 16)

        # SP should decrement by 2
        self.assertEqual(self.cpu.registers.SP, 0xFFFC)

        # Check memory (little-endian: low byte at lower address)
        self.assertEqual(self.cpu.memory.get_value(0xFFFC), 0xF0)  # Low byte
        self.assertEqual(self.cpu.memory.get_value(0xFFFD), 0xDE)  # High byte

    def test_run_pop_hl(self):
        """Test running POP HL instruction (0xE1, 12 cycles)"""
        self.cpu.registers.SP = 0xFFFC
        self.cpu.memory.set_value(0xFFFC, 0x12)  # Low byte
        self.cpu.memory.set_value(0xFFFD, 0x34)  # High byte
        self.cpu.registers.PC = 0x0000

        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xE1)  # POP HL

        self.cpu.run(max_cycles=12)

        # PC should advance by 1 (opcode only, no operands)
        self.assertEqual(self.cpu.registers.PC, 0x0001)
        self.assertEqual(self.cpu.current_cycles, 12)

        # SP should increment by 2
        self.assertEqual(self.cpu.registers.SP, 0xFFFE)

        # HL should be set to popped value
        self.assertEqual(self.cpu.get_register("HL"), 0x3412)

    def test_run_push_pop_sequence(self):
        """Test running a sequence of PUSH and POP instructions"""
        self.cpu.registers.SP = 0xFFFE
        self.cpu.set_register("BC", 0x1111)
        self.cpu.set_register("DE", 0x2222)
        self.cpu.set_register("HL", 0x3333)
        self.cpu.registers.PC = 0x0000

        # Set opcodes: PUSH BC, PUSH DE, PUSH HL
        self.cpu.memory.set_value(0x0000, 0xC5)  # PUSH BC
        self.cpu.memory.set_value(0x0001, 0xD5)  # PUSH DE
        self.cpu.memory.set_value(0x0002, 0xE5)  # PUSH HL

        self.cpu.run(max_cycles=48)

        # PC should advance by 3 (3 opcodes)
        self.assertEqual(self.cpu.registers.PC, 0x0003)
        self.assertEqual(self.cpu.current_cycles, 48)

        # SP should decrement by 6 (3 words × 2 bytes)
        self.assertEqual(self.cpu.registers.SP, 0xFFF8)

        # Check memory layout (most recent push at lowest address)
        self.assertEqual(self.cpu.memory.get_value(0xFFF8), 0x33)  # HL low byte
        self.assertEqual(self.cpu.memory.get_value(0xFFF9), 0x33)  # HL high byte
        self.assertEqual(self.cpu.memory.get_value(0xFFFA), 0x22)  # DE low byte
        self.assertEqual(self.cpu.memory.get_value(0xFFFB), 0x22)  # DE high byte
        self.assertEqual(self.cpu.memory.get_value(0xFFFC), 0x11)  # BC low byte
        self.assertEqual(self.cpu.memory.get_value(0xFFFD), 0x11)  # BC high byte


if __name__ == "__main__":
    unittest.main()
