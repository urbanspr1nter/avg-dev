"""
Miscellaneous instruction handlers for Gameboy CPU.

These handlers implement instructions that don't fit into other categories,
such as NOP (no operation), HALT, STOP, etc.
"""


def nop(cpu, opcode_info):
    """NOP - No operation"""
    return opcode_info["cycles"][0]
