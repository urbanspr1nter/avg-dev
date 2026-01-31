"""
Arithmetic operation handlers for Gameboy CPU.

This module contains handlers for arithmetic operations like ADC (Add with Carry).
"""


def adc_a_b(cpu, opcode_info) -> int:
    """ADC A, B - Add B to A with carry"""
    a_value = cpu.get_register("A")
    b_value = cpu.get_register("B")
    carry_flag = cpu.get_flag("C")

    # Perform addition with carry
    result = a_value + b_value + (1 if carry_flag else 0)

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", False)
    cpu.set_flag(
        "H", ((a_value & 0xF) + (b_value & 0xF) + (1 if carry_flag else 0)) > 0xF
    )
    cpu.set_flag("C", result > 0xFF)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def adc_a_c(cpu, opcode_info) -> int:
    """ADC A, C - Add C to A with carry"""
    a_value = cpu.get_register("A")
    c_value = cpu.get_register("C")
    carry_flag = cpu.get_flag("C")

    # Perform addition with carry
    result = a_value + c_value + (1 if carry_flag else 0)

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", False)
    cpu.set_flag(
        "H", ((a_value & 0xF) + (c_value & 0xF) + (1 if carry_flag else 0)) > 0xF
    )
    cpu.set_flag("C", result > 0xFF)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def adc_a_d(cpu, opcode_info) -> int:
    """ADC A, D - Add D to A with carry"""
    a_value = cpu.get_register("A")
    d_value = cpu.get_register("D")
    carry_flag = cpu.get_flag("C")

    # Perform addition with carry
    result = a_value + d_value + (1 if carry_flag else 0)

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", False)
    cpu.set_flag(
        "H", ((a_value & 0xF) + (d_value & 0xF) + (1 if carry_flag else 0)) > 0xF
    )
    cpu.set_flag("C", result > 0xFF)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def adc_a_e(cpu, opcode_info) -> int:
    """ADC A, E - Add E to A with carry"""
    a_value = cpu.get_register("A")
    e_value = cpu.get_register("E")
    carry_flag = cpu.get_flag("C")

    # Perform addition with carry
    result = a_value + e_value + (1 if carry_flag else 0)

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", False)
    cpu.set_flag(
        "H", ((a_value & 0xF) + (e_value & 0xF) + (1 if carry_flag else 0)) > 0xF
    )
    cpu.set_flag("C", result > 0xFF)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def adc_a_h(cpu, opcode_info) -> int:
    """ADC A, H - Add H to A with carry"""
    a_value = cpu.get_register("A")
    h_value = cpu.get_register("H")
    carry_flag = cpu.get_flag("C")

    # Perform addition with carry
    result = a_value + h_value + (1 if carry_flag else 0)

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", False)
    cpu.set_flag(
        "H", ((a_value & 0xF) + (h_value & 0xF) + (1 if carry_flag else 0)) > 0xF
    )
    cpu.set_flag("C", result > 0xFF)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def adc_a_l(cpu, opcode_info) -> int:
    """ADC A, L - Add L to A with carry"""
    a_value = cpu.get_register("A")
    l_value = cpu.get_register("L")
    carry_flag = cpu.get_flag("C")

    # Perform addition with carry
    result = a_value + l_value + (1 if carry_flag else 0)

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", False)
    cpu.set_flag(
        "H", ((a_value & 0xF) + (l_value & 0xF) + (1 if carry_flag else 0)) > 0xF
    )
    cpu.set_flag("C", result > 0xFF)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def adc_a_a(cpu, opcode_info) -> int:
    """ADC A, A - Add A to A with carry"""
    a_value = cpu.get_register("A")
    carry_flag = cpu.get_flag("C")

    # Perform addition with carry
    result = a_value + a_value + (1 if carry_flag else 0)

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", False)
    cpu.set_flag(
        "H", ((a_value & 0xF) + (a_value & 0xF) + (1 if carry_flag else 0)) > 0xF
    )
    cpu.set_flag("C", result > 0xFF)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def adc_a_hl(cpu, opcode_info) -> int:
    """ADC A, (HL) - Add memory at HL to A with carry"""
    a_value = cpu.get_register("A")
    hl_address = cpu.get_register_pair("HL")
    hl_value = cpu.memory.get_value(hl_address)
    carry_flag = cpu.get_flag("C")

    # Perform addition with carry
    result = a_value + hl_value + (1 if carry_flag else 0)

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", False)
    cpu.set_flag(
        "H", ((a_value & 0xF) + (hl_value & 0xF) + (1 if carry_flag else 0)) > 0xF
    )
    cpu.set_flag("C", result > 0xFF)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def add_hl_bc(cpu, opcode_info) -> int:
    """ADD HL, BC - Add BC to HL"""
    hl_value = cpu.get_register_pair("HL")
    bc_value = cpu.get_register_pair("BC")

    # Perform addition
    result = hl_value + bc_value

    # Update flags
    cpu.set_flag("N", False)
    cpu.set_flag("H", (hl_value & 0xFFF) + (bc_value & 0xFFF) > 0xFFF)
    cpu.set_flag("C", result > 0xFFFF)

    # Store result in HL
    cpu.set_register_pair("HL", result & 0xFFFF)

    return opcode_info["cycles"][0]


def add_hl_de(cpu, opcode_info) -> int:
    """ADD HL, DE - Add DE to HL"""
    hl_value = cpu.get_register_pair("HL")
    de_value = cpu.get_register_pair("DE")

    # Perform addition
    result = hl_value + de_value

    # Update flags
    cpu.set_flag("N", False)
    cpu.set_flag("H", (hl_value & 0xFFF) + (de_value & 0xFFF) > 0xFFF)
    cpu.set_flag("C", result > 0xFFFF)

    # Store result in HL
    cpu.set_register_pair("HL", result & 0xFFFF)

    return opcode_info["cycles"][0]


def add_hl_hl(cpu, opcode_info) -> int:
    """ADD HL, HL - Add HL to HL (equivalent to HL << 1)"""
    hl_value = cpu.get_register_pair("HL")

    # Perform addition
    result = hl_value + hl_value

    # Update flags
    cpu.set_flag("N", False)
    cpu.set_flag("H", (hl_value & 0x7FF) > 0x7FF)
    cpu.set_flag("C", result > 0xFFFF)

    # Store result in HL
    cpu.set_register_pair("HL", result & 0xFFFF)

    return opcode_info["cycles"][0]


def add_hl_sp(cpu, opcode_info) -> int:
    """ADD HL, SP - Add SP to HL"""
    hl_value = cpu.get_register_pair("HL")
    sp_value = cpu.get_register("SP")

    # Perform addition
    result = hl_value + sp_value

    # Update flags
    cpu.set_flag("N", False)
    cpu.set_flag("H", (hl_value & 0xFFF) + (sp_value & 0xFFF) > 0xFFF)
    cpu.set_flag("C", result > 0xFFFF)

    # Store result in HL
    cpu.set_register_pair("HL", result & 0xFFFF)

    return opcode_info["cycles"][0]


def add_a_b(cpu, opcode_info) -> int:
    """ADD A, B - Add B to A"""
    a_value = cpu.get_register("A")
    b_value = cpu.get_register("B")

    # Perform addition
    result = a_value + b_value

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", (a_value & 0xF) + (b_value & 0xF) > 0xF)
    cpu.set_flag("C", result > 0xFF)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def add_a_c(cpu, opcode_info) -> int:
    """ADD A, C - Add C to A"""
    a_value = cpu.get_register("A")
    c_value = cpu.get_register("C")

    # Perform addition
    result = a_value + c_value

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", (a_value & 0xF) + (c_value & 0xF) > 0xF)
    cpu.set_flag("C", result > 0xFF)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def add_a_d(cpu, opcode_info) -> int:
    """ADD A, D - Add D to A"""
    a_value = cpu.get_register("A")
    d_value = cpu.get_register("D")

    # Perform addition
    result = a_value + d_value

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", (a_value & 0xF) + (d_value & 0xF) > 0xF)
    cpu.set_flag("C", result > 0xFF)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def add_a_e(cpu, opcode_info) -> int:
    """ADD A, E - Add E to A"""
    a_value = cpu.get_register("A")
    e_value = cpu.get_register("E")

    # Perform addition
    result = a_value + e_value

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", (a_value & 0xF) + (e_value & 0xF) > 0xF)
    cpu.set_flag("C", result > 0xFF)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def add_a_h(cpu, opcode_info) -> int:
    """ADD A, H - Add H to A"""
    a_value = cpu.get_register("A")
    h_value = cpu.get_register("H")

    # Perform addition
    result = a_value + h_value

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", (a_value & 0xF) + (h_value & 0xF) > 0xF)
    cpu.set_flag("C", result > 0xFF)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def add_a_l(cpu, opcode_info) -> int:
    """ADD A, L - Add L to A"""
    a_value = cpu.get_register("A")
    l_value = cpu.get_register("L")

    # Perform addition
    result = a_value + l_value

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", (a_value & 0xF) + (l_value & 0xF) > 0xF)
    cpu.set_flag("C", result > 0xFF)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def add_a_a(cpu, opcode_info) -> int:
    """ADD A, A - Add A to A (equivalent to A << 1)"""
    a_value = cpu.get_register("A")

    # Perform addition
    result = a_value + a_value

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", (a_value & 0xF) > 0x7)
    cpu.set_flag("C", result > 0xFF)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def add_a_n8(cpu, opcode_info) -> int:
    """ADD A, n8 - Add immediate byte to A"""
    a_value = cpu.get_register("A")
    # Get the immediate operand from operand_values
    n8_value = cpu.operand_values[1]["value"]

    # Perform addition
    result = a_value + n8_value

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", (a_value & 0xF) + (n8_value & 0xF) > 0xF)
    cpu.set_flag("C", result > 0xFF)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def add_a_hl(cpu, opcode_info) -> int:
    """ADD A, (HL) - Add memory at HL to A"""
    a_value = cpu.get_register("A")
    hl_address = cpu.get_register_pair("HL")
    hl_value = cpu.memory.get_value(hl_address)

    # Perform addition
    result = a_value + hl_value

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", (a_value & 0xF) + (hl_value & 0xF) > 0xF)
    cpu.set_flag("C", result > 0xFF)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]
