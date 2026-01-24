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

### Handler Refactoring (January 24, 2026)
**Date**: January 24, 2026

**Changes Made**:
1. Created `src/cpu/handlers/` directory to organize opcode handlers by category
2. Moved handlers into separate files:
   - `ld_handlers.py`: LD (load) instructions
   - `jr_handlers.py`: JR (jump relative) instructions  
   - `misc_handlers.py`: Miscellaneous instructions like NOP
3. Updated CPU class to import handlers and call them as functions instead of methods
4. Added documentation in `src/cpu/handlers/README.md`

**Benefits**:
- Better code organization by instruction type
- Easier maintenance and navigation
- Clearer separation of concerns
- All 60 CPU tests still pass after refactoring

### JR NZ, e8 Test Fix (0x20)
**Date**: January 24, 2026

**Issue**: The test `test_run_jr_nz_e8_jump_not_taken` was failing because it set register A to 0x00 but didn't explicitly set the Z flag. In the Gameboy CPU implementation, setting a register value doesn't automatically update flags - flags must be set explicitly.

**Fix**: Added `self.cpu.set_flag('Z', True)` after setting A to 0x00 in the test case at line 124 of `tests/cpu/test_fetch_with_operands.py`.

**Verification**: All 60 CPU tests now pass

### LD E, n8 Implementation (0x1E)
**Date**: January 24, 2026

**Changes Made**:
1. Added `_ld_e_n8()` handler method to `src/cpu/gb_cpu.py`
   - Loads 8-bit immediate value into register E
   - Returns 8 cycles

2. Registered handler in dispatch table:
   ```python
   0x1E: self._ld_e_n8
   ```

3. Added test case to `tests/cpu/test_fetch_with_operands.py`:
   ```python
   def test_run_ld_e_n8(self):
       """Test running LD E, n8 instruction (0x1E, 8 cycles)"""
       self.cpu.memory.set_value(0x0000, 0x1E)  # LD E, n8
       self.cpu.memory.set_value(0x0001, 0x7F)  # n8 = 0x7F
       self.cpu.registers.PC = 0x0000
       
       self.cpu.run(max_cycles=8)
       
       self.assertEqual(self.cpu.registers.PC, 0x0002)
       self.assertEqual(self.cpu.current_cycles, 8)
       self.assertEqual(self.cpu.get_register('E'), 0x7F)
   ```

**Verification**: All 58 CPU tests pass

### LD D, n8 Implementation (0x16)
**Date**: January 24, 2026

**Changes Made**:
1. Added `_ld_d_n8()` handler method to `src/cpu/gb_cpu.py`
   - Loads 8-bit immediate value into register D
   - Returns 8 cycles

2. Registered handler in dispatch table:
   ```python
   0x16: self._ld_d_n8
   ```

3. Added test case to `tests/cpu/test_fetch_with_operands.py`:
   ```python
   def test_run_ld_d_n8(self):
       """Test running LD D, n8 instruction (0x16, 8 cycles)"""
       self.cpu.memory.set_value(0x0000, 0x16)  # LD D, n8
       self.cpu.memory.set_value(0x0001, 0x42)  # n8 = 0x42
       self.cpu.registers.PC = 0x0000
       
       self.cpu.run(max_cycles=8)
       
       self.assertEqual(self.cpu.registers.PC, 0x0002)
       self.assertEqual(self.cpu.current_cycles, 8)
       self.assertEqual(self.cpu.get_register('D'), 0x42)
   ```

**Verification**: All 57 CPU tests pass

## Commands to Run Tests

```bash
# Run all CPU tests
python -m unittest discover tests/cpu -v

# Run specific test file
python -m unittest tests.cpu.test_fetch_with_operands -v

# Run specific test method
python -m unittest tests.cpu.test_fetch_with_operands.TestFetchWithOperands.test_run_ld_d_n8 -v
```

## Code Conventions

1. **Naming**: Use snake_case for method names, follow Gameboy assembly mnemonics
2. **Comments**: Minimal - focus on clear code and docstrings
3. **Testing**: Comprehensive unit tests for all new functionality
4. **Cycle Accuracy**: Must match official Gameboy CPU cycle counts
5. **Memory Safety**: All memory accesses must be bounded (0x0000-0xFFFF)
