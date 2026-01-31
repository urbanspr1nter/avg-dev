# AGENTS.md

This file contains information for AI agents working on this codebase.

## Project Overview

The pokemon-ai project is a Gameboy emulator with a REST API interface, designed to play Pokemon RED/BLUE using AI-controlled inputs. The emulator focuses on CPU, graphics, sound, and input emulation without peripherals.

## Key Files

### Emulator Core
- `@emulator/DESIGN.md`: Comprehensive design document for the Gameboy emulator
  - Contains hardware specifications, CPU architecture, memory map
  - Documents opcode handling approach using dispatch tables
  - Includes pseudocode for CPU execution loop

### Code Structure
- `src/cpu/gb_cpu.py`: Main CPU implementation
  - Uses dispatch table pattern for opcode handling
  - Each opcode has dedicated handler method
  - Operand values pre-fetched into `self.operand_values`

- `tests/cpu/`: Unit tests for CPU functionality
  - `test_fetch_with_operands.py`: Tests for opcodes with operands
  - `test_registers.py`: Register access tests
  - `test_stack.py`: Stack operations tests
  - `test_flags.py`: Flag manipulation tests

## Implementation Patterns

### Opcode Handler Pattern
```python
def _handler_name(self, opcode_info) -> int:
    """Mnemonic - Brief description"""
    # Access immediate operands from self.operand_values
    # Update registers/memory via self.set_register(), self.memory.set_value()
    return opcode_info["cycles"][0]  # or cycles[1] for conditional branch
```

### Dispatch Table Structure
```python
self.opcode_handlers = {
    0x00: self._nop,
    0x01: self._ld_bc_d16,
    0x16: self._ld_d_n8,  # Example: LD D, n8
    # ... other opcodes ...
}
```

### Testing Approach
- Use unittest framework
- Test files in `tests/cpu/` directory
- Each test verifies:
  - Correct PC advancement based on opcode size
  - Accurate cycle counting
  - Proper register/memory state changes
  - Operand handling for instructions with operands

## Recent Work

### SUB/SBC Implementations (0x90-0x9F, 0xD6, 0xDE)
**Date**: January 31, 2026

**Changes Made**:
1. Added handler functions to `src/cpu/handlers/arith_handlers.py`:
   - SUB instructions (0x90-0x97, 0xD6):
     - `sub_a_b()`: SUB A, B (0x90) - Subtract B from A
     - `sub_a_c()`: SUB A, C (0x91) - Subtract C from A
     - `sub_a_d()`: SUB A, D (0x92) - Subtract D from A
     - `sub_a_e()`: SUB A, E (0x93) - Subtract E from A
     - `sub_a_h()`: SUB A, H (0x94) - Subtract H from A
     - `sub_a_l()`: SUB A, L (0x95) - Subtract L from A
     - `sub_a_hl()`: SUB A, (HL) (0x96) - Subtract value at memory address HL from A
     - `sub_a_a()`: SUB A, A (0x97) - Subtract A from A (always results in 0)
     - `sub_a_n8()`: SUB A, n8 (0xD6) - Subtract immediate byte from A
   
   - SBC instructions (0x98-0x9F, 0xDE):
     - `sbc_a_b()`: SBC A, B (0x98) - Subtract B from A with carry
     - `sbc_a_c()`: SBC A, C (0x99) - Subtract C from A with carry
     - `sbc_a_d()`: SBC A, D (0x9A) - Subtract D from A with carry
     - `sbc_a_e()`: SBC A, E (0x9B) - Subtract E from A with carry
     - `sbc_a_h()`: SBC A, H (0x9C) - Subtract H from A with carry
     - `sbc_a_l()`: SBC A, L (0x9D) - Subtract L from A with carry
     - `sbc_a_hl()`: SBC A, (HL) (0x9E) - Subtract value at memory address HL from A with carry
     - `sbc_a_a()`: SBC A, A (0x9F) - Subtract A from A with carry
     - `sbc_a_n8()`: SBC A, n8 (0xDE) - Subtract immediate byte from A with carry
  
  All handlers:
  - Perform 8-bit subtraction (with optional carry for SBC)
  - Update Z flag if result is zero
  - Set N flag to True (always set for SUB/SBC instructions)
  - Update H flag for half borrow
  - Update C flag for borrow/carry
  - Return appropriate cycle count (4 cycles for register operands, 8 cycles for memory/immediate)

2. Registered handlers in dispatch table at `src/cpu/gb_cpu.py`:
   ```python
   0x90: sub_a_b
   0x91: sub_a_c
   0x92: sub_a_d
   0x93: sub_a_e
   0x94: sub_a_h
   0x95: sub_a_l
   0x96: sub_a_hl
   0x97: sub_a_a
   0xD6: sub_a_n8
   0x98: sbc_a_b
   0x99: sbc_a_c
   0x9A: sbc_a_d
   0x9B: sbc_a_e
   0x9C: sbc_a_h
   0x9D: sbc_a_l
   0x9E: sbc_a_hl
   0x9F: sbc_a_a
   0xDE: sbc_a_n8
   ```

3. Added imports for all handler functions at `src/cpu/gb_cpu.py`

4. Added comprehensive test cases to `tests/cpu/test_fetch_with_operands.py`:
   - Basic functionality tests for each SUB A, xx and SBC A, xx instruction
   - Flag manipulation tests (Z, N, H, C flags)
   - Tests verify correct PC advancement and cycle counting
   - Tests with carry flag set for SBC instructions

**Verification**: All 143 CPU tests pass (including the new tests)

### ADD A, xx Implementations (0x80-0x87, 0xC6)
**Date**: January 31, 2026

**Changes Made**:
1. Added handler functions to `src/cpu/handlers/arith_handlers.py`:
   - `add_a_b()`: ADD A, B (0x80) - Add B to A
   - `add_a_c()`: ADD A, C (0x81) - Add C to A  
   - `add_a_d()`: ADD A, D (0x82) - Add D to A
   - `add_a_e()`: ADD A, E (0x83) - Add E to A
   - `add_a_h()`: ADD A, H (0x84) - Add H to A
   - `add_a_l()`: ADD A, L (0x85) - Add L to A
   - `add_a_hl()`: ADD A, (HL) (0x86) - Add value at memory address HL to A
   - `add_a_a()`: ADD A, A (0x87) - Add A to A (equivalent to A << 1)
   - `add_a_n8()`: ADD A, n8 (0xC6) - Add immediate byte to A
  
  All handlers:
  - Perform 8-bit addition
  - Update Z flag if result is zero
  - Set N flag to False
  - Update H flag for half carry
  - Update C flag for carry
  - Return appropriate cycle count (4 cycles for register operands, 8 cycles for memory/immediate)

2. Registered handlers in dispatch table at `src/cpu/gb_cpu.py`:
   ```python
   0x80: add_a_b
   0x81: add_a_c
   0x82: add_a_d
   0x83: add_a_e
   0x84: add_a_h
   0x85: add_a_l
   0x86: add_a_hl
   0x87: add_a_a
   0xC6: add_a_n8
   ```

3. Added imports for all handler functions at `src/cpu/gb_cpu.py`

4. Updated ADC test cases to use correct opcodes (0x88-0x8F instead of 0x80-0x87)

5. Added comprehensive test cases to `tests/cpu/test_fetch_with_operands.py`:
   - Basic functionality tests for each ADD A, xx instruction
   - Flag manipulation tests (Z, N, H, C flags)
   - Tests verify correct PC advancement and cycle counting

**Verification**: All 123 CPU tests pass (including the new tests)

### LD (HL), n8 Implementation (0x36)
**Date**: January 25, 2026

**Changes Made**:
1. Added `ld_hl_n8()` handler function to `src/cpu/handlers/ld_handlers.py`
   - Loads 8-bit immediate value into memory at address specified by HL register
   - Returns 12 cycles

2. Registered handler in dispatch table at `src/cpu/gb_cpu.py:50`:
   ```python
   0x36: ld_hl_n8
   ```

3. Added import for `ld_hl_n8` function at `src/cpu/gb_cpu.py:16`

4. Added test case to `tests/cpu/test_fetch_with_operands.py`:
   ```python
   def test_run_ld_hl_n8(self):
       """Test running LD (HL), n8 instruction (0x36, 12 cycles)"""
       # Set opcode at 0x0000
       self.cpu.memory.set_value(0x0000, 0x36)  # LD (HL), n8
       # Set operand value to 0x7F
       self.cpu.memory.set_value(0x0001, 0x7F)
       # Set HL to point to address 0xC000
       self.cpu.set_register('HL', 0xC000)
       self.cpu.registers.PC = 0x0000
        
       self.cpu.run(max_cycles=12)
        
       # PC should advance by 2: opcode (1) + operand (1)
       self.assertEqual(self.cpu.registers.PC, 0x0002)
       self.assertEqual(self.cpu.current_cycles, 12)
       # Memory at address 0xC000 should contain 0x7F
       self.assertEqual(self.cpu.memory.get_value(0xC000), 0x7F)
   ```

**Verification**: All 87 CPU tests pass (including the new test)

## Commands to Run Tests

```bash
# Run all CPU tests
python -m unittest discover tests/cpu -v

# Run specific test file
python -m unittest tests.cpu.test_fetch_with_operands -v

# Run specific test method
python -m unittest tests.cpu.test_fetch_with_operands.TestFetchWithOperands.test_run_ld_d_n8 -v
```

## Approach to Implementation

To make the work more digestible and manageable, we follow this approach:

1. **Break down by instruction type**: Group related opcodes together (e.g., all INC instructions, all LD instructions)
2. **Use handler files**: Organize handlers by category in `src/cpu/handlers/` directory
3. **Implement one opcode at a time**: Focus on completing one simple opcode before moving to the next
4. **Write comprehensive tests**: Each new opcode gets its own test case that verifies:
   - Correct PC advancement
   - Accurate cycle counting
   - Proper register/memory state changes
5. **Verify all tests pass**: After each implementation, run the full test suite to ensure no regressions
6. **Document changes**: Update AGENTS.md with details of what was implemented and verified

This approach allows for steady progress while maintaining code quality and ensuring correctness at each step.

## Code Conventions

1. **Naming**: Use snake_case for method names, follow Gameboy assembly mnemonics
2. **Comments**: Minimal - focus on clear code and docstrings
3. **Testing**: Comprehensive unit tests for all new functionality
4. **Cycle Accuracy**: Must match official Gameboy CPU cycle counts
5. **Memory Safety**: All memory accesses must be bounded (0x0000-0xFFFF)
6. **Searching**: Use Kagi Search MCP tool if prompted to search for things outside of your knowledge base or repo

## Next Steps

### Recommended Opcodes to Implement Next

Based on the current implementation pattern and code organization, here are the next easiest sets of opcodes to implement:

#### 1. **AND A, xx (0xA0-0xA7, 0xE6)** - Bitwise AND operations
   - Simple bitwise operations similar to ADD/SUB but with different flag behavior
   - All set N and H flags to False, C flag to False, Z flag based on result
   - Good candidate for implementing after arithmetic ops

#### 2. **OR A, xx (0xB0-0xB7, 0xF6)** - Bitwise OR operations  
   - Similar structure to AND but different flag behavior
   - Set N and H flags to False, C flag to False, Z flag based on result

#### 3. **XOR A, xx (0xA8-0xAF, 0xEE)** - Bitwise XOR operations
   - Similar structure with yet another flag pattern
   - Set N and H flags to False, C flag to False, Z flag based on result

#### 4. **CP A, xx (0xB8-0xBF, 0xFE)** - Compare operations
   - Similar to SUB but doesn't store result, only sets flags
   - Set N and H flags based on subtraction, C flag for borrow, Z if equal

These opcodes follow a similar pattern to the recently implemented ADD/ADC/SUB/SBC instructions:
- Register operands (0xA0-0xAF): 4 cycles
- Memory operand (HL): 8 cycles  
- Immediate operand: 8 cycles
- All are 8-bit operations on register A

The implementation would follow the same pattern:
1. Add handler functions to `src/cpu/handlers/arith_handlers.py`
2. Register in dispatch table at `src/cpu/gb_cpu.py`
3. Add imports
4. Write comprehensive tests
5. Verify all tests pass
