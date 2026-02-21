#!/usr/bin/env python3
"""Debug stack pop wrap-around."""

from src.cpu.gb_cpu import CPU

def debug_stack_pop():
    """Debug stack pop wrap-around."""
    cpu = CPU()
    
    cpu.registers.SP = 0xFFFE
    cpu.memory.set_value(0xFFFE, 0x78)  # Low byte
    cpu.memory.set_value(0xFFFF, 0x56)  # High byte
    
    print(f"SP before pop: {cpu.registers.SP:#06X}")
    print(f"Memory at 0xFFFE: {cpu.memory.get_value(0xFFFE):#04X}")
    print(f"Memory at 0xFFFF: {cpu.memory.get_value(0xFFFF):#04X}")
    
    value = cpu.pop_word()
    
    print(f"SP after pop: {cpu.registers.SP:#06X}")
    print(f"Popped value: {value:#06X}")

if __name__ == "__main__":
    debug_stack_pop()