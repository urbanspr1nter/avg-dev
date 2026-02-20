# AGENTS.md

This file contains information for AI agents working on this codebase.

## Project Overview

The pokemon-ai project is a Gameboy emulator with a REST API interface, designed to play Pokemon RED/BLUE using AI-controlled inputs. The emulator focuses on CPU, graphics, sound, and input emulation without peripherals.

## Key Files

### Emulator Core
- `emulator/DESIGN.md`: Comprehensive design document for the Gameboy emulator
  - Contains hardware specifications, CPU architecture, memory map
  - Documents opcode handling approach using dispatch tables
  - Includes pseudocode for CPU execution loop

### Code Structure
- `src/cpu/gb_cpu.py`: Main CPU implementation
  - Contains `Registers`, `Interrupts`, and `CPU` classes
  - Uses dispatch table pattern for opcode handling
  - Operand values pre-fetched into `cpu.operand_values` list by the `run()` loop
  - The `run()` method is the core execution loop — see "Critical Implementation Notes" below

- `src/cpu/handlers/`: Handler functions organized by instruction type
  - `arith_handlers.py`: ADD, SUB, SBC instructions
  - `bitwise_handlers.py`: AND, OR, XOR, CP instructions
  - `inc_dec_handlers.py`: INC instructions
  - `jump_handlers.py`: JP, JR, CALL, RET, RETI, RST instructions
  - `ld_handlers.py`: LD (load) immediate instructions
  - `ld_r1_r2_handlers.py`: LD r1, r2 register-to-register loads (0x40-0x7F)
  - `ldh_handlers.py`: LDH high-memory I/O instructions
  - `misc_handlers.py`: NOP and other miscellaneous instructions
  - `rotate_handlers.py`: RLC, RRC, RL, RR (rotate A register)
  - `stack_handlers.py`: PUSH, POP instructions

- `Opcodes.json`: Full Game Boy opcode database (~2.5MB) — see "Opcodes.json Format" below

- `tests/cpu/`: Unit tests for CPU functionality
  - `test_fetch_with_operands.py`: Tests for opcodes with operands
  - `test_fetch_opcodes_only.py`: Tests for opcodes without operands
  - `test_registers.py`: Register access tests
  - `test_stack.py`: Stack operations tests
  - `test_flags.py`: Flag manipulation tests
  - `test_bitwise_ops.py`: Bitwise operation tests
  - `test_rotate_ops.py`: Rotation/shift operation tests
  - `test_ld_r1_r2.py`: LD r1, r2 instruction tests
  - `test_jump_instructions.py`: JP, JR, CALL, RET, RETI, RST tests

## Critical Implementation Notes

**READ THIS SECTION CAREFULLY before making any changes to the CPU.**

### 1. The `run()` Loop Operand Fetching — DO NOT CHANGE THE CONDITION

The `run()` method in `gb_cpu.py` fetches operands for each instruction. The critical condition that decides how to handle each operand is:

```python
if "bytes" in operand:
    # This operand needs data fetched from the instruction stream (n8, n16, e8, a16)
    ...
else:
    # This is a register operand (B, C, D, E, H, L, A, HL, etc.)
    ...
```

**DO NOT** change `if "bytes" in operand:` to `if operand_immediate:` or any other condition. The reason: in Opcodes.json, register operands like `B` in `LD B, n8` have `"immediate": true`, which means "direct register reference" — NOT that it needs bytes fetched from memory. The `"bytes"` field is the ONLY reliable way to distinguish between operands that require instruction stream reads and those that don't.

### 2. Condition Code "C" vs Register "C" Ambiguity

In Opcodes.json, the operand name `"C"` can mean either:
- **Register C** (in instructions like `LD C, n8`)
- **Carry flag condition** (in instructions like `RET C`, `JP C, a16`)

The `run()` loop skips condition code operands (Z, NZ, C, NC) so they don't pollute `operand_values`. But it MUST only skip them for conditional instructions. The guard is:

```python
is_conditional = len(opcode_info.get("cycles", [])) > 1
if is_conditional and operand_name in ["Z", "NZ", "C", "NC"]:
    pass  # Skip condition codes
```

If you remove the `is_conditional` guard, instructions like `LD C, n8` will break because register C gets skipped.

### 3. Handler Function Signature

All handler functions use this signature — note the first parameter is `cpu`, NOT `self`:

```python
def handler_name(cpu, opcode_info) -> int:
    """Mnemonic - Brief description"""
    # Access pre-fetched operands from cpu.operand_values
    # Update registers via cpu.set_register(), cpu.get_register()
    # Update memory via cpu.memory.set_value(), cpu.memory.get_value()
    # Update flags via cpu.set_flag(), cpu.get_flag()
    return opcode_info["cycles"][0]  # or cycles[1] for not-taken conditional branch
```

Handlers are standalone functions (not methods), imported and stored in the dispatch table as function references.

### 4. Dispatch Table Format

The dispatch table maps raw opcode byte values to handler functions:

```python
self.opcode_handlers = {
    0x00: nop,
    0x07: rlc_a,
    0xC3: jp_nn,
    # ...
}
```

Handlers are called as: `handler(self, opcode_info)` where `self` is the CPU instance.

### 5. Opcode-to-Instruction Mapping — VERIFY BEFORE IMPLEMENTING

Always verify the correct opcode-to-mnemonic mapping before implementing. A previous agent incorrectly mapped:
- `0x27` → rotate handler (WRONG — 0x27 is DAA, Decimal Adjust Accumulator)
- `0x2F` → rotate handler (WRONG — 0x2F is CPL, Complement A)

Use the Pan Docs or Opcodes.json as the source of truth. Common gotcha opcodes:
- `0x07` = RLCA, `0x0F` = RRCA, `0x17` = RLA, `0x1F` = RRA
- `0x27` = DAA, `0x2F` = CPL, `0x37` = SCF, `0x3F` = CCF

### 6. Conditional Instruction Cycle Counts

Conditional instructions have TWO cycle counts in `opcode_info["cycles"]`:
- `cycles[0]` = cycles when condition is MET (action taken)
- `cycles[1]` = cycles when condition is NOT met (action skipped)

For example, conditional RET instructions:
- **RET NZ/Z/NC/C**: 20 cycles when taken, 8 when not taken (NOT 16 as you might expect)

Always check Opcodes.json for the correct cycle counts.

### 7. Opcodes.json Format

Each operand entry in Opcodes.json has these fields:
- `"name"`: Operand name (e.g., "B", "n8", "a16", "HL")
- `"immediate"`: Boolean
  - `true` for registers = direct register reference
  - `false` for registers = register indirect (memory access via register, e.g., `(HL)`)
  - `true` for data operands = immediate value
  - `false` for data operands = memory address
- `"bytes"`: Integer (ONLY present for operands that need instruction stream reads)
  - `1` for n8, e8
  - `2` for n16, a16

The `"bytes"` field is what distinguishes "fetch from instruction stream" from "use register directly".

## Implementation Patterns

### Opcode Handler Pattern
```python
def handler_name(cpu, opcode_info) -> int:
    """Mnemonic - Brief description"""
    # Access immediate operands from cpu.operand_values
    # Update registers/memory via cpu.set_register(), cpu.memory.set_value()
    return opcode_info["cycles"][0]  # or cycles[1] for conditional branch not taken
```

### Testing Approach
- Use unittest framework
- Test files in `tests/cpu/` directory
- Each test verifies:
  - Correct PC advancement based on opcode size
  - Accurate cycle counting
  - Proper register/memory state changes
  - Operand handling for instructions with operands
  - Flag states after execution

## Code Conventions

1. **Naming**: Use snake_case for function names, follow Gameboy assembly mnemonics
2. **Handler param**: Always `cpu` as first parameter, never `self`
3. **Testing**: Comprehensive unit tests for all new functionality
4. **Cycle Accuracy**: Must match official Gameboy CPU cycle counts from Opcodes.json
5. **Memory Safety**: All memory accesses must be bounded (0x0000-0xFFFF)
6. **Searching**: Use Kagi Search MCP tool if prompted to search for things outside of your knowledge base or repo

## Approach to Implementation

To make the work more digestible and manageable, we follow this approach:

1. **Break down by instruction type**: Group related opcodes together (e.g., all INC instructions, all LD instructions)
2. **Use handler files**: Organize handlers by category in `src/cpu/handlers/` directory
3. **Implement one opcode at a time**: Focus on completing one simple opcode before moving to the next
4. **Write comprehensive tests**: Each new opcode gets its own test case
5. **Verify all tests pass**: After each implementation, run the full test suite to ensure no regressions
6. **Verify opcode mapping**: Always cross-reference Opcodes.json to confirm the opcode byte matches the mnemonic

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
- **RLCA**: 0x07 (Rotate A Left, old bit 7 to Carry)
- **RRCA**: 0x0F (Rotate A Right, old bit 0 to Carry)
- **RLA**: 0x17 (Rotate A Left through Carry)
- **RRA**: 0x1F (Rotate A Right through Carry)

### Load Instructions
- **LD r, n8**: Various (8-bit immediate loads)
- **LD (HL), n8**: 0x36
- **LD r1, r2**: 0x40-0x7F (56 register-to-register loads)
- **PUSH rr**: 0xC5, 0xD5, 0xE5, 0xF5 (4 instructions)
- **POP rr**: 0xC1, 0xD1, 0xE1, 0xF1 (4 instructions)
- **LDH (n), A**: 0xE0
- **LDH (C), A**: 0xE2
- **LDH A, (n)**: 0xF0
- **LDH A, (C)**: 0xF2

### Jump/Control Flow Instructions
- **JP nn**: 0xC3 (unconditional jump)
- **JP cc, nn**: 0xC2, 0xCA, 0xD2, 0xDA (conditional jumps)
- **JP HL**: 0xE9
- **JR e8**: 0x18 (unconditional relative jump)
- **JR cc, e8**: 0x20, 0x28, 0x30, 0x38 (conditional relative jumps)
- **CALL nn**: 0xCD (unconditional call)
- **CALL cc, nn**: 0xC4, 0xCC, 0xD4, 0xDC (conditional calls)
- **RET**: 0xC9 (unconditional return)
- **RET cc**: 0xC0, 0xC8, 0xD0, 0xD8 (conditional returns)
- **RETI**: 0xD9 (return and enable interrupts)
- **RST**: 0xC7, 0xCF, 0xD7, 0xDF, 0xE7, 0xEF, 0xF7, 0xFF (8 restart vectors)

### Increment/Decrement
- **INC r**: 0x04, 0x0C, 0x14, 0x1C (INC B, C, D, E)

### Miscellaneous
- **NOP**: 0x00
- **SCF**: 0x37 (Set Carry Flag)
- **CCF**: 0x3F (Complement Carry Flag)
- **CPL**: 0x2F (Complement A register)

### Total Implemented: ~207 opcodes

## Not Yet Implemented (Key Missing Opcodes)

These are important opcodes still needed for a functional emulator:
- **DAA** (0x27): Decimal Adjust Accumulator
- **HALT** (0x76): Halt CPU until interrupt
- **DI** (0xF3): Disable Interrupts
- **EI** (0xFB): Enable Interrupts
- **LD HL, n16** (0x21) and other 16-bit loads (0x01, 0x11, 0x31)
- **HALT** (0x76): Halt CPU until interrupt
- **DI** (0xF3): Disable Interrupts
- **EI** (0xFB): Enable Interrupts
- **HALT** (0x76): Halt CPU until interrupt
- **DI** (0xF3): Disable Interrupts
- **EI** (0xFB): Enable Interrupts
- **LD HL, n16** (0x21) and other 16-bit loads (0x01, 0x11, 0x31)
- **INC/DEC** for H, L, A, (HL), and 16-bit register pairs
- **ADC** instructions
- **CB-prefixed** instructions (bit operations, shifts, rotates on all registers)
- **LD (a16), A** / **LD A, (a16)** and other memory load variants
- **LD (HL+), A** / **LD (HL-), A** and reverse variants

## Current Test Status

258 tests passing as of February 20, 2026.
