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
  - `arith_handlers.py`: ADD, ADC, SUB, SBC, ADD SP instructions
  - `bitwise_handlers.py`: AND, OR, XOR, CP instructions
  - `inc_dec_handlers.py`: INC, DEC (8-bit, 16-bit, and (HL) indirect)
  - `interrupt_handlers.py`: DI, EI, HALT
  - `jump_handlers.py`: JP, JP cc, JR, CALL, RET, RETI, RST instructions
  - `ld_handlers.py`: LD (load) immediate/indirect/absolute instructions
  - `ld_r1_r2_handlers.py`: LD r1, r2 register-to-register loads (0x40-0x7F)
  - `ldh_handlers.py`: LDH high-memory I/O instructions
  - `misc_handlers.py`: NOP, SCF, CCF, CPL, DAA
  - `rotate_handlers.py`: RLCA, RRCA, RLA, RRA (unprefixed rotate A)
  - `stack_handlers.py`: PUSH, POP instructions

- `Opcodes.json`: Full Game Boy opcode database (~2.5MB) — see "Opcodes.json Format" below

- `tests/cpu/`: Unit tests for CPU functionality (328 tests)
  - `test_fetch_with_operands.py`: Tests for opcodes with operands
  - `test_fetch_opcodes_only.py`: Tests for opcodes without operands
  - `test_registers.py`: Register access tests
  - `test_stack.py`: Stack operations tests
  - `test_flags.py`: Flag manipulation tests
  - `test_bitwise_ops.py`: Bitwise operation tests
  - `test_rotate_ops.py`: Rotation/shift operation tests
  - `test_ld_r1_r2.py`: LD r1, r2 instruction tests
  - `test_jump_instructions.py`: JP, JR, CALL, RET, RETI, RST tests
  - `test_interrupts.py`: Interrupt system tests (Phases 1-5)
  - `test_load_store.py`: Load/store instruction tests
  - `test_remaining_opcodes.py`: Conditional JP, ADC n8, ADD SP, DAA tests

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
- **ADC A, r**: 0x88-0x8F, 0xCE (9 instructions)
- **SUB A, r**: 0x90-0x97, 0xD6 (9 instructions)
- **SBC A, r**: 0x98-0x9F, 0xDE (9 instructions)
- **ADD SP, e8**: 0xE8
- **ADD HL, rr**: 0x09, 0x19, 0x29, 0x39

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
- **LD rr, n16**: 0x01, 0x11, 0x21, 0x31 (16-bit immediate loads: BC, DE, HL, SP)
- **LD (HL), n8**: 0x36
- **LD r1, r2**: 0x40-0x7F (56 register-to-register loads)
- **LD A, (BC)**: 0x0A, **LD A, (DE)**: 0x1A (register-indirect loads)
- **LD (BC), A**: 0x02, **LD (DE), A**: 0x12 (register-indirect stores)
- **LD (HL+), A**: 0x22, **LD A, (HL+)**: 0x2A (auto-increment)
- **LD (HL-), A**: 0x32, **LD A, (HL-)**: 0x3A (auto-decrement)
- **LD (a16), A**: 0xEA, **LD A, (a16)**: 0xFA (absolute address)
- **LD (a16), SP**: 0x08 (store SP to absolute address)
- **LD SP, HL**: 0xF9
- **LD HL, SP+e8**: 0xF8 (SP + signed offset into HL, sets H/C flags)
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
- **INC r8**: 0x04, 0x0C, 0x14, 0x1C, 0x24, 0x2C, 0x3C (INC B, C, D, E, H, L, A)
- **DEC r8**: 0x05, 0x0D, 0x15, 0x1D, 0x25, 0x2D, 0x3D (DEC B, C, D, E, H, L, A)
- **INC rr**: 0x03, 0x13, 0x23, 0x33 (INC BC, DE, HL, SP)
- **DEC rr**: 0x0B, 0x1B, 0x2B, 0x3B (DEC BC, DE, HL, SP)
- **INC (HL)**: 0x34, **DEC (HL)**: 0x35

### Interrupt Instructions
- **DI**: 0xF3 (Disable Interrupts, immediate)
- **EI**: 0xFB (Enable Interrupts with 1-instruction delay)
- **HALT**: 0x76 (Halt CPU until interrupt)

### Miscellaneous
- **NOP**: 0x00
- **SCF**: 0x37 (Set Carry Flag)
- **CCF**: 0x3F (Complement Carry Flag)
- **CPL**: 0x2F (Complement A register)
- **DAA**: 0x27 (Decimal Adjust Accumulator)
- **STOP**: 0x10

### Total Implemented: ~245 unprefixed opcodes (all valid unprefixed opcodes complete)

## Not Yet Implemented: CB-Prefixed Instructions

The only remaining CPU opcodes are the 256 CB-prefixed instructions. These are accessed via a `0xCB` prefix byte — the run loop already handles fetching the second byte and looking it up in `Opcodes.json["cbprefixed"]`. What's missing is the handlers and a `cb_opcode_handlers` dispatch table.

### What are CB-prefixed instructions?

The Game Boy's SM83 CPU uses `0xCB` as an escape prefix to access a second 256-opcode table. When the CPU encounters `0xCB`, it reads the next byte and dispatches from the CB table instead of the normal table. This doubles the effective instruction set, providing full bit manipulation, shifts, and rotates on all registers — not just A.

### CB-prefixed instruction map

All 256 opcodes operate on 8 targets in a fixed order: **B, C, D, E, H, L, (HL), A** (encoded in bits 2-0 of the second byte).

| CB range    | Mnemonic | Count | Description                                      | Flags   | Cycles (reg / (HL)) |
|-------------|----------|-------|--------------------------------------------------|---------|----------------------|
| 0x00-0x07   | RLC      | 8     | Rotate left circular (bit 7 → carry + bit 0)     | Z 0 0 C | 8 / 16               |
| 0x08-0x0F   | RRC      | 8     | Rotate right circular (bit 0 → carry + bit 7)    | Z 0 0 C | 8 / 16               |
| 0x10-0x17   | RL       | 8     | Rotate left through carry                        | Z 0 0 C | 8 / 16               |
| 0x18-0x1F   | RR       | 8     | Rotate right through carry                       | Z 0 0 C | 8 / 16               |
| 0x20-0x27   | SLA      | 8     | Shift left arithmetic (0 → bit 0)               | Z 0 0 C | 8 / 16               |
| 0x28-0x2F   | SRA      | 8     | Shift right arithmetic (bit 7 preserved)         | Z 0 0 C | 8 / 16               |
| 0x30-0x37   | SWAP     | 8     | Swap upper and lower nibbles                     | Z 0 0 0 | 8 / 16               |
| 0x38-0x3F   | SRL      | 8     | Shift right logical (0 → bit 7)                 | Z 0 0 C | 8 / 16               |
| 0x40-0x7F   | BIT      | 64    | Test bit n (Z=1 if bit is 0)                    | Z 0 1 - | 8 / 12               |
| 0x80-0xBF   | RES      | 64    | Reset (clear) bit n                              | - - - - | 8 / 16               |
| 0xC0-0xFF   | SET      | 64    | Set bit n                                        | - - - - | 8 / 16               |

### Key differences from unprefixed rotates

The unprefixed RLCA/RRCA/RLA/RRA (0x07/0x0F/0x17/0x1F) only operate on A and **always clear Z**. The CB-prefixed RLC/RRC/RL/RR operate on any target and **set Z if result is zero**.

### Implementation approach

The CB table is highly regular (11 operations x 8 targets). Recommended approach:
1. Create `src/cpu/handlers/cb_handlers.py`
2. Write one helper function per operation type (e.g., `_rlc(cpu, target)`) that reads the target value, performs the operation, writes back, and sets flags
3. Generate 256 thin wrapper functions or use a data-driven dispatch table that maps each CB opcode to (operation, target) pairs
4. Add a `cb_opcode_handlers` dict to the CPU class, dispatched from the existing CB-prefix path in `run()`
5. For (HL) targets: read from `memory[HL]`, operate, write back — same logic but with memory access

## Current Test Status

328 tests passing as of February 21, 2026.

## Interrupt System Implementation Plan

The Game Boy interrupt system is being implemented in multiple phases:

### ✅ Phase 1: Core Infrastructure (COMPLETED)
- DI (0xF3), EI (0xFB), HALT (0x76) instruction handlers
- RETI (0xD9) handler with proper IME flag management
- Interrupt service routine implementation (20 cycles)
- Basic interrupt priority system (V-Blank > LCD STAT > Timer > Serial > Joypad)
- Interrupt checking in CPU run loop
- 7 comprehensive interrupt tests

### ✅ Phase 2: Memory-Mapped Registers (COMPLETED)
- IF register (0xFF0F) - Interrupt Flag register
- IE register (0xFFFF) - Interrupt Enable register
- Memory-mapped register handlers in gb_memory.py
- Register access methods with proper 5-bit masking
- Stack operation fixes for register address conflicts
- All memory-mapped register functionality working

### ✅ Phase 3: EI Instruction Delay - Core Implementation (COMPLETED)
- ✅ Add ime_pending flag to Interrupts class
- ✅ Modify EI handler to set pending flag instead of immediate enable
- ✅ Update CPU run loop to handle delayed IME enable
- ✅ Basic tests for delayed interrupt enabling
- ✅ 3 comprehensive tests added for EI delay functionality
- ✅ All 10 interrupt tests passing

### ✅ Phase 4: EI Delay - Edge Cases and HALT Bug Fix (COMPLETED)
- ✅ Fixed DI to cancel pending EI (ime_pending cleared)
- ✅ Fixed run loop post-instruction EI delay check (respects DI cancellation)
- ✅ Implemented HALT bug: IME=0 + pending interrupt → next byte read twice
- ✅ Added halt_bug flag to Interrupts class (one-shot, consumed by run loop)
- ✅ Refactored HALT handler for all 4 cases (IME=1/0 x pending/not-pending)
- ✅ Added halted idle loop to run() — CPU consumes 4 cycles/iteration while halted
- ✅ Removed halted guard from check_interrupts() (now managed by run loop)
- ✅ 6 new edge-case tests: EI+DI cancel, DI+EI delay, double EI, HALT bug,
  HALT wake on external interrupt, HALT wake with IME=0
- ✅ All 282 tests passing (24 interrupt tests, 1 skipped for CB-prefixed)

### ✅ Phase 5: Advanced Interrupt Scenarios (COMPLETED)
- ✅ Nested interrupt prevention (IME=False blocks second interrupt during service)
- ✅ Interrupt chaining after RETI (V-Blank → RETI → Timer fires automatically)
- ✅ HALT wakes on each of 5 interrupt types (parameterized test)
- ✅ HALT wake with IME=0 (wakes but doesn't service, type-agnostic)
- ✅ Stack boundary: default SP=0xFFFE interrupt push doesn't corrupt IF/IE
- ✅ Stack wrap: SP=0x0001 push wraps to 0xFFFF, correctly corrupts IE (faithful to hardware)
- ✅ Multiple pending: only serviced interrupt's IF bit cleared, others preserved
- ✅ Partial IE mask: only IE-enabled interrupts fire, disabled ones ignored
- ✅ 8 new tests, all 290 tests passing (32 interrupt tests, 1 skipped for CB-prefixed)

### 📋 Phase 6: Real ROM Integration Testing
- Test with actual Game Boy ROMs that use interrupts
- Validate interrupt-driven game mechanics
- Cycle-accurate timing verification
- Compatibility testing with various ROMs

### 📋 Phase 7: Performance Optimization
- Optimize interrupt checking in CPU run loop
- Memory access optimizations for interrupt registers
- State caching improvements
- Benchmarking and profiling

### 📋 Phase 8: Final Validation and Documentation
- Complete edge case test suite
- Comprehensive documentation of interrupt system
- Final regression testing
- Integration validation with full emulator

## Interrupt System Architecture

### Memory-Mapped Registers
- **IF (Interrupt Flag) at 0xFF0F**: Indicates pending interrupts
  - Bit 0: V-Blank interrupt
  - Bit 1: LCD STAT interrupt
  - Bit 2: Timer interrupt
  - Bit 3: Serial interrupt
  - Bit 4: Joypad interrupt
  - Bits 5-7: Unused (always 0)

- **IE (Interrupt Enable) at 0xFFFF**: Enables interrupt sources
  - Same bit layout as IF register
  - Only lower 5 bits are valid

### Interrupt Priority
1. V-Blank (highest priority)
2. LCD STAT
3. Timer
4. Serial
5. Joypad (lowest priority)

### Interrupt Service Routine
- Takes 20 cycles to service an interrupt
- Disables IME during service
- Clears specific IF bit
- Jumps to fixed address based on interrupt type
- RETI (0xD9) returns and re-enables interrupts

### Key Implementation Details
- Interrupts only service when IME (Interrupt Master Enable) is true
- HALT instruction wakes up immediately if interrupts are pending
- EI instruction has 1-instruction delay before enabling interrupts
- DI cancels any pending EI (clears both ime and ime_pending)
- HALT bug: when HALT executes with IME=0 and (IF & IE) != 0, the CPU does NOT
  halt and does NOT service the interrupt — instead the next instruction byte is
  read twice (halt_bug flag causes run loop to undo one PC increment after fetch)
- When halted with no pending interrupt, CPU idles at 4 cycles/iteration until
  any interrupt becomes pending (IF & IE != 0), then wakes regardless of IME
- All memory accesses to 0xFF0F/0xFFFF go through register handlers
