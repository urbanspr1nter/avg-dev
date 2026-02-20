"""
Miscellaneous instruction handlers for Gameboy CPU.

These handlers implement instructions that don't fit into other categories,
such as NOP (no operation), HALT, STOP, etc.
"""


def nop(cpu, opcode_info):
    """NOP - No operation"""
    return opcode_info["cycles"][0]


def scf(cpu, opcode_info):
    """SCF - Set Carry Flag"""
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", True)
    return opcode_info["cycles"][0]


def ccf(cpu, opcode_info):
    """CCF - Complement Carry Flag"""
    # Get current carry flag value
    current_carry = cpu.get_flag("C")
    # Toggle the carry flag
    cpu.set_flag("C", not current_carry)
    # Reset N and H flags
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    return opcode_info["cycles"][0]


def cpl(cpu, opcode_info):
    """CPL - Complement A register"""
    # Get current A value
    a_value = cpu.get_register("A")
    # Complement (bitwise NOT) the A register
    cpu.set_register("A", ~a_value & 0xFF)
    # Set N and H flags
    cpu.set_flag("N", True)
    cpu.set_flag("H", True)
    return opcode_info["cycles"][0]
