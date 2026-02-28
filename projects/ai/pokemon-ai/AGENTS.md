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
  - `cb_handlers.py`: All 256 CB-prefixed instructions (rotates, shifts, SWAP, BIT, RES, SET)

- `Opcodes.json`: Full Game Boy opcode database (~2.5MB) — see "Opcodes.json Format" below

- `src/ppu/ppu.py`: PPU (Pixel Processing Unit) implementation
  - Holds 12 memory-mapped registers (0xFF40-0xFF4B)
  - Mode state machine: cycles through OAM Scan → Pixel Transfer → H-Blank → V-Blank
  - `tick(cycles)` called by CPU run loop after each instruction (same pattern as Timer)
  - Fires V-Blank interrupt (IF bit 0) when entering scanline 144
  - STAT interrupts (IF bit 1) with rising-edge detection for mode 0/1/2 and LYC match
  - Updates STAT mode bits (0-1) and LYC coincidence flag (bit 2)
  - LCD disabled check: tick() does nothing when LCDC bit 7 = 0
  - Background rendering: tile map lookup, 2bpp tile decoding, SCX/SCY scrolling, BGP palette, LCDC bit 4 addressing
  - Window rendering: overlay via WY/WX, LCDC bit 5 enable, LCDC bit 6 tile map, internal line counter
  - Sprite rendering: OAM scan (10/line limit), 8x8/8x16 modes, flips, palettes, priority, BG priority, transparency
  - 160×144 framebuffer with `get_framebuffer()` accessor and `render_ascii()` visualization

- `src/joypad/joypad.py`: Joypad (P1/JOYP register at 0xFF00)
  - 8 buttons in two groups: d-pad (right/left/up/down) and action (A/B/Select/Start)
  - Select-line multiplexing: CPU writes bits 4-5 to choose group, reads bits 0-3 for state
  - Active-low: 0 = pressed/selected, 1 = not pressed/not selected
  - `press(button)` / `release(button)` for external input (REST API integration)
  - Joypad interrupt (IF bit 4) on button press (1→0 transition)
  - Wired into memory bus via `load_joypad()` (same pattern as Timer/Serial)

- `src/frontend/pygame_frontend.py`: Pygame GUI frontend
  - `PygameFrontend` class — thin rendering layer over the GameBoy core
  - Frame-based timing: runs 70,224 T-cycles per frame (~16.74ms), sleeps for remainder to hit ~59.7 fps
  - Renders PPU framebuffer (shade values 0-3) using classic DMG green palette
  - Keyboard input mapped to joypad: WASD (d-pad), J/K (B/A), Enter (Start), Delete (Select)
  - Fast-forward: hold Space for 3x speed (runs 3 emulation frames per rendered frame)
  - GameBoy core has no knowledge of the frontend — frontend depends on core, not vice versa
  - Designed for modularity: future HTML5/REST frontend uses the same `gb.run()` / `gb.get_framebuffer()` / `gb.joypad.press()` interface

- `tests/cpu/`: Unit tests for CPU functionality (388 tests)
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
  - `test_cb_opcodes.py`: All 11 CB operation types with register, (HL), and flag tests
  - `test_cycle_accuracy.py`: Cycle accuracy verification for all opcodes against Opcodes.json (~500 checks)
- `src/cartridge/mbc.py`: MBC strategy classes (NoMBC, MBC1, MBC3)
  - Strategy pattern: Cartridge delegates banking logic to the correct MBC class
  - `NoMBC`: ROM ONLY (type 0x00), flat access, writes ignored
  - `MBC1`: 5-bit ROM bank, 2-bit RAM bank, banking mode, cartridge RAM
  - `MBC3`: 7-bit ROM bank, 4 RAM banks, optional RTC with latch mechanism
  - RTC uses host `time.time()` — latch freezes a snapshot into 5 registers (S/M/H/DL/DH)

- `tests/cartridge/`: Cartridge, MBC1, MBC3, and battery save tests (117 tests)
  - `test_gb_cartridge.py`: Header parsing, ROM access, checksum validation
  - `test_mbc1.py`: MBC1 ROM/RAM banking, mode select, edge cases
  - `test_mbc3.py`: MBC3 ROM banking (7-bit), RAM banking, RTC latch/halt/overflow, Memory integration
  - `test_battery.py`: Battery save/load (.sav files), has_battery detection, cross-bank persistence
- `tests/ppu/`: PPU tests (122 tests)
  - `test_ppu.py`: Register defaults/read/write, STAT mask, LY read-only, mode timing, V-Blank interrupt, LCD disabled, CPU integration, BG rendering, tile decoding, scrolling, tile addressing, window rendering, sprite rendering, STAT interrupts, OAM DMA, VRAM/OAM access restrictions, ASCII output
- `tests/joypad/`: Joypad tests (34 tests)
  - `test_joypad.py`: Register read/write, select-line multiplexing, all 8 buttons, press/release, interrupt firing, memory integration, GameBoy integration
- `tests/frontend/`: Frontend tests (19 tests)
  - `test_pygame_frontend.py`: DMG palette, key mapping, timing constants, frame cycle advancement, event handling (press/release/escape/quit), post-boot state

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
# All tests (743 tests)
python -m unittest discover tests/ -v

# CPU tests only (388 tests)
python -m unittest discover tests/cpu -v

# PPU tests (122 tests)
python -m unittest discover tests/ppu -v

# Joypad tests (34 tests)
python -m unittest discover tests/joypad -v

# Cartridge tests (117 tests)
python -m unittest discover tests/cartridge -v

# Frontend tests (19 tests)
python -m unittest discover tests/frontend -v

# Timer, serial, memory tests
python -m unittest discover tests/timer -v
python -m unittest discover tests/serial -v
python -m unittest discover tests/memory -v

# GameBoy integration tests
python -m unittest tests.test_gameboy -v

# Specific test file
python -m unittest tests.cpu.test_fetch_with_operands -v

# Specific test method
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
- **STOP**: 0x10 (stub — full behavior requires joypad + LCD subsystems)

### Total Implemented: ~245 unprefixed opcodes + 256 CB-prefixed opcodes (ALL opcodes complete)

## CB-Prefixed Instructions (COMPLETED)

All 256 CB-prefixed opcodes are implemented in `src/cpu/handlers/cb_handlers.py` using a data-driven approach: 11 handler functions dispatched via `cpu.cb_opcode_handlers` (a 256-entry table generated by `build_cb_dispatch()`).

### What are CB-prefixed instructions?

The Game Boy's SM83 CPU uses `0xCB` as an escape prefix to access a second 256-opcode table. When the CPU encounters `0xCB`, it reads the next byte and dispatches from the CB table instead of the normal table. This doubles the effective instruction set, providing full bit manipulation, shifts, and rotates on all registers — not just A.

### CB-prefixed instruction map

All 256 opcodes operate on 8 targets in a fixed order: **B, C, D, E, H, L, (HL), A** (encoded in bits 2-0 of the second byte).

| CB range    | Mnemonic | Count | Handler     | Description                                      | Flags   | Cycles (reg / (HL)) |
|-------------|----------|-------|-------------|--------------------------------------------------|---------|----------------------|
| 0x00-0x07   | RLC      | 8     | `cb_rlc`    | Rotate left circular (bit 7 → carry + bit 0)     | Z 0 0 C | 8 / 16               |
| 0x08-0x0F   | RRC      | 8     | `cb_rrc`    | Rotate right circular (bit 0 → carry + bit 7)    | Z 0 0 C | 8 / 16               |
| 0x10-0x17   | RL       | 8     | `cb_rl`     | Rotate left through carry                        | Z 0 0 C | 8 / 16               |
| 0x18-0x1F   | RR       | 8     | `cb_rr`     | Rotate right through carry                       | Z 0 0 C | 8 / 16               |
| 0x20-0x27   | SLA      | 8     | `cb_sla`    | Shift left arithmetic (0 → bit 0)               | Z 0 0 C | 8 / 16               |
| 0x28-0x2F   | SRA      | 8     | `cb_sra`    | Shift right arithmetic (bit 7 preserved)         | Z 0 0 C | 8 / 16               |
| 0x30-0x37   | SWAP     | 8     | `cb_swap`   | Swap upper and lower nibbles                     | Z 0 0 0 | 8 / 16               |
| 0x38-0x3F   | SRL      | 8     | `cb_srl`    | Shift right logical (0 → bit 7)                 | Z 0 0 C | 8 / 16               |
| 0x40-0x7F   | BIT      | 64    | `cb_bit`    | Test bit n (Z=1 if bit is 0)                    | Z 0 1 - | 8 / 12               |
| 0x80-0xBF   | RES      | 64    | `cb_res`    | Reset (clear) bit n                              | - - - - | 8 / 16               |
| 0xC0-0xFF   | SET      | 64    | `cb_set`    | Set bit n                                        | - - - - | 8 / 16               |

### Key differences from unprefixed rotates

The unprefixed RLCA/RRCA/RLA/RRA (0x07/0x0F/0x17/0x1F) only operate on A and **always clear Z**. The CB-prefixed RLC/RRC/RL/RR operate on any target and **set Z if result is zero**.

### Implementation details

- Handlers use `_read_target()` / `_write_target()` helpers that resolve register or (HL) indirect via the operand's `immediate` flag
- The dispatch table is generated by `build_cb_dispatch()` and stored as `cpu.cb_opcode_handlers`
- The `run()` loop sets `is_cb_prefix = True` when it sees `0xCB`, then dispatches from `cb_opcode_handlers` instead of `opcode_handlers`

## Current Test Status

743 tests passing as of February 28, 2026.

### Blargg Test ROM Validation

Both Blargg test ROMs pass, confirming full instruction correctness and cycle-accurate timing:
- **cpu_instrs**: All 11 sub-tests pass (special ops, interrupts, op sp/hl, op r/imm, op rp, ld r/r, jr/jp/call/ret/rst, misc instrs, op r/r, bit ops, op a/(hl))
- **instr_timing**: Passed

Run with: `python run_blargg.py rom/blargg/cpu_instrs.gb`

### Real Game Validation: Tetris

Tetris title screen renders correctly via ASCII framebuffer:
- Run with: `python run_tetris.py`
- ~12M T-cycles (~3s GB time) reaches the title screen with TETRIS logo, menu options, and copyright
- LCDC=0xD3 (LCD on, BG on, sprites on, window on)

Interactive pygame frontend:
- Run with: `python run_pygame.py rom/Tetris.gb` (optionally `--scale 4`)
- Renders at ~59.7 fps with classic DMG green palette
- WASD for d-pad, J/K for B/A, Enter for Start, Delete for Select, Escape to quit
- Hold Space for 3x fast-forward

### Real Game Validation: Pokemon Red

Pokemon Red loads and runs with MBC3 bank switching and cartridge RAM:
- Run with: `python run_pygame.py rom/Pokemon-Red.gb`
- MBC3+RAM+BATTERY (type 0x13), 1 MB ROM (64 banks), 32 KB RAM (4 banks)
- Battery saves: cartridge RAM saved to `.sav` file on quit (Escape, window close, or CTRL-C via try/finally)
- Save file loaded automatically on startup if present
- Save format: raw byte dump of cartridge RAM, compatible with other emulators

Two bugs were found and fixed during Tetris integration:
1. **VRAM/OAM access restrictions**: Must only apply when LCD is enabled (LCDC bit 7 = 1). When LCD is off, VRAM/OAM are freely accessible. Without this fix, games that disable LCD to write VRAM (standard practice) would have writes silently dropped if the PPU happened to be in mode 3 when LCD was turned off.
2. **Joypad register (0xFF00)**: Reading must return 0xCF (no buttons pressed) instead of 0x00 (which the game interprets as "all buttons pressed"). This was initially a temporary hack, now replaced by the full Joypad class.

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

### ✅ Phase 6: Real ROM Integration Testing (COMPLETED)
- ✅ Blargg cpu_instrs: all 11 sub-tests pass
- ✅ Blargg instr_timing: passed
- ✅ Fixed 3 instruction bugs found by Blargg tests:
  - ADD HL,HL: H flag half-carry check was always false (needed bit 11 carry test)
  - SBC A,A: H flag was hardcoded False (incorrect when carry set — nibble borrow occurs)
  - POP AF: lower 4 bits of F register must be masked to 0 (hardware constraint)
- ✅ MBC1 bank switching enables loading multi-bank ROMs like cpu_instrs

### 📋 Phase 7: Performance Optimization
- Optimize interrupt checking in CPU run loop
- Memory access optimizations for interrupt registers
- State caching improvements
- Benchmarking and profiling

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

## PPU (Pixel Processing Unit) Implementation

### ✅ Phase 1: Registers (COMPLETED)
- 12 memory-mapped registers (0xFF40-0xFF4B) in `src/ppu/ppu.py`
- Wired into memory bus via `load_ppu()` in `gb_memory.py`
- STAT write mask (bits 0-2 read-only, bit 7 always reads 1)
- LY read-only from CPU side (writing resets to 0)
- 35 register tests

### ✅ Phase 2: Mode State Machine (COMPLETED)
- `tick(cycles)` method advances PPU alongside CPU (same pattern as Timer)
- Mode transitions: OAM Scan (mode 2, 80 dots) → Pixel Transfer (mode 3, 172 dots) → H-Blank (mode 0, 204 dots)
- V-Blank (mode 1) at scanlines 144-153
- LY increments each 456-cycle scanline, wraps after 153
- STAT bits 0-1 reflect current mode, bit 2 reflects LYC==LY
- V-Blank interrupt (IF bit 0) fires when entering scanline 144
- LCD disabled check: tick() does nothing when LCDC bit 7 = 0
- CPU integration: `ppu.tick()` called from run loop (HALT idle + post-instruction)
- 26 mode state machine tests

### ✅ Phase 3: Background Rendering (COMPLETED)
- 160×144 framebuffer (list of lists, shade values 0-3) with `get_framebuffer()` accessor
- `_render_scanline()` called at mode 3→0 transition (dot 252) renders BG into framebuffer
- Tile data decoding: 2 bytes per row → 8 pixels of 2-bit color indices
- Tile map lookup with SCY/SCX scroll wrapping (256×256 BG map)
- LCDC bit 3: BG tile map selection (0x9800 or 0x9C00)
- LCDC bit 4: tile data addressing mode (unsigned 0x8000 vs signed 0x8800)
- BGP palette application (2-bit color indices → 4 shades of gray)
- `_tile_data_address()` static helper shared by BG and window
- `render_ascii()` ASCII visualization (shades: ` ░▒█`)
- `GameBoy.get_framebuffer()` accessor
- 16 new tests (framebuffer, tile decoding, scrolling, addressing, ASCII output)

### ✅ Phase 4: Window Rendering (COMPLETED)
- Window overlay in `_render_scanline()` renders on top of BG pixels
- LCDC bit 5: window enable/disable
- LCDC bit 6: window tile map selection (0x9800 or 0x9C00)
- WY/WX position registers (window screen X = WX - 7)
- Internal `_window_line` counter: increments only on scanlines where window rendered, resets at frame start
- Shares tile data addressing with BG (LCDC bit 4)
- 7 new tests (enable/disable, overlay, WY offset, line counter, tile map, addressing)

### ✅ Phase 5: Sprite Rendering (COMPLETED)
- `_render_sprites()` called after BG+window in `_render_scanline()`
- OAM scan: iterate 40 entries (0xFE00-0xFE9F), collect up to 10 sprites overlapping current scanline
- Sprite position: Y-16 for screen Y, X-8 for screen X
- 8x8 and 8x16 sprite modes (LCDC bit 2); 8x16 masks tile index bit 0
- OBP0/OBP1 palette selection (attr bit 4)
- X-flip (attr bit 5) and Y-flip (attr bit 6); Y-flip in 8x16 swaps top/bottom tiles
- Color 0 = transparent (BG shows through)
- BG priority (attr bit 7): sprite hidden behind non-zero BG color index
- Per-scanline `bg_indices` array tracks BG/window color indices for BG priority
- Sprite priority: stable sort by X position, lower OAM index wins ties
- Render in reverse priority order (lowest priority first, highest overwrites)
- Off-screen clipping (partial sprites at screen edges)
- 14 new tests (disable, basic, transparency, palettes, flips, 8x16, BG priority, limits, priority, clipping)

### ✅ Phase 6: STAT Interrupts (COMPLETED)
- `_stat_irq_line` boolean for rising-edge detection
- `_update_stat_irq()` evaluates OR of enabled STAT conditions, fires IF bit 1 on 0→1 transition
- STAT bit 3: H-Blank (mode 0) interrupt
- STAT bit 4: V-Blank (mode 1) interrupt
- STAT bit 5: OAM Scan (mode 2) interrupt
- STAT bit 6: LYC==LY coincidence interrupt
- Rising-edge prevents duplicate interrupts when multiple sources active simultaneously
- Called from `_set_mode()` and `_update_lyc_flag()`
- 12 new tests (mode 0/1/2 interrupts, LYC, disabled checks, rising edge, coexistence with V-Blank)

### ✅ Phase 7: OAM DMA Transfer (COMPLETED)
- `_dma_transfer(source_page)` copies 160 bytes from `source_page * 0x100` to OAM (0xFE00-0xFE9F)
- Triggered instantly on write to 0xFF46 (simplified — real hardware takes 640 T-cycles)
- Reads from raw memory array (correct for WRAM sources; cartridge ROM DMA can be enhanced later)
- 5 new tests (copy, different source, register readback, bounds, no-memory safety)

### ✅ Phase 8: VRAM/OAM Access Restrictions (COMPLETED)
- VRAM (0x8000-0x9FFF): reads return 0xFF during mode 3, writes silently dropped
- OAM (0xFE00-0xFE9F): reads return 0xFF during modes 2/3, writes silently dropped
- **LCD-disabled bypass**: restrictions only apply when LCDC bit 7 = 1 (LCD on). When LCD is off, VRAM/OAM are freely accessible — games disable LCD to write VRAM safely.
- Implemented in `gb_memory.py` `get_value()`/`set_value()` — only affects CPU-initiated access
- PPU internal rendering reads from `self._memory.memory[]` (raw array), unaffected by restrictions
- 10 new tests (VRAM read/write per mode, OAM read/write per mode, no-PPU fallback)
