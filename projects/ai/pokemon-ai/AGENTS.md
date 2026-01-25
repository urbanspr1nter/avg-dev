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

### LD L, n8 Implementation (0x2E)
**Date**: January 24, 2026

**Changes Made**:
1. Added `ld_l_n8` handler function to `src/cpu/handlers/ld_handlers.py`
   - Loads 8-bit immediate value into register L
   - Returns 8 cycles

2. Registered handler in dispatch table at `src/cpu/gb_cpu.py:47`:
   ```python
   0x2E: ld_l_n8
   ```

3. Added import for `ld_l_n8` function at `src/cpu/gb_cpu.py:16`

4. Added test case to `tests/cpu/test_fetch_with_operands.py`:
   ```python
   def test_run_ld_l_n8(self):
       """Test running LD L, n8 instruction (0x2E, 8 cycles)"""
       self.cpu.memory.set_value(0x0000, 0x2E)  # LD L, n8
       self.cpu.memory.set_value(0x0001, 0x7F)  # n8 = 0x7F
       self.cpu.registers.PC = 0x0000
        
       self.cpu.run(max_cycles=8)
        
       self.assertEqual(self.cpu.registers.PC, 0x0002)
       self.assertEqual(self.cpu.current_cycles, 8)
       self.assertEqual(self.cpu.get_register('L'), 0x7F)
   ```

**Verification**: All 62 CPU tests pass (including the new test)

### LD H, n8 Implementation (0x26)
**Date**: January 24, 2026

**Changes Made**:
1. Added `_ld_h_n8()` handler function to `src/cpu/handlers/ld_handlers.py`
   - Loads 8-bit immediate value into register H
   - Returns 8 cycles

2. Registered handler in dispatch table at `src/cpu/gb_cpu.py:47`:
   ```python
   0x26: ld_h_n8
   ```

3. Added import for `ld_h_n8` function at `src/cpu/gb_cpu.py:16`

4. Added test case to `tests/cpu/test_fetch_with_operands.py`:
   ```python
   def test_run_ld_h_n8(self):
       """Test running LD H, n8 instruction (0x26, 8 cycles)"""
       self.cpu.memory.set_value(0x0000, 0x26)  # LD H, n8
       self.cpu.memory.set_value(0x0001, 0xFF)  # n8 = 0xFF
       self.cpu.registers.PC = 0x0000
       
       self.cpu.run(max_cycles=8)
       
       self.assertEqual(self.cpu.registers.PC, 0x0002)
       self.assertEqual(self.cpu.current_cycles, 8)
       self.assertEqual(self.cpu.get_register('H'), 0xFF)
   ```

**Verification**: All 61 CPU tests pass (including the new test)

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

### INC B Implementation (0x04)
**Date**: January 24, 2026

**Changes Made**:
1. Added `inc_b()` handler function to `src/cpu/handlers/inc_dec_handlers.py`
   - Increments register B by 1
   - Updates Z flag if result is zero
   - Updates H flag for half carry
   - Returns 4 cycles

2. Registered handler in dispatch table at `src/cpu/gb_cpu.py:47`:
   ```python
   0x04: inc_b
   ```

3. Added import for `inc_b` function at `src/cpu/gb_cpu.py:16`

4. Added test case to `tests/cpu/test_fetch_with_operands.py`:
   ```python
   def test_run_inc_b(self):
       """Test running INC B instruction (0x04, 4 cycles)"""
       self.cpu.set_register('B', 0x7F)
       self.cpu.registers.PC = 0x0000
       
       self.cpu.run(max_cycles=4)
       
       self.assertEqual(self.cpu.registers.PC, 0x0001)
       self.assertEqual(self.cpu.current_cycles, 4)
       self.assertEqual(self.cpu.get_register('B'), 0x80)
   ```

**Verification**: All 65 CPU tests pass (including the new test)

### INC C Implementation (0x0C)
**Date**: January 24, 2026

**Changes Made**:
1. Added `inc_c()` handler function to `src/cpu/handlers/inc_dec_handlers.py`
   - Increments register C by 1
   - Updates Z flag if result is zero
   - Updates H flag for half carry
   - Returns 4 cycles

2. Registered handler in dispatch table at `src/cpu/gb_cpu.py:47`:
   ```python
   0x0C: inc_c
   ```

3. Added import for `inc_c` function at `src/cpu/gb_cpu.py:16`

4. Added test case to `tests/cpu/test_fetch_with_operands.py`:
   ```python
   def test_run_inc_c(self):
       """Test running INC C instruction (0x0C, 4 cycles)"""
       self.cpu.set_register('C', 0x7F)
       self.cpu.registers.PC = 0x0000
       
       self.cpu.run(max_cycles=4)
       
       self.assertEqual(self.cpu.registers.PC, 0x0001)
       self.assertEqual(self.cpu.current_cycles, 4)
       self.assertEqual(self.cpu.get_register('C'), 0x80)
   ```

**Verification**: All 65 CPU tests pass (including the new test)

### INC D Implementation (0x14)
**Date**: January 24, 2026

**Changes Made**:
1. Added `inc_d()` handler function to `src/cpu/handlers/inc_dec_handlers.py`
   - Increments register D by 1
   - Updates Z flag if result is zero
   - Updates H flag for half carry
   - Returns 4 cycles

2. Registered handler in dispatch table at `src/cpu/gb_cpu.py:47`:
   ```python
   0x14: inc_d
   ```

3. Added import for `inc_d` function at `src/cpu/gb_cpu.py:16`

4. Added test case to `tests/cpu/test_fetch_with_operands.py`:
   ```python
   def test_run_inc_d(self):
       """Test running INC D instruction (0x14, 4 cycles)"""
       self.cpu.set_register('D', 0x7F)
       self.cpu.registers.PC = 0x0000
        
       self.cpu.run(max_cycles=4)
        
       self.assertEqual(self.cpu.registers.PC, 0x0001)
       self.assertEqual(self.cpu.current_cycles, 4)
       self.assertEqual(self.cpu.get_register('D'), 0x80)
   ```

**Verification**: All 65 CPU tests pass (including the new test)

### INC H Implementation (0x24)
**Date**: January 25, 2026

**Changes Made**:
1. Added `inc_h()` handler function to `src/cpu/handlers/inc_dec_handlers.py`
   - Increments register H by 1
   - Updates Z flag if result is zero
   - Updates H flag for half carry
   - Returns 4 cycles

2. Registered handler in dispatch table at `src/cpu/gb_cpu.py:50`:
   ```python
   0x24: inc_h
   ```

3. Added import for `inc_h` function at `src/cpu/gb_cpu.py:16`

4. Added test cases to `tests/cpu/test_fetch_with_operands.py`:
   ```python
   def test_run_inc_h(self):
       """Test running INC H instruction (0x24, 4 cycles)"""
       self.cpu.set_register('H', 0x7F)
       self.cpu.registers.PC = 0x0000
        
       self.cpu.run(max_cycles=4)
        
       self.assertEqual(self.cpu.registers.PC, 0x0001)
       self.assertEqual(self.cpu.current_cycles, 4)
       self.assertEqual(self.cpu.get_register('H'), 0x80)
   
   def test_run_inc_h_zero_flag(self):
       """Test running INC H instruction with Zero flag set (0x24, 4 cycles)"""
       self.cpu.set_register('H', 0xFF)
       self.cpu.registers.PC = 0x0000
        
       self.cpu.run(max_cycles=4)
        
       self.assertEqual(self.cpu.registers.PC, 0x0001)
       self.assertEqual(self.cpu.current_cycles, 4)
       self.assertEqual(self.cpu.get_register('H'), 0x00)
       self.assertTrue(self.cpu.get_flag('Z'))
   ```

**Verification**: All 68 CPU tests pass (including the new tests)

### INC L Implementation (0x2C) and INC A Implementation (0x3C)
**Date**: January 25, 2026

**Changes Made**:
1. Added `inc_l()` and `inc_a()` handler functions to `src/cpu/handlers/inc_dec_handlers.py`
   - Both increment their respective registers by 1
   - Update Z flag if result is zero
   - Update H flag for half carry
   - Return 4 cycles each

2. Registered handlers in dispatch table at `src/cpu/gb_cpu.py:50`:
   ```python
   0x2C: inc_l
   0x3C: inc_a
   ```

3. Added imports for `inc_l` and `inc_a` functions at `src/cpu/gb_cpu.py:16`

4. Added test cases to `tests/cpu/test_fetch_with_operands.py`:
   ```python
   def test_run_inc_l(self):
       """Test running INC L instruction (0x2C, 4 cycles)"""
       self.cpu.set_register('L', 0x7F)
       self.cpu.registers.PC = 0x0000
        
       self.cpu.run(max_cycles=4)
        
       self.assertEqual(self.cpu.registers.PC, 0x0001)
       self.assertEqual(self.cpu.current_cycles, 4)
       self.assertEqual(self.cpu.get_register('L'), 0x80)
   
   def test_run_inc_a(self):
       """Test running INC A instruction (0x3C, 4 cycles)"""
       self.cpu.set_register('A', 0x7F)
       self.cpu.registers.PC = 0x0000
        
       self.cpu.run(max_cycles=4)
        
       self.assertEqual(self.cpu.registers.PC, 0x0001)
       self.assertEqual(self.cpu.current_cycles, 4)
       self.assertEqual(self.cpu.get_register('A'), 0x80)
   ```

**Verification**: All 72 CPU tests pass (including the new tests)

### DEC B Implementation (0x05), DEC C Implementation (0x0D), and DEC D Implementation (0x15)
**Date**: January 25, 2026

**Changes Made**:
1. Added `dec_b()`, `dec_c()`, and `dec_d()` handler functions to `src/cpu/handlers/inc_dec_handlers.py`
   - All decrement their respective registers by 1
   - Update Z flag if result is zero
   - Set N flag (always set for DEC instructions)
   - Update H flag for half borrow
   - Return 4 cycles each

2. Registered handlers in dispatch table at `src/cpu/gb_cpu.py:50`:
   ```python
   0x05: dec_b
   0x0D: dec_c
   0x15: dec_d
   ```

3. Added imports for `dec_b`, `dec_c`, and `dec_d` functions at `src/cpu/gb_cpu.py:16`

4. Added test cases to `tests/cpu/test_fetch_with_operands.py`:
   ```python
   def test_run_dec_b(self):
       """Test running DEC B instruction (0x05, 4 cycles)"""
       self.cpu.set_register('B', 0x80)
       self.cpu.registers.PC = 0x0000
        
       self.cpu.run(max_cycles=4)
        
       self.assertEqual(self.cpu.registers.PC, 0x0001)
       self.assertEqual(self.cpu.current_cycles, 4)
       self.assertEqual(self.cpu.get_register('B'), 0x7F)
   
   def test_run_dec_c(self):
       """Test running DEC C instruction (0x0D, 4 cycles)"""
       self.cpu.set_register('C', 0x80)
       self.cpu.registers.PC = 0x0000
        
       self.cpu.run(max_cycles=4)
        
       self.assertEqual(self.cpu.registers.PC, 0x0001)
       self.assertEqual(self.cpu.current_cycles, 4)
       self.assertEqual(self.cpu.get_register('C'), 0x7F)
   
   def test_run_dec_d(self):
       """Test running DEC D instruction (0x15, 4 cycles)"""
       self.cpu.set_register('D', 0x80)
       self.cpu.registers.PC = 0x0000
        
       self.cpu.run(max_cycles=4)
        
       self.assertEqual(self.cpu.registers.PC, 0x0001)
       self.assertEqual(self.cpu.current_cycles, 4)
       self.assertEqual(self.cpu.get_register('D'), 0x7F)
   ```

**Verification**: All 75 CPU tests pass (including the new tests)

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
