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
  - `test_bitwise_ops.py`: Bitwise operation tests
  - `test_rotate_ops.py`: Rotation/shift operation tests
  - `test_ld_r1_r2.py`: LD r1, r2 instruction tests

## Implementation Patterns

### Opcode Handler Pattern
```python
def handler_name(cpu, opcode_info) -> int:
    """Mnemonic - Brief description"""
    # Access immediate operands from cpu.operand_values
    # Update registers/memory via cpu.set_register(), cpu.memory.set_value()
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

## Code Conventions

1. **Naming**: Use snake_case for method names, follow Gameboy assembly mnemonics
2. **Comments**: Minimal - focus on clear code and docstrings
3. **Testing**: Comprehensive unit tests for all new functionality
4. **Cycle Accuracy**: Must match official Gameboy CPU cycle counts
5. **Memory Safety**: All memory accesses must be bounded (0x0000-0xFFFF)
6. **Searching**: Use Kagi Search MCP tool if prompted to search for things outside of your knowledge base or repo

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

## Commands to Run Tests

```bash
# Run all CPU tests
python -m unittest discover tests/cpu -v

# Run specific test file
python -m unittest tests.cpu.test_fetch_with_operands -v

# Run specific test method
python -m unittest tests.cpu.test_fetch_with_operands.TestFetchWithOperands.test_run_ld_d_n8 -v
```

## Implemented Opcodes

### Arithmetic Operations (ADD, SUB, SBC)
- **ADD A, r**: 0x80-0x87, 0xC6 (9 instructions)
- **SUB A, r**: 0x90-0x97, 0xD6 (9 instructions)
- **SBC A, r**: 0x98-0x9F, 0xDE (9 instructions)

### Bitwise Operations (AND, OR, XOR, CP)
- **AND A, r**: 0xA0-0xA7, 0xE6 (9 instructions)
- **OR A, r**: 0xB0-0xB7, 0xF6 (9 instructions)
- **XOR A, r**: 0xA8-0xAF, 0xEE (9 instructions)
- **CP A, r**: 0xB8-0xBF, 0xFE (9 instructions)

### Rotation/Shift Operations
- **RLC A**: 0x07
- **RRC A**: 0x0F
- **RL A**: 0x17
- **RR A**: 0x1F
- **RLA A**: 0x27
- **RRA A**: 0x2F

### Load Instructions
- **LD (HL), n8**: 0x36
- **LD r1, r2**: 0x40-0x7F (56 instructions)
- **PUSH rr**: 0xC5, 0xD5, 0xE5, 0xF5 (4 instructions)
- **POP rr**: 0xC1, 0xD1, 0xE1, 0xF1 (4 instructions)
- **LDH (n), A**: 0xE0
- **LDH (C), A**: 0xE2
- **LDH A, (n)**: 0xF0
- **LDH A, (C)**: 0xF2

### Total Implemented: 167 opcodes

## Next Steps - Jump Instructions

The next major set of instructions to implement are the jump/control flow instructions. These include:

### Unconditional Jumps
- **JP nn**: 0xC3 (Jump to address)
- **JR n**: 0x18, 0x20, 0x28, 0x30, 0x38 (Relative jumps with conditions)
- **JP HL**: 0xE9 (Jump to HL register)

### Conditional Jumps
- **JR NZ, n**: 0x20 (Jump if Z flag is not set)
- **JR Z, n**: 0x28 (Jump if Z flag is set)
- **JR NC, n**: 0x30 (Jump if C flag is not set)
- **JR C, n**: 0x38 (Jump if C flag is set)

### Call/Return Instructions
- **CALL nn**: 0xCD (Call subroutine at address)
- **CALL NZ, nn**: 0xC4 (Call if Z not set)
- **CALL Z, nn**: 0xCC (Call if Z set)
- **CALL NC, nn**: 0xD4 (Call if C not set)
- **CALL C, nn**: 0xDC (Call if C set)
- **RET**: 0xC9 (Return from subroutine)
- **RET NZ**: 0xC0 (Return if Z not set)
- **RET Z**: 0xC8 (Return if Z set)
- **RET NC**: 0xD0 (Return if C not set)
- **RET C**: 0xD8 (Return if C set)
- **RETI**: 0xD9 (Return and enable interrupts)

### Restart Instructions
- **RST 00H**: 0xC7
- **RST 08H**: 0xCF
- **RST 10H**: 0xD7
- **RST 18H**: 0xDF
- **RST 20H**: 0xE7
- **RST 28H**: 0xEF
- **RST 30H**: 0xF7
- **RST 38H**: 0xFF

### Implementation Plan for Jump Instructions

1. **Create jump_handlers.py** in `src/cpu/handlers/`
2. **Implement each instruction type separately**:
   - Start with unconditional jumps (JP nn, JP HL)
   - Then relative jumps (JR n and conditional variants)
   - Then call/return instructions
   - Finally restart instructions
3. **Register in dispatch table** at `src/cpu/gb_cpu.py`
4. **Add comprehensive tests** in appropriate test files
5. **Verify cycle accuracy**:
   - JP nn: 16 cycles (3-byte instruction)
   - JR n: 12/8 cycles (depending on jump taken)
   - JP HL: 4 cycles
   - CALL nn: 24/12 cycles (with/without jump)
   - RET: 16/8 cycles (with/without jump)
   - RST: 16 cycles each

### Key Implementation Details

- **PC Management**: Jump instructions must update PC correctly
- **Cycle Counting**: Conditional jumps have different cycle counts based on whether the jump is taken
- **Stack Operations**: CALL and RET use stack for return addresses
- **Flag Conditions**: Conditional jumps check Z, C, N, H flags

## Recent Work Summary

### February 8, 2026 - PUSH/POP Instructions
**Date**: February 8, 2026

**Changes Made**:
1. Created `src/cpu/handlers/stack_handlers.py` with 8 handler functions:
   - PUSH AF (0xF5), PUSH BC (0xC5), PUSH DE (0xD5), PUSH HL (0xE5)
   - POP AF (0xF1), POP BC (0xC1), POP DE (0xD1), POP HL (0xE1)

2. Registered handlers in dispatch table at `src/cpu/gb_cpu.py`

3. Added imports for all handler functions

4. Added comprehensive test cases to `tests/cpu/test_stack.py`:
   - Basic functionality tests
   - PC advancement and cycle counting verification
   - Stack pointer management tests
   - Multiple push/pop sequences
   - Boundary/wrap-around scenarios

**Verification**: All 226 CPU tests pass (including the new PUSH/POP instruction tests)

### February 8, 2026 - LDH Instructions
**Date**: February 8, 2026

**Changes Made**:
1. Created `src/cpu/handlers/ldh_handlers.py` with 4 handler functions:
   - LDH (n), A (0xE0)
   - LDH A, (n) (0xF0)
   - LDH (C), A (0xE2)
   - LDH A, (C) (0xF2)

2. Registered handlers in dispatch table

3. Added imports and comprehensive tests

**Verification**: All 217 CPU tests pass

### February 8, 2026 - Additional Rotation Instructions
**Date**: February 8, 2026

**Changes Made**:
1. Added RLA (0x27) and RRA (0x2F) to `src/cpu/handlers/rotate_handlers.py`

2. Registered handlers in dispatch table

3. Added comprehensive tests

**Verification**: All 217 CPU tests pass

### February 1, 2026 - LD r1, r2 Instructions
**Date**: February 1, 2026

**Changes Made**:
1. Created `src/cpu/handlers/ld_r1_r2_handlers.py` with 56 handler functions for all register-to-register load instructions (0x40-0x7F)

2. Registered all handlers in dispatch table

3. Added comprehensive tests

**Verification**: All 207 CPU tests pass

### February 1, 2026 - Bitwise Operations
**Date**: February 1, 2026

**Changes Made**:
1. Created `src/cpu/handlers/bitwise_handlers.py` with 38 handler functions:
   - AND A, r (9 instructions)
   - OR A, r (9 instructions)
   - XOR A, r (9 instructions)
   - CP A, r (9 instructions)

2. Registered handlers in dispatch table

3. Added comprehensive tests with flag manipulation verification

**Verification**: All 181 CPU tests pass

### February 1, 2026 - Rotation/Shift Operations
**Date**: February 1, 2026

**Changes Made**:
1. Created `src/cpu/handlers/rotate_handlers.py` with 4 handler functions:
   - RLC A (0x07)
   - RRC A (0x0F)
   - RL A (0x17)
   - RR A (0x1F)

2. Registered handlers in dispatch table

3. Added comprehensive tests

**Verification**: All 191 CPU tests pass

### January 31, 2026 - SUB/SBC Instructions
**Date**: January 31, 2026

**Changes Made**:
1. Added handler functions to `src/cpu/handlers/arith_handlers.py`:
   - SUB A, r (9 instructions)
   - SBC A, r (9 instructions)

2. Registered handlers in dispatch table

3. Added comprehensive tests with flag manipulation verification

**Verification**: All 143 CPU tests pass

### January 31, 2026 - ADD Instructions
**Date**: January 31, 2026

**Changes Made**:
1. Added handler functions to `src/cpu/handlers/arith_handlers.py`:
   - ADD A, r (9 instructions)

2. Registered handlers in dispatch table

3. Updated ADC test cases

4. Added comprehensive tests with flag manipulation verification

**Verification**: All 123 CPU tests pass