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
