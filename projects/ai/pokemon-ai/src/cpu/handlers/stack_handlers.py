"""
Stack operation instruction handlers.

These instructions push 16-bit register pairs onto the stack or pop them off.
All PUSH instructions are 16 cycles, all POP instructions are 12 cycles (except POP AF which is also 12).
"""


def push_af(cpu, opcode_info):
    """PUSH AF - Push AF onto stack (16 cycles)"""
    af_value = cpu.get_register("AF")
    cpu.push_word(af_value)
    return opcode_info["cycles"][0]


def push_bc(cpu, opcode_info):
    """PUSH BC - Push BC onto stack (16 cycles)"""
    bc_value = cpu.get_register("BC")
    cpu.push_word(bc_value)
    return opcode_info["cycles"][0]


def push_de(cpu, opcode_info):
    """PUSH DE - Push DE onto stack (16 cycles)"""
    de_value = cpu.get_register("DE")
    cpu.push_word(de_value)
    return opcode_info["cycles"][0]


def push_hl(cpu, opcode_info):
    """PUSH HL - Push HL onto stack (16 cycles)"""
    hl_value = cpu.get_register("HL")
    cpu.push_word(hl_value)
    return opcode_info["cycles"][0]


def pop_af(cpu, opcode_info):
    """POP AF - Pop from stack into AF (12 cycles)"""
    af_value = cpu.pop_word()
    cpu.set_register("AF", af_value)
    return opcode_info["cycles"][0]


def pop_bc(cpu, opcode_info):
    """POP BC - Pop from stack into BC (12 cycles)"""
    bc_value = cpu.pop_word()
    cpu.set_register("BC", bc_value)
    return opcode_info["cycles"][0]


def pop_de(cpu, opcode_info):
    """POP DE - Pop from stack into DE (12 cycles)"""
    de_value = cpu.pop_word()
    cpu.set_register("DE", de_value)
    return opcode_info["cycles"][0]


def pop_hl(cpu, opcode_info):
    """POP HL - Pop from stack into HL (12 cycles)"""
    hl_value = cpu.pop_word()
    cpu.set_register("HL", hl_value)
    return opcode_info["cycles"][0]
