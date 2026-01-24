# CPU Opcode Handlers

This directory contains the opcode handlers for the Gameboy emulator, organized by instruction category.

## Structure

Handlers are organized into separate files based on instruction type:

### Current Handler Files

1. **ld_handlers.py** - LD (Load) instructions
   - Loads values between registers and memory
   - Examples: `LD BC, n16`, `LD D, n8`

2. **jr_handlers.py** - JR (Jump Relative) instructions  
   - Conditional and unconditional relative jumps
   - Examples: `JR NZ, e8`, `JR NC, e8`

3. **misc_handlers.py** - Miscellaneous instructions
   - Instructions that don't fit other categories
   - Examples: `NOP`, `HALT`, `STOP`

### Handler Signature

All handlers follow this signature:
```python
def handler_name(cpu, opcode_info) -> int:
    """Mnemonic - Brief description"""
    # Access cpu.operand_values for operands
    # Update registers/memory via cpu.set_register(), cpu.memory.set_value()
    return cycles_used  # From opcode_info["cycles"][index]
```

### Parameters

- `cpu`: The CPU instance (provides access to registers, memory, operand_values)
- `opcode_info`: Dictionary containing opcode metadata from Opcodes.json
  - `mnemonic`: Instruction name
  - `bytes`: Total instruction size
  - `cycles`: Array of cycle counts
  - `operands`: List of operands
  - `flags`: Flag affect information

### Accessing Operands

Operands are pre-fetched into `cpu.operand_values` as a list of dictionaries:
```python
[
    {
        "name": str,       # Operand name (e.g., "n16", "BC", "A")
        "value": int|str,  # Numeric value or register name
        "immediate": bool, # True for immediate values, False for memory references
        "type": str        # One of: "immediate_value", "immediate_address", 
                            #          "register", "register_indirect"
    }
]
```

## Adding New Handlers

1. Create or update the appropriate handler file based on instruction type
2. Add the new handler function with proper signature
3. Update the dispatch table in `src/cpu/gb_cpu.py` to map opcode to handler
4. Write tests in `tests/cpu/` directory
5. Run tests: `python -m unittest discover tests/cpu -v`

## Benefits of This Structure

- **Better organization**: Related instructions are grouped together
- **Easier maintenance**: Changes to one instruction type don't affect others
- **Clearer codebase**: New contributors can quickly find relevant handlers
- **Modular testing**: Each handler file can be tested independently