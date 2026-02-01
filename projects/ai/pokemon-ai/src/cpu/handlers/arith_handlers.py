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


def sub_a_b(cpu, opcode_info) -> int:
    """SUB A, B - Subtract B from A"""
    a_value = cpu.get_register("A")
    b_value = cpu.get_register("B")

    # Perform subtraction
    result = a_value - b_value

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (b_value & 0xF))
    cpu.set_flag("C", result < 0)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def sub_a_c(cpu, opcode_info) -> int:
    """SUB A, C - Subtract C from A"""
    a_value = cpu.get_register("A")
    c_value = cpu.get_register("C")

    # Perform subtraction
    result = a_value - c_value

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (c_value & 0xF))
    cpu.set_flag("C", result < 0)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def sub_a_d(cpu, opcode_info) -> int:
    """SUB A, D - Subtract D from A"""
    a_value = cpu.get_register("A")
    d_value = cpu.get_register("D")

    # Perform subtraction
    result = a_value - d_value

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (d_value & 0xF))
    cpu.set_flag("C", result < 0)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def sub_a_e(cpu, opcode_info) -> int:
    """SUB A, E - Subtract E from A"""
    a_value = cpu.get_register("A")
    e_value = cpu.get_register("E")

    # Perform subtraction
    result = a_value - e_value

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (e_value & 0xF))
    cpu.set_flag("C", result < 0)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def sub_a_h(cpu, opcode_info) -> int:
    """SUB A, H - Subtract H from A"""
    a_value = cpu.get_register("A")
    h_value = cpu.get_register("H")

    # Perform subtraction
    result = a_value - h_value

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (h_value & 0xF))
    cpu.set_flag("C", result < 0)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def sub_a_l(cpu, opcode_info) -> int:
    """SUB A, L - Subtract L from A"""
    a_value = cpu.get_register("A")
    l_value = cpu.get_register("L")

    # Perform subtraction
    result = a_value - l_value

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (l_value & 0xF))
    cpu.set_flag("C", result < 0)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def sub_a_hl(cpu, opcode_info) -> int:
    """SUB A, (HL) - Subtract memory at HL from A"""
    a_value = cpu.get_register("A")
    hl_address = cpu.get_register_pair("HL")
    hl_value = cpu.memory.get_value(hl_address)

    # Perform subtraction
    result = a_value - hl_value

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (hl_value & 0xF))
    cpu.set_flag("C", result < 0)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def sub_a_a(cpu, opcode_info) -> int:
    """SUB A, A - Subtract A from A (always results in 0)"""
    a_value = cpu.get_register("A")

    # Perform subtraction
    result = a_value - a_value

    # Update flags
    cpu.set_flag("Z", True)  # Result is always zero
    cpu.set_flag("N", True)
    cpu.set_flag("H", False)  # No half carry when subtracting same value
    cpu.set_flag("C", False)  # No carry when subtracting same value

    # Store result in A (always 0)
    cpu.set_register("A", 0x00)

    return opcode_info["cycles"][0]


def sub_a_n8(cpu, opcode_info) -> int:
    """SUB A, n8 - Subtract immediate byte from A"""
    a_value = cpu.get_register("A")
    # Get the immediate operand from operand_values
    n8_value = cpu.operand_values[1]["value"]

    # Perform subtraction
    result = a_value - n8_value

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (n8_value & 0xF))
    cpu.set_flag("C", result < 0)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def sbc_a_b(cpu, opcode_info) -> int:
    """SBC A, B - Subtract B from A with carry"""
    a_value = cpu.get_register("A")
    b_value = cpu.get_register("B")
    carry_flag = cpu.get_flag("C")

    # Perform subtraction with carry
    result = a_value - b_value - (1 if carry_flag else 0)

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (b_value & 0xF) + (1 if carry_flag else 0))
    cpu.set_flag("C", result < 0)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def sbc_a_c(cpu, opcode_info) -> int:
    """SBC A, C - Subtract C from A with carry"""
    a_value = cpu.get_register("A")
    c_value = cpu.get_register("C")
    carry_flag = cpu.get_flag("C")

    # Perform subtraction with carry
    result = a_value - c_value - (1 if carry_flag else 0)

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (c_value & 0xF) + (1 if carry_flag else 0))
    cpu.set_flag("C", result < 0)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def sbc_a_d(cpu, opcode_info) -> int:
    """SBC A, D - Subtract D from A with carry"""
    a_value = cpu.get_register("A")
    d_value = cpu.get_register("D")
    carry_flag = cpu.get_flag("C")

    # Perform subtraction with carry
    result = a_value - d_value - (1 if carry_flag else 0)

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (d_value & 0xF) + (1 if carry_flag else 0))
    cpu.set_flag("C", result < 0)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def sbc_a_e(cpu, opcode_info) -> int:
    """SBC A, E - Subtract E from A with carry"""
    a_value = cpu.get_register("A")
    e_value = cpu.get_register("E")
    carry_flag = cpu.get_flag("C")

    # Perform subtraction with carry
    result = a_value - e_value - (1 if carry_flag else 0)

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (e_value & 0xF) + (1 if carry_flag else 0))
    cpu.set_flag("C", result < 0)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def sbc_a_h(cpu, opcode_info) -> int:
    """SBC A, H - Subtract H from A with carry"""
    a_value = cpu.get_register("A")
    h_value = cpu.get_register("H")
    carry_flag = cpu.get_flag("C")

    # Perform subtraction with carry
    result = a_value - h_value - (1 if carry_flag else 0)

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (h_value & 0xF) + (1 if carry_flag else 0))
    cpu.set_flag("C", result < 0)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def sbc_a_l(cpu, opcode_info) -> int:
    """SBC A, L - Subtract L from A with carry"""
    a_value = cpu.get_register("A")
    l_value = cpu.get_register("L")
    carry_flag = cpu.get_flag("C")

    # Perform subtraction with carry
    result = a_value - l_value - (1 if carry_flag else 0)

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (l_value & 0xF) + (1 if carry_flag else 0))
    cpu.set_flag("C", result < 0)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def sbc_a_hl(cpu, opcode_info) -> int:
    """SBC A, (HL) - Subtract memory at HL from A with carry"""
    a_value = cpu.get_register("A")
    hl_address = cpu.get_register_pair("HL")
    hl_value = cpu.memory.get_value(hl_address)
    carry_flag = cpu.get_flag("C")

    # Perform subtraction with carry
    result = a_value - hl_value - (1 if carry_flag else 0)

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (hl_value & 0xF) + (1 if carry_flag else 0))
    cpu.set_flag("C", result < 0)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def sbc_a_a(cpu, opcode_info) -> int:
    """SBC A, A - Subtract A from A with carry (always results in 0 or 0xFF)"""
    a_value = cpu.get_register("A")
    carry_flag = cpu.get_flag("C")

    # Perform subtraction with carry
    result = a_value - a_value - (1 if carry_flag else 0)

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", False)
    cpu.set_flag("C", result < 0)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def sbc_a_n8(cpu, opcode_info) -> int:
    """SBC A, n8 - Subtract immediate byte from A with carry"""
    a_value = cpu.get_register("A")
    # Get the immediate operand from operand_values
    n8_value = cpu.operand_values[1]["value"]
    carry_flag = cpu.get_flag("C")

    # Perform subtraction with carry
    result = a_value - n8_value - (1 if carry_flag else 0)

    # Update flags
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (n8_value & 0xF) + (1 if carry_flag else 0))
    cpu.set_flag("C", result < 0)

    # Store result in A
    cpu.set_register("A", result & 0xFF)

    return opcode_info["cycles"][0]


def and_a_b(cpu, opcode_info) -> int:
    """AND A, B - Bitwise AND between A and B"""
    a_value = cpu.get_register("A")
    b_value = cpu.get_register("B")

    # Perform bitwise AND
    result = a_value & b_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", True)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def and_a_c(cpu, opcode_info) -> int:
    """AND A, C - Bitwise AND between A and C"""
    a_value = cpu.get_register("A")
    c_value = cpu.get_register("C")

    # Perform bitwise AND
    result = a_value & c_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", True)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def and_a_d(cpu, opcode_info) -> int:
    """AND A, D - Bitwise AND between A and D"""
    a_value = cpu.get_register("A")
    d_value = cpu.get_register("D")

    # Perform bitwise AND
    result = a_value & d_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", True)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def and_a_e(cpu, opcode_info) -> int:
    """AND A, E - Bitwise AND between A and E"""
    a_value = cpu.get_register("A")
    e_value = cpu.get_register("E")

    # Perform bitwise AND
    result = a_value & e_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", True)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def and_a_h(cpu, opcode_info) -> int:
    """AND A, H - Bitwise AND between A and H"""
    a_value = cpu.get_register("A")
    h_value = cpu.get_register("H")

    # Perform bitwise AND
    result = a_value & h_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", True)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def and_a_l(cpu, opcode_info) -> int:
    """AND A, L - Bitwise AND between A and L"""
    a_value = cpu.get_register("A")
    l_value = cpu.get_register("L")

    # Perform bitwise AND
    result = a_value & l_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", True)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def and_a_hl(cpu, opcode_info) -> int:
    """AND A, (HL) - Bitwise AND between A and memory at HL"""
    a_value = cpu.get_register("A")
    hl_address = cpu.get_register_pair("HL")
    hl_value = cpu.memory.get_value(hl_address)

    # Perform bitwise AND
    result = a_value & hl_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", True)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def and_a_a(cpu, opcode_info) -> int:
    """AND A, A - Bitwise AND between A and A (no change to A)"""
    a_value = cpu.get_register("A")

    # Perform bitwise AND
    result = a_value & a_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", True)
    cpu.set_flag("C", False)

    # Store result in A (same as original value)
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def and_a_n8(cpu, opcode_info) -> int:
    """AND A, n8 - Bitwise AND between A and immediate byte"""
    a_value = cpu.get_register("A")
    # Get the immediate operand from operand_values
    n8_value = cpu.operand_values[1]["value"]

    # Perform bitwise AND
    result = a_value & n8_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", True)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def or_a_b(cpu, opcode_info) -> int:
    """OR A, B - Bitwise OR between A and B"""
    a_value = cpu.get_register("A")
    b_value = cpu.get_register("B")

    # Perform bitwise OR
    result = a_value | b_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def or_a_c(cpu, opcode_info) -> int:
    """OR A, C - Bitwise OR between A and C"""
    a_value = cpu.get_register("A")
    c_value = cpu.get_register("C")

    # Perform bitwise OR
    result = a_value | c_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def or_a_d(cpu, opcode_info) -> int:
    """OR A, D - Bitwise OR between A and D"""
    a_value = cpu.get_register("A")
    d_value = cpu.get_register("D")

    # Perform bitwise OR
    result = a_value | d_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def or_a_e(cpu, opcode_info) -> int:
    """OR A, E - Bitwise OR between A and E"""
    a_value = cpu.get_register("A")
    e_value = cpu.get_register("E")

    # Perform bitwise OR
    result = a_value | e_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def or_a_h(cpu, opcode_info) -> int:
    """OR A, H - Bitwise OR between A and H"""
    a_value = cpu.get_register("A")
    h_value = cpu.get_register("H")

    # Perform bitwise OR
    result = a_value | h_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def or_a_l(cpu, opcode_info) -> int:
    """OR A, L - Bitwise OR between A and L"""
    a_value = cpu.get_register("A")
    l_value = cpu.get_register("L")

    # Perform bitwise OR
    result = a_value | l_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def or_a_hl(cpu, opcode_info) -> int:
    """OR A, (HL) - Bitwise OR between A and memory at HL"""
    a_value = cpu.get_register("A")
    hl_address = cpu.get_register_pair("HL")
    hl_value = cpu.memory.get_value(hl_address)

    # Perform bitwise OR
    result = a_value | hl_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def or_a_a(cpu, opcode_info) -> int:
    """OR A, A - Bitwise OR between A and A (no change to A)"""
    a_value = cpu.get_register("A")

    # Perform bitwise OR
    result = a_value | a_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    # Store result in A (same as original value)
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def or_a_n8(cpu, opcode_info) -> int:
    """OR A, n8 - Bitwise OR between A and immediate byte"""
    a_value = cpu.get_register("A")
    # Get the immediate operand from operand_values
    n8_value = cpu.operand_values[1]["value"]

    # Perform bitwise OR
    result = a_value | n8_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def xor_a_b(cpu, opcode_info) -> int:
    """XOR A, B - Bitwise XOR between A and B"""
    a_value = cpu.get_register("A")
    b_value = cpu.get_register("B")

    # Perform bitwise XOR
    result = a_value ^ b_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def xor_a_c(cpu, opcode_info) -> int:
    """XOR A, C - Bitwise XOR between A and C"""
    a_value = cpu.get_register("A")
    c_value = cpu.get_register("C")

    # Perform bitwise XOR
    result = a_value ^ c_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def xor_a_d(cpu, opcode_info) -> int:
    """XOR A, D - Bitwise XOR between A and D"""
    a_value = cpu.get_register("A")
    d_value = cpu.get_register("D")

    # Perform bitwise XOR
    result = a_value ^ d_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def xor_a_e(cpu, opcode_info) -> int:
    """XOR A, E - Bitwise XOR between A and E"""
    a_value = cpu.get_register("A")
    e_value = cpu.get_register("E")

    # Perform bitwise XOR
    result = a_value ^ e_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def xor_a_h(cpu, opcode_info) -> int:
    """XOR A, H - Bitwise XOR between A and H"""
    a_value = cpu.get_register("A")
    h_value = cpu.get_register("H")

    # Perform bitwise XOR
    result = a_value ^ h_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def xor_a_l(cpu, opcode_info) -> int:
    """XOR A, L - Bitwise XOR between A and L"""
    a_value = cpu.get_register("A")
    l_value = cpu.get_register("L")

    # Perform bitwise XOR
    result = a_value ^ l_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def xor_a_hl(cpu, opcode_info) -> int:
    """XOR A, (HL) - Bitwise XOR between A and memory at HL"""
    a_value = cpu.get_register("A")
    hl_address = cpu.get_register_pair("HL")
    hl_value = cpu.memory.get_value(hl_address)

    # Perform bitwise XOR
    result = a_value ^ hl_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def xor_a_a(cpu, opcode_info) -> int:
    """XOR A, A - Bitwise XOR between A and A (always results in 0)"""
    a_value = cpu.get_register("A")

    # Perform bitwise XOR
    result = a_value ^ a_value

    # Update flags
    cpu.set_flag("Z", True)  # Result is always zero
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    # Store result in A (always 0)
    cpu.set_register("A", 0x00)

    return opcode_info["cycles"][0]


def xor_a_n8(cpu, opcode_info) -> int:
    """XOR A, n8 - Bitwise XOR between A and immediate byte"""
    a_value = cpu.get_register("A")
    # Get the immediate operand from operand_values
    n8_value = cpu.operand_values[1]["value"]

    # Perform bitwise XOR
    result = a_value ^ n8_value

    # Update flags
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    # Store result in A
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]


def cp_a_b(cpu, opcode_info) -> int:
    """CP A, B - Compare A with B (subtract but don't store result)"""
    a_value = cpu.get_register("A")
    b_value = cpu.get_register("B")

    # Perform subtraction for comparison (but don't store result)
    result = a_value - b_value

    # Update flags based on subtraction
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (b_value & 0xF))
    cpu.set_flag("C", result < 0)

    # Don't store result in A

    return opcode_info["cycles"][0]


def cp_a_c(cpu, opcode_info) -> int:
    """CP A, C - Compare A with C (subtract but don't store result)"""
    a_value = cpu.get_register("A")
    c_value = cpu.get_register("C")

    # Perform subtraction for comparison (but don't store result)
    result = a_value - c_value

    # Update flags based on subtraction
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (c_value & 0xF))
    cpu.set_flag("C", result < 0)

    # Don't store result in A

    return opcode_info["cycles"][0]


def cp_a_d(cpu, opcode_info) -> int:
    """CP A, D - Compare A with D (subtract but don't store result)"""
    a_value = cpu.get_register("A")
    d_value = cpu.get_register("D")

    # Perform subtraction for comparison (but don't store result)
    result = a_value - d_value

    # Update flags based on subtraction
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (d_value & 0xF))
    cpu.set_flag("C", result < 0)

    # Don't store result in A

    return opcode_info["cycles"][0]


def cp_a_e(cpu, opcode_info) -> int:
    """CP A, E - Compare A with E (subtract but don't store result)"""
    a_value = cpu.get_register("A")
    e_value = cpu.get_register("E")

    # Perform subtraction for comparison (but don't store result)
    result = a_value - e_value

    # Update flags based on subtraction
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (e_value & 0xF))
    cpu.set_flag("C", result < 0)

    # Don't store result in A

    return opcode_info["cycles"][0]


def cp_a_h(cpu, opcode_info) -> int:
    """CP A, H - Compare A with H (subtract but don't store result)"""
    a_value = cpu.get_register("A")
    h_value = cpu.get_register("H")

    # Perform subtraction for comparison (but don't store result)
    result = a_value - h_value

    # Update flags based on subtraction
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (h_value & 0xF))
    cpu.set_flag("C", result < 0)

    # Don't store result in A

    return opcode_info["cycles"][0]


def cp_a_l(cpu, opcode_info) -> int:
    """CP A, L - Compare A with L (subtract but don't store result)"""
    a_value = cpu.get_register("A")
    l_value = cpu.get_register("L")

    # Perform subtraction for comparison (but don't store result)
    result = a_value - l_value

    # Update flags based on subtraction
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (l_value & 0xF))
    cpu.set_flag("C", result < 0)

    # Don't store result in A

    return opcode_info["cycles"][0]


def cp_a_hl(cpu, opcode_info) -> int:
    """CP A, (HL) - Compare A with memory at HL (subtract but don't store result)"""
    a_value = cpu.get_register("A")
    hl_address = cpu.get_register_pair("HL")
    hl_value = cpu.memory.get_value(hl_address)

    # Perform subtraction for comparison (but don't store result)
    result = a_value - hl_value

    # Update flags based on subtraction
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (hl_value & 0xF))
    cpu.set_flag("C", result < 0)

    # Don't store result in A

    return opcode_info["cycles"][0]


def cp_a_a(cpu, opcode_info) -> int:
    """CP A, A - Compare A with A (always equal)"""
    a_value = cpu.get_register("A")

    # Perform subtraction for comparison (but don't store result)
    result = a_value - a_value

    # Update flags based on subtraction
    cpu.set_flag("Z", True)  # Result is always zero
    cpu.set_flag("N", True)
    cpu.set_flag("H", False)  # No half carry when subtracting same value
    cpu.set_flag("C", False)  # No carry when subtracting same value

    # Don't store result in A

    return opcode_info["cycles"][0]


def cp_a_n8(cpu, opcode_info) -> int:
    """CP A, n8 - Compare A with immediate byte (subtract but don't store result)"""
    a_value = cpu.get_register("A")
    # Get the immediate operand from operand_values
    n8_value = cpu.operand_values[1]["value"]

    # Perform subtraction for comparison (but don't store result)
    result = a_value - n8_value

    # Update flags based on subtraction
    cpu.set_flag("Z", (result & 0xFF) == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", (a_value & 0xF) < (n8_value & 0xF))
    cpu.set_flag("C", result < 0)

    # Don't store result in A

    return opcode_info["cycles"][0]
