"""
Test cases for jump and control flow instructions.

This module tests:
- Unconditional jumps (JP, JP HL)
- Relative jumps (JR)
- Conditional jumps (JR with flags)
- Call/Return instructions
- Restart instructions
"""

import unittest
from src.cpu.gb_cpu import CPU


class TestJumpInstructions(unittest.TestCase):
    """Test jump and control flow instruction implementations."""

    def setUp(self):
        """Set up test fixtures."""
        self.cpu = CPU()
        # Clear memory for each test
        for i in range(0x10000):
            self.cpu.memory.set_value(i, 0)

    def test_run_jp_nn(self):
        """Test running JP nn instruction (0xC3, 16 cycles)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xC3)  # JP nn
        # Set target address to 0x1234 (low byte first)
        self.cpu.memory.set_value(0x0001, 0x34)
        self.cpu.memory.set_value(0x0002, 0x12)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=16)

        # PC should jump to target address (0x1234)
        self.assertEqual(self.cpu.registers.PC, 0x1234)
        self.assertEqual(self.cpu.current_cycles, 16)

    def test_run_jp_hl(self):
        """Test running JP HL instruction (0xE9, 4 cycles)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xE9)  # JP HL
        # Set HL to point to address 0x5678
        self.cpu.set_register("HL", 0x5678)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=4)

        # PC should jump to HL value (0x5678)
        self.assertEqual(self.cpu.registers.PC, 0x5678)
        self.assertEqual(self.cpu.current_cycles, 4)

    def test_run_jr_n(self):
        """Test running JR n instruction (0x18, 12 cycles)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x18)  # JR n
        # Set offset to +5 (0x05)
        self.cpu.memory.set_value(0x0001, 0x05)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)

        # PC should jump: JR is at 0x0000, 2 bytes, so PC=0x0002 + 5 = 0x0007
        self.assertEqual(self.cpu.registers.PC, 0x0007)
        self.assertEqual(self.cpu.current_cycles, 12)

    def test_run_jr_n_negative_offset(self):
        """Test running JR n with negative offset."""
        # Set opcode at 0x0010
        self.cpu.memory.set_value(0x0010, 0x18)  # JR n
        # Set offset to -3 (0xFD)
        self.cpu.memory.set_value(0x0011, 0xFD)
        self.cpu.registers.PC = 0x0010

        self.cpu.run(max_cycles=12)

        # PC should jump: JR is at 0x0010, 2 bytes, so PC=0x0012 + (-3) = 0x000F
        self.assertEqual(self.cpu.registers.PC, 0x000F)
        self.assertEqual(self.cpu.current_cycles, 12)

    def test_run_jr_nz_n_taken(self):
        """Test running JR NZ, n when jump is taken (Z=0)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x20)  # JR NZ, n
        # Set offset to +10 (0x0A)
        self.cpu.memory.set_value(0x0001, 0x0A)
        self.cpu.registers.PC = 0x0000

        # Clear Z flag
        self.cpu.set_flag("Z", False)

        self.cpu.run(max_cycles=12)

        # PC should jump: JR NZ is at 0x0000, 2 bytes, so PC=0x0002 + 10 = 0x000C
        self.assertEqual(self.cpu.registers.PC, 0x000C)
        self.assertEqual(self.cpu.current_cycles, 12)

    def test_run_jr_nz_n_not_taken(self):
        """Test running JR NZ, n when jump is not taken (Z=1)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x20)  # JR NZ, n
        # Set offset to +10 (0x0A)
        self.cpu.memory.set_value(0x0001, 0x0A)
        self.cpu.registers.PC = 0x0000

        # Set Z flag
        self.cpu.set_flag("Z", True)

        self.cpu.run(max_cycles=8)

        # PC should advance past the 2-byte JR instruction (0x0000 + 2 = 0x0002)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 8)

    def test_run_jr_z_n_taken(self):
        """Test running JR Z, n when jump is taken (Z=1)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x28)  # JR Z, n
        # Set offset to +5 (0x05)
        self.cpu.memory.set_value(0x0001, 0x05)
        self.cpu.registers.PC = 0x0000

        # Set Z flag
        self.cpu.set_flag("Z", True)

        self.cpu.run(max_cycles=12)

        # PC should jump: JR Z is at 0x0000, 2 bytes, so PC=0x0002 + 5 = 0x0007
        self.assertEqual(self.cpu.registers.PC, 0x0007)
        self.assertEqual(self.cpu.current_cycles, 12)

    def test_run_jr_z_n_not_taken(self):
        """Test running JR Z, n when jump is not taken (Z=0)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x28)  # JR Z, n
        # Set offset to +5 (0x05)
        self.cpu.memory.set_value(0x0001, 0x05)
        self.cpu.registers.PC = 0x0000

        # Clear Z flag
        self.cpu.set_flag("Z", False)

        self.cpu.run(max_cycles=8)

        # PC should advance past the 2-byte JR instruction (0x0000 + 2 = 0x0002)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 8)

    def test_run_jr_nc_n_taken(self):
        """Test running JR NC, n when jump is taken (C=0)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x30)  # JR NC, n
        # Set offset to +8 (0x08)
        self.cpu.memory.set_value(0x0001, 0x08)
        self.cpu.registers.PC = 0x0000

        # Clear C flag
        self.cpu.set_flag("C", False)

        self.cpu.run(max_cycles=12)

        # PC should jump: JR NC is at 0x0000, 2 bytes, so PC=0x0002 + 8 = 0x000A
        self.assertEqual(self.cpu.registers.PC, 0x000A)
        self.assertEqual(self.cpu.current_cycles, 12)

    def test_run_jr_nc_n_not_taken(self):
        """Test running JR NC, n when jump is not taken (C=1)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x30)  # JR NC, n
        # Set offset to +8 (0x08)
        self.cpu.memory.set_value(0x0001, 0x08)
        self.cpu.registers.PC = 0x0000

        # Set C flag
        self.cpu.set_flag("C", True)

        self.cpu.run(max_cycles=8)

        # PC should advance past the 2-byte JR instruction (0x0000 + 2 = 0x0002)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 8)

    def test_run_jr_c_n_taken(self):
        """Test running JR C, n when jump is taken (C=1)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x38)  # JR C, n
        # Set offset to +4 (0x04)
        self.cpu.memory.set_value(0x0001, 0x04)
        self.cpu.registers.PC = 0x0000

        # Set C flag
        self.cpu.set_flag("C", True)

        self.cpu.run(max_cycles=12)

        # PC should jump: JR C is at 0x0000, 2 bytes, so PC=0x0002 + 4 = 0x0006
        self.assertEqual(self.cpu.registers.PC, 0x0006)
        self.assertEqual(self.cpu.current_cycles, 12)

    def test_run_jr_c_n_not_taken(self):
        """Test running JR C, n when jump is not taken (C=0)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0x38)  # JR C, n
        # Set offset to +4 (0x04)
        self.cpu.memory.set_value(0x0001, 0x04)
        self.cpu.registers.PC = 0x0000

        # Clear C flag
        self.cpu.set_flag("C", False)

        self.cpu.run(max_cycles=8)

        # PC should advance past the 2-byte JR instruction (0x0000 + 2 = 0x0002)
        self.assertEqual(self.cpu.registers.PC, 0x0002)
        self.assertEqual(self.cpu.current_cycles, 8)

    def test_run_call_nn(self):
        """Test running CALL nn instruction (0xCD, 24 cycles)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xCD)  # CALL nn
        # Set target address to 0x2345 (low byte first)
        self.cpu.memory.set_value(0x0001, 0x45)
        self.cpu.memory.set_value(0x0002, 0x23)

        # Set SP to point to memory location 0xFFFE-0xFFFF
        self.cpu.registers.SP = 0xFFFE
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=24)

        # PC should jump to target address (0x2345)
        self.assertEqual(self.cpu.registers.PC, 0x2345)

        # Return address (PC + 3) should be pushed onto stack
        # Stack grows downward: first byte (high) at SP+1, second byte (low) at SP
        return_addr_low = self.cpu.memory.get_value(0xFFFC)
        return_addr_high = self.cpu.memory.get_value(0xFFFD)

        expected_return_addr = 0x0003  # PC + 3 (after CALL instruction)
        self.assertEqual(return_addr_low, expected_return_addr & 0xFF)
        self.assertEqual(return_addr_high, (expected_return_addr >> 8) & 0xFF)

        self.assertEqual(self.cpu.current_cycles, 24)

    def test_run_call_nz_nn_taken(self):
        """Test running CALL NZ, nn when call is taken (Z=0)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xC4)  # CALL NZ, nn
        # Set target address to 0x1234
        self.cpu.memory.set_value(0x0001, 0x34)
        self.cpu.memory.set_value(0x0002, 0x12)

        # Set SP and clear Z flag
        self.cpu.registers.SP = 0xFFFE
        self.cpu.set_flag("Z", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=24)

        # PC should jump to target address (0x1234)
        self.assertEqual(self.cpu.registers.PC, 0x1234)

        # Return address should be pushed onto stack
        return_addr_low = self.cpu.memory.get_value(0xFFFC)
        return_addr_high = self.cpu.memory.get_value(0xFFFD)
        expected_return_addr = 0x0003
        self.assertEqual(return_addr_low, expected_return_addr & 0xFF)
        self.assertEqual(return_addr_high, (expected_return_addr >> 8) & 0xFF)

        self.assertEqual(self.cpu.current_cycles, 24)

    def test_run_call_nz_nn_not_taken(self):
        """Test running CALL NZ, nn when call is not taken (Z=1)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xC4)  # CALL NZ, nn
        # Set target address to 0x1234
        self.cpu.memory.set_value(0x0001, 0x34)
        self.cpu.memory.set_value(0x0002, 0x12)

        # Set Z flag
        self.cpu.set_flag("Z", True)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)

        # PC should just advance by 3 bytes (opcode + 2-byte address)
        self.assertEqual(self.cpu.registers.PC, 0x0003)

        # Stack should not be modified
        stack_value = self.cpu.memory.get_value(0xFFFE)
        self.assertEqual(stack_value, 0)  # Memory was cleared in setUp

        self.assertEqual(self.cpu.current_cycles, 12)

    def test_run_call_z_nn_taken(self):
        """Test running CALL Z, nn when call is taken (Z=1)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xCC)  # CALL Z, nn
        # Set target address to 0x5678
        self.cpu.memory.set_value(0x0001, 0x78)
        self.cpu.memory.set_value(0x0002, 0x56)

        # Set SP and Z flag
        self.cpu.registers.SP = 0xFFFE
        self.cpu.set_flag("Z", True)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=24)

        # PC should jump to target address (0x5678)
        self.assertEqual(self.cpu.registers.PC, 0x5678)

        # Return address should be pushed onto stack
        return_addr_low = self.cpu.memory.get_value(0xFFFC)
        return_addr_high = self.cpu.memory.get_value(0xFFFD)
        expected_return_addr = 0x0003
        self.assertEqual(return_addr_low, expected_return_addr & 0xFF)
        self.assertEqual(return_addr_high, (expected_return_addr >> 8) & 0xFF)

        self.assertEqual(self.cpu.current_cycles, 24)

    def test_run_call_z_nn_not_taken(self):
        """Test running CALL Z, nn when call is not taken (Z=0)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xCC)  # CALL Z, nn
        # Set target address to 0x5678
        self.cpu.memory.set_value(0x0001, 0x78)
        self.cpu.memory.set_value(0x0002, 0x56)

        # Clear Z flag
        self.cpu.set_flag("Z", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)

        # PC should just advance by 3 bytes
        self.assertEqual(self.cpu.registers.PC, 0x0003)

        # Stack should not be modified
        stack_value = self.cpu.memory.get_value(0xFFFE)
        self.assertEqual(stack_value, 0)

        self.assertEqual(self.cpu.current_cycles, 12)

    def test_run_call_nc_nn_taken(self):
        """Test running CALL NC, nn when call is taken (C=0)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xD4)  # CALL NC, nn
        # Set target address to 0xABCD
        self.cpu.memory.set_value(0x0001, 0xCD)
        self.cpu.memory.set_value(0x0002, 0xAB)

        # Set SP and clear C flag
        self.cpu.registers.SP = 0xFFFE
        self.cpu.set_flag("C", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=24)

        # PC should jump to target address (0xABCD)
        self.assertEqual(self.cpu.registers.PC, 0xABCD)

        # Return address should be pushed onto stack
        return_addr_low = self.cpu.memory.get_value(0xFFFC)
        return_addr_high = self.cpu.memory.get_value(0xFFFD)
        expected_return_addr = 0x0003
        self.assertEqual(return_addr_low, expected_return_addr & 0xFF)
        self.assertEqual(return_addr_high, (expected_return_addr >> 8) & 0xFF)

        self.assertEqual(self.cpu.current_cycles, 24)

    def test_run_call_nc_nn_not_taken(self):
        """Test running CALL NC, nn when call is not taken (C=1)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xD4)  # CALL NC, nn
        # Set target address to 0xABCD
        self.cpu.memory.set_value(0x0001, 0xCD)
        self.cpu.memory.set_value(0x0002, 0xAB)

        # Set C flag
        self.cpu.set_flag("C", True)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)

        # PC should just advance by 3 bytes
        self.assertEqual(self.cpu.registers.PC, 0x0003)

        # Stack should not be modified
        stack_value = self.cpu.memory.get_value(0xFFFE)
        self.assertEqual(stack_value, 0)

        self.assertEqual(self.cpu.current_cycles, 12)

    def test_run_call_c_nn_taken(self):
        """Test running CALL C, nn when call is taken (C=1)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xDC)  # CALL C, nn
        # Set target address to 0x9ABC
        self.cpu.memory.set_value(0x0001, 0xBC)
        self.cpu.memory.set_value(0x0002, 0x9A)

        # Set SP and C flag
        self.cpu.registers.SP = 0xFFFE
        self.cpu.set_flag("C", True)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=24)

        # PC should jump to target address (0x9ABC)
        self.assertEqual(self.cpu.registers.PC, 0x9ABC)

        # Return address should be pushed onto stack
        return_addr_low = self.cpu.memory.get_value(0xFFFC)
        return_addr_high = self.cpu.memory.get_value(0xFFFD)
        expected_return_addr = 0x0003
        self.assertEqual(return_addr_low, expected_return_addr & 0xFF)
        self.assertEqual(return_addr_high, (expected_return_addr >> 8) & 0xFF)

        self.assertEqual(self.cpu.current_cycles, 24)

    def test_run_call_c_nn_not_taken(self):
        """Test running CALL C, nn when call is not taken (C=0)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xDC)  # CALL C, nn
        # Set target address to 0x9ABC
        self.cpu.memory.set_value(0x0001, 0xBC)
        self.cpu.memory.set_value(0x0002, 0x9A)

        # Clear C flag
        self.cpu.set_flag("C", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=12)

        # PC should just advance by 3 bytes
        self.assertEqual(self.cpu.registers.PC, 0x0003)

        # Stack should not be modified
        stack_value = self.cpu.memory.get_value(0xFFFE)
        self.assertEqual(stack_value, 0)

        self.assertEqual(self.cpu.current_cycles, 12)

    def test_run_ret(self):
        """Test running RET instruction (0xC9, 16 cycles)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xC9)  # RET

        # Set SP to point to memory location 0xFFFE-0xFFFF
        self.cpu.registers.SP = 0xFFFE

        # Push return address onto stack
        return_addr = 0x4567
        self.cpu.push_word(return_addr)

        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=16)

        # PC should return to the address on stack (0x4567)
        self.assertEqual(self.cpu.registers.PC, 0x4567)
        self.assertEqual(self.cpu.current_cycles, 16)

    def test_run_ret_nz_taken(self):
        """Test running RET NZ when return is taken (Z=0)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xC0)  # RET NZ

        # Set SP to point to memory location 0xFFFE-0xFFFF
        self.cpu.registers.SP = 0xFFFE

        # Push return address onto stack
        return_addr = 0x89AB
        self.cpu.push_word(return_addr)

        # Clear Z flag
        self.cpu.set_flag("Z", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=20)

        # PC should return to the address on stack (0x89AB)
        self.assertEqual(self.cpu.registers.PC, 0x89AB)
        self.assertEqual(self.cpu.current_cycles, 20)

    def test_run_ret_nz_not_taken(self):
        """Test running RET NZ when return is not taken (Z=1)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xC0)  # RET NZ

        # Set SP to point to memory location 0xFFFE-0xFFFF
        self.cpu.registers.SP = 0xFFFE

        # Push some value onto stack (should not be popped)
        self.cpu.push_word(0x1234)

        # Set Z flag
        self.cpu.set_flag("Z", True)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should just continue (not return)
        self.assertEqual(self.cpu.registers.PC, 0x0001)

        # Stack value should not be popped
        stack_value = self.cpu.memory.get_value(0xFFFE - 2)
        self.assertEqual(stack_value, 0x34)  # Low byte of pushed value

        self.assertEqual(self.cpu.current_cycles, 8)

    def test_run_ret_z_taken(self):
        """Test running RET Z when return is taken (Z=1)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xC8)  # RET Z

        # Set SP to point to memory location 0xFFFE-0xFFFF
        self.cpu.registers.SP = 0xFFFE

        # Push return address onto stack
        return_addr = 0xCDEF
        self.cpu.push_word(return_addr)

        # Set Z flag
        self.cpu.set_flag("Z", True)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=20)

        # PC should return to the address on stack (0xCDEF)
        self.assertEqual(self.cpu.registers.PC, 0xCDEF)
        self.assertEqual(self.cpu.current_cycles, 20)

    def test_run_ret_z_not_taken(self):
        """Test running RET Z when return is not taken (Z=0)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xC8)  # RET Z

        # Set SP to point to memory location 0xFFFE-0xFFFF
        self.cpu.registers.SP = 0xFFFE

        # Push some value onto stack (should not be popped)
        self.cpu.push_word(0x5678)

        # Clear Z flag
        self.cpu.set_flag("Z", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should just continue
        self.assertEqual(self.cpu.registers.PC, 0x0001)

        # Stack value should not be popped
        stack_value = self.cpu.memory.get_value(0xFFFE - 2)
        self.assertEqual(stack_value, 0x78)  # Low byte of pushed value

        self.assertEqual(self.cpu.current_cycles, 8)

    def test_run_ret_nc_taken(self):
        """Test running RET NC when return is taken (C=0)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xD0)  # RET NC

        # Set SP to point to memory location 0xFFFE-0xFFFF
        self.cpu.registers.SP = 0xFFFE

        # Push return address onto stack
        return_addr = 0xEF01
        self.cpu.push_word(return_addr)

        # Clear C flag
        self.cpu.set_flag("C", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=20)

        # PC should return to the address on stack (0xEF01)
        self.assertEqual(self.cpu.registers.PC, 0xEF01)
        self.assertEqual(self.cpu.current_cycles, 20)

    def test_run_ret_nc_not_taken(self):
        """Test running RET NC when return is not taken (C=1)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xD0)  # RET NC

        # Set SP to point to memory location 0xFFFE-0xFFFF
        self.cpu.registers.SP = 0xFFFE

        # Push some value onto stack (should not be popped)
        self.cpu.push_word(0x9ABC)

        # Set C flag
        self.cpu.set_flag("C", True)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should just continue
        self.assertEqual(self.cpu.registers.PC, 0x0001)

        # Stack value should not be popped
        stack_value = self.cpu.memory.get_value(0xFFFE - 2)
        self.assertEqual(stack_value, 0xBC)  # Low byte of pushed value

        self.assertEqual(self.cpu.current_cycles, 8)

    def test_run_ret_c_taken(self):
        """Test running RET C when return is taken (C=1)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xD8)  # RET C

        # Set SP to point to memory location 0xFFFE-0xFFFF
        self.cpu.registers.SP = 0xFFFE

        # Push return address onto stack
        return_addr = 0x3456
        self.cpu.push_word(return_addr)

        # Set C flag
        self.cpu.set_flag("C", True)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=20)

        # PC should return to the address on stack (0x3456)
        self.assertEqual(self.cpu.registers.PC, 0x3456)
        self.assertEqual(self.cpu.current_cycles, 20)

    def test_run_ret_c_not_taken(self):
        """Test running RET C when return is not taken (C=0)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xD8)  # RET C

        # Set SP to point to memory location 0xFFFE-0xFFFF
        self.cpu.registers.SP = 0xFFFE

        # Push some value onto stack (should not be popped)
        self.cpu.push_word(0x789A)

        # Clear C flag
        self.cpu.set_flag("C", False)
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=8)

        # PC should just continue
        self.assertEqual(self.cpu.registers.PC, 0x0001)

        # Stack value should not be popped
        stack_value = self.cpu.memory.get_value(0xFFFE - 2)
        self.assertEqual(stack_value, 0x9A)  # Low byte of pushed value

        self.assertEqual(self.cpu.current_cycles, 8)

    def test_run_reti(self):
        """Test running RETI instruction (0xD9, 16 cycles)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xD9)  # RETI

        # Set SP to avoid writing to IE register at 0xFFFF
        self.cpu.registers.SP = 0xFFFE

        # Push return address onto stack
        return_addr = 0xBCDE
        self.cpu.push_word(return_addr)

        # Disable interrupts initially
        self.cpu.interrupts.enabled = False
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=16)

        # PC should return to the address on stack (0xBCDE)
        self.assertEqual(self.cpu.registers.PC, 0xBCDE)

        # Interrupts should be enabled
        self.assertTrue(self.cpu.interrupts.ime)

        self.assertEqual(self.cpu.current_cycles, 16)

    def test_run_rst_00h(self):
        """Test running RST 00H instruction (0xC7, 16 cycles)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xC7)  # RST 00H

        # Set SP to point to memory location 0xFFFE-0xFFFF
        self.cpu.registers.SP = 0xFFFE
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=16)

        # PC should jump to restart address (0x00)
        self.assertEqual(self.cpu.registers.PC, 0x00)

        # Current PC should be pushed onto stack
        return_addr_low = self.cpu.memory.get_value(0xFFFC)
        return_addr_high = self.cpu.memory.get_value(0xFFFD)

        expected_return_addr = 0x0001  # PC + 1 (after RST instruction)
        self.assertEqual(return_addr_low, expected_return_addr & 0xFF)
        self.assertEqual(return_addr_high, (expected_return_addr >> 8) & 0xFF)

        self.assertEqual(self.cpu.current_cycles, 16)

    def test_run_rst_38h(self):
        """Test running RST 38H instruction (0xFF, 16 cycles)."""
        # Set opcode at 0x0000
        self.cpu.memory.set_value(0x0000, 0xFF)  # RST 38H

        # Set SP to point to memory location 0xFFFE-0xFFFF
        self.cpu.registers.SP = 0xFFFE
        self.cpu.registers.PC = 0x0000

        self.cpu.run(max_cycles=16)

        # PC should jump to restart address (0x38)
        self.assertEqual(self.cpu.registers.PC, 0x38)

        # Current PC should be pushed onto stack
        return_addr_low = self.cpu.memory.get_value(0xFFFC)
        return_addr_high = self.cpu.memory.get_value(0xFFFD)

        expected_return_addr = 0x0001  # PC + 1 (after RST instruction)
        self.assertEqual(return_addr_low, expected_return_addr & 0xFF)
        self.assertEqual(return_addr_high, (expected_return_addr >> 8) & 0xFF)

        self.assertEqual(self.cpu.current_cycles, 16)


if __name__ == "__main__":
    unittest.main()
