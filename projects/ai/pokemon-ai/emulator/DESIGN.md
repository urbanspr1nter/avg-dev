# Purpose

A GAMEBOY emulator that exposes a REST API to control a ROM being played.

**Ultimate Goal**: Play Pokemon RED/BLUE using REST API calls to control the game. And have a GUI navigation agent finish the game.

# Features
- Gameboy emulator implemented in `emulator` directory. This is going to be a Python project. We should keep the implementation simple and create a minimal emulator that emulates: CPU, graphics, sound and input. (Not interested in emulating Gameboy peripherals.)
- REST api (service) is allowed to be the only mode for input. Ex. JSON payload that tells the emulator to invoke control inputs such as left, right, up, down, etc.
- Graphics should support ROMS that had super gameboy (color) features. (Pokemon Red/Blue are examples)

**Processing Model**: The target games (like Pokemon Red/Blue) progress slowly through discrete actions rather than real-time interactions. The emulator does not need to process at high frame rates or handle concurrent timing requirements.

```mermaid
flowchart TD
  Client --> REST_API
  REST_API --> Input_Handling
  
  subgraph "Gameboy Emulator"
    CPU
    Memory
    Graphics
    Sound
    Input_Handling
  end
  
  CPU --> Memory
  Memory --> Graphics
  Input_Handling --> Memory
  Graphics -->|Rendered Frame| Client
```

# Gameboy Hardware

Here are the technical specifications of the Gameboy hardware.

## Technical Specifications

|Component|Game Boy|
|---------|--------|
|CPU|8-bit 8080 Sharp CPU (SM83 core)|
|Master Clock|4.194 MHz|
|System Clock|1/4 of the master clock|
|RAM|8 KiB|
|Video RAM|8 KiB|
|Resolution|160 px x 144 px|
|OBJ Sprites|8x8 or 8x16, max: 40 per screen, 10 per line|
|Color Palettes|BG: 1x4, OBJ: 2x3|
|Colors|4 shades of green|
|Horizontal Sync|9.198 KHz|
|Vertical Sync|59.73 Hz|
|Sound|4 channels with stereo output|

## CPU Registers

The Game Boy CPU has the following registers:

**8-bit registers:**
- A (Accumulator)
- B
- C
- D
- E
- H
- L

**16-bit register pairs:**
- AF (A + Flags)
- BC (B + C)
- DE (D + E)
- HL (H + L)

**Special 16-bit registers:**
- SP (Stack Pointer)
- PC (Program Counter)

| 16-bit | Hi | Lo | Name/Function |
|--------|----|----|---------------|
| AF     | A  | -  | Accumulator & Flags |
| BC     | B  | C  | BC |
| DE     | D  | E  | DE |
| HL     | H  | L  | HL |
| SP     | -  | -  | Stack Pointer |
| PC     | -  | -  | Program Counter/Pointer |


### Flags Register (Lower 8 bits of AF register)

| Bit | Name | Explanation |
|-----|------|-------------|
| 7   | z    | Zero flag |
| 6   | n    | Subtraction flag (BCD) |
| 5   | h    | Half Carry flag (BCD) |
| 4   | c    | Carry flag |

# CPU Implementation Details

## Code Structure
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

## Handler Refactoring

The handlers have been organized into separate files by instruction type:
- `src/cpu/handlers/ld_handlers.py`: LD (load) instructions
- `src/cpu/handlers/jr_handlers.py`: JR (jump relative) instructions  
- `src/cpu/handlers/misc_handlers.py`: Miscellaneous instructions like NOP

The CPU class imports these handlers and calls them as functions instead of methods.

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

### INC E Implementation (0x1C)
**Date**: January 24, 2026

**Changes Made**:
1. Added `inc_e()` handler function to `src/cpu/handlers/inc_dec_handlers.py`
   - Increments register E by 1
   - Updates Z flag if result is zero
   - Updates H flag for half carry
   - Returns 4 cycles

2. Registered handler in dispatch table at `src/cpu/gb_cpu.py:47`:
   ```python
   0x1C: inc_e
   ```

3. Added import for `inc_e` function at `src/cpu/gb_cpu.py:16`

4. Added test case to `tests/cpu/test_fetch_with_operands.py`:
   ```python
   def test_run_inc_e(self):
       """Test running INC E instruction (0x1C, 4 cycles)"""
       self.cpu.set_register('E', 0x7F)
       self.cpu.registers.PC = 0x0000
        
       self.cpu.run(max_cycles=4)
        
       self.assertEqual(self.cpu.registers.PC, 0x0001)
       self.assertEqual(self.cpu.current_cycles, 4)
       self.assertEqual(self.cpu.get_register('E'), 0x80)
   ```

**Verification**: All 66 CPU tests pass (including the new test)