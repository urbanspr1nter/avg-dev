#!/usr/bin/env python3
"""Debug RETI instruction."""

from src.cpu.gb_cpu import CPU

def debug_reti():
    """Debug RETI instruction."""
    cpu = CPU()
    
    # Set opcode at 0x0000
    cpu.memory.set_value(0x0000, 0xD9)  # RETI

    # Push return address onto stack
    return_addr = 0xBCDE
    cpu.push_word(return_addr)
    
    print(f"Stack pointer after push: {cpu.registers.SP:#06X}")
    print(f"Memory at SP: {cpu.memory.get_value(cpu.registers.SP):#04X}")
    print(f"Memory at SP+1: {cpu.memory.get_value(cpu.registers.SP + 1):#04X}")
    
    # Disable interrupts initially
    cpu.interrupts.ime = False
    cpu.registers.PC = 0x0000
    
    print(f"PC before RETI: {cpu.registers.PC:#06X}")
    print(f"IME before RETI: {cpu.interrupts.ime}")
    
    cpu.run(max_cycles=16)
    
    print(f"PC after RETI: {cpu.registers.PC:#06X}")
    print(f"IME after RETI: {cpu.interrupts.ime}")
    print(f"Current cycles: {cpu.current_cycles}")

if __name__ == "__main__":
    debug_reti()