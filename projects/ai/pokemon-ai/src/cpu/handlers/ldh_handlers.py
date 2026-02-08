"""
LDH (Load Half) instruction handlers.

These instructions load to/from HRAM (High RAM) at addresses 0xFF00-0xFF7F
or I/O registers at addresses 0xFF80-0xFFFF.
"""


def ldh_ff_n_a(cpu, opcode_info):
    """LDH (n), A - Load A into HRAM/I/O at address 0xFF00+n"""
    # Get the operand value (a8) from first operand
    n = cpu.operand_values[0]["value"]

    # Calculate target address: 0xFF00 + n
    addr = 0xFF00 + n

    # Store A register into memory at calculated address
    a_value = cpu.get_register("A")
    cpu.memory.set_value(addr, a_value)

    return opcode_info["cycles"][0]


def ldh_a_ff_n(cpu, opcode_info):
    """LDH A, (n) - Load from HRAM/I/O at address 0xFF00+n into A"""
    # Get the operand value (a8) from second operand
    n = cpu.operand_values[1]["value"]

    # Calculate source address: 0xFF00 + n
    addr = 0xFF00 + n

    # Load from memory at calculated address into A register
    value = cpu.memory.get_value(addr)
    cpu.set_register("A", value)

    return opcode_info["cycles"][0]


def ldh_ff_c_a(cpu, opcode_info):
    """LDH (C), A - Load A into HRAM/I/O at address 0xFF00+C"""
    # Get the C register value from operand_values[1] (which is "C")
    c_value = cpu.get_register("C")

    # Calculate target address: 0xFF00 + C
    addr = 0xFF00 + c_value

    # Store A register into memory at calculated address
    a_value = cpu.get_register("A")
    cpu.memory.set_value(addr, a_value)

    return opcode_info["cycles"][0]


def ldh_a_ff_c(cpu, opcode_info):
    """LDH A, (C) - Load from HRAM/I/O at address 0xFF00+C into A"""
    # Get the C register value from operand_values[1] (which is "C")
    c_value = cpu.get_register("C")

    # Calculate source address: 0xFF00 + C
    addr = 0xFF00 + c_value

    # Load from memory at calculated address into A register
    value = cpu.memory.get_value(addr)
    cpu.set_register("A", value)

    return opcode_info["cycles"][0]
