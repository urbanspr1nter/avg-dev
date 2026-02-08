"""
Bitwise operation handlers for Gameboy CPU.

This module contains handler functions for AND, OR, XOR, and CP instructions.
All bitwise operations are 8-bit operations on register A.
"""


def and_a_b(cpu, opcode_info) -> int:
    """AND A, B - Bitwise AND of A and B, result in A"""
    a_val = cpu.get_register("A")
    b_val = cpu.get_register("B")
    result = a_val & b_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 1 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", True)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def and_a_c(cpu, opcode_info) -> int:
    """AND A, C - Bitwise AND of A and C, result in A"""
    a_val = cpu.get_register("A")
    c_val = cpu.get_register("C")
    result = a_val & c_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 1 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", True)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def and_a_d(cpu, opcode_info) -> int:
    """AND A, D - Bitwise AND of A and D, result in A"""
    a_val = cpu.get_register("A")
    d_val = cpu.get_register("D")
    result = a_val & d_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 1 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", True)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def and_a_e(cpu, opcode_info) -> int:
    """AND A, E - Bitwise AND of A and E, result in A"""
    a_val = cpu.get_register("A")
    e_val = cpu.get_register("E")
    result = a_val & e_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 1 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", True)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def and_a_h(cpu, opcode_info) -> int:
    """AND A, H - Bitwise AND of A and H, result in A"""
    a_val = cpu.get_register("A")
    h_val = cpu.get_register("H")
    result = a_val & h_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 1 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", True)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def and_a_l(cpu, opcode_info) -> int:
    """AND A, L - Bitwise AND of A and L, result in A"""
    a_val = cpu.get_register("A")
    l_val = cpu.get_register("L")
    result = a_val & l_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 1 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", True)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def and_a_hl(cpu, opcode_info) -> int:
    """AND A, (HL) - Bitwise AND of A and memory at HL, result in A"""
    a_val = cpu.get_register("A")
    hl_addr = cpu.get_register("HL")
    mem_val = cpu.memory.get_value(hl_addr)
    result = a_val & mem_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 1 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", True)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def and_a_a(cpu, opcode_info) -> int:
    """AND A, A - Bitwise AND of A with itself, result in A (always A)"""
    a_val = cpu.get_register("A")
    result = a_val & a_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 1 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", True)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def and_a_n8(cpu, opcode_info) -> int:
    """AND A, n8 - Bitwise AND of A and immediate 8-bit value, result in A"""
    a_val = cpu.get_register("A")
    n8_val = cpu.operand_values[1]["value"]
    result = a_val & n8_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 1 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", True)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def or_a_b(cpu, opcode_info) -> int:
    """OR A, B - Bitwise OR of A and B, result in A"""
    a_val = cpu.get_register("A")
    b_val = cpu.get_register("B")
    result = a_val | b_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 0 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def or_a_c(cpu, opcode_info) -> int:
    """OR A, C - Bitwise OR of A and C, result in A"""
    a_val = cpu.get_register("A")
    c_val = cpu.get_register("C")
    result = a_val | c_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 0 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def or_a_d(cpu, opcode_info) -> int:
    """OR A, D - Bitwise OR of A and D, result in A"""
    a_val = cpu.get_register("A")
    d_val = cpu.get_register("D")
    result = a_val | d_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 0 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def or_a_e(cpu, opcode_info) -> int:
    """OR A, E - Bitwise OR of A and E, result in A"""
    a_val = cpu.get_register("A")
    e_val = cpu.get_register("E")
    result = a_val | e_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 0 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def or_a_h(cpu, opcode_info) -> int:
    """OR A, H - Bitwise OR of A and H, result in A"""
    a_val = cpu.get_register("A")
    h_val = cpu.get_register("H")
    result = a_val | h_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 0 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def or_a_l(cpu, opcode_info) -> int:
    """OR A, L - Bitwise OR of A and L, result in A"""
    a_val = cpu.get_register("A")
    l_val = cpu.get_register("L")
    result = a_val | l_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 0 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def or_a_hl(cpu, opcode_info) -> int:
    """OR A, (HL) - Bitwise OR of A and memory at HL, result in A"""
    a_val = cpu.get_register("A")
    hl_addr = cpu.get_register("HL")
    mem_val = cpu.memory.get_value(hl_addr)
    result = a_val | mem_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 0 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def or_a_a(cpu, opcode_info) -> int:
    """OR A, A - Bitwise OR of A with itself, result in A (always A)"""
    a_val = cpu.get_register("A")
    result = a_val | a_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 0 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def or_a_n8(cpu, opcode_info) -> int:
    """OR A, n8 - Bitwise OR of A and immediate 8-bit value, result in A"""
    a_val = cpu.get_register("A")
    n8_val = cpu.operand_values[1]["value"]
    result = a_val | n8_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 0 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def xor_a_b(cpu, opcode_info) -> int:
    """XOR A, B - Bitwise XOR of A and B, result in A"""
    a_val = cpu.get_register("A")
    b_val = cpu.get_register("B")
    result = a_val ^ b_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 0 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def xor_a_c(cpu, opcode_info) -> int:
    """XOR A, C - Bitwise XOR of A and C, result in A"""
    a_val = cpu.get_register("A")
    c_val = cpu.get_register("C")
    result = a_val ^ c_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 0 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def xor_a_d(cpu, opcode_info) -> int:
    """XOR A, D - Bitwise XOR of A and D, result in A"""
    a_val = cpu.get_register("A")
    d_val = cpu.get_register("D")
    result = a_val ^ d_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 0 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def xor_a_e(cpu, opcode_info) -> int:
    """XOR A, E - Bitwise XOR of A and E, result in A"""
    a_val = cpu.get_register("A")
    e_val = cpu.get_register("E")
    result = a_val ^ e_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 0 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def xor_a_h(cpu, opcode_info) -> int:
    """XOR A, H - Bitwise XOR of A and H, result in A"""
    a_val = cpu.get_register("A")
    h_val = cpu.get_register("H")
    result = a_val ^ h_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 0 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def xor_a_l(cpu, opcode_info) -> int:
    """XOR A, L - Bitwise XOR of A and L, result in A"""
    a_val = cpu.get_register("A")
    l_val = cpu.get_register("L")
    result = a_val ^ l_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 0 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def xor_a_hl(cpu, opcode_info) -> int:
    """XOR A, (HL) - Bitwise XOR of A and memory at HL, result in A"""
    a_val = cpu.get_register("A")
    hl_addr = cpu.get_register("HL")
    mem_val = cpu.memory.get_value(hl_addr)
    result = a_val ^ mem_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 0 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def xor_a_a(cpu, opcode_info) -> int:
    """XOR A, A - Bitwise XOR of A with itself, result in A (always 0)"""
    a_val = cpu.get_register("A")
    result = a_val ^ a_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 0 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def xor_a_n8(cpu, opcode_info) -> int:
    """XOR A, n8 - Bitwise XOR of A and immediate 8-bit value, result in A"""
    a_val = cpu.get_register("A")
    n8_val = cpu.operand_values[1]["value"]
    result = a_val ^ n8_val

    # Set A to the result
    cpu.set_register("A", result)

    # Update flags: Z - 1 if result is zero, N - 0 (always), H - 0 (always), C - 0 (always)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", False)

    return opcode_info["cycles"][0]


def cp_a_b(cpu, opcode_info) -> int:
    """CP A, B - Compare A with B (A - B), update flags only"""
    a_val = cpu.get_register("A")
    b_val = cpu.get_register("B")

    # Perform subtraction for comparison
    result = a_val - b_val

    # Update flags: Z - 1 if result is zero, N - 1 (always), H - half borrow, C - borrow
    # Half borrow occurs when lower 4 bits of B > lower 4 bits of A
    half_borrow = (a_val & 0x0F) < (b_val & 0x0F)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", half_borrow)
    cpu.set_flag("C", result < 0)  # Borrow occurred if result is negative

    return opcode_info["cycles"][0]


def cp_a_c(cpu, opcode_info) -> int:
    """CP A, C - Compare A with C (A - C), update flags only"""
    a_val = cpu.get_register("A")
    c_val = cpu.get_register("C")

    # Perform subtraction for comparison
    result = a_val - c_val

    # Update flags: Z - 1 if result is zero, N - 1 (always), H - half borrow, C - borrow
    # Half borrow occurs when lower 4 bits of C > lower 4 bits of A
    half_borrow = (a_val & 0x0F) < (c_val & 0x0F)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", half_borrow)
    cpu.set_flag("C", result < 0)  # Borrow occurred if result is negative

    return opcode_info["cycles"][0]


def cp_a_d(cpu, opcode_info) -> int:
    """CP A, D - Compare A with D (A - D), update flags only"""
    a_val = cpu.get_register("A")
    d_val = cpu.get_register("D")

    # Perform subtraction for comparison
    result = a_val - d_val

    # Update flags: Z - 1 if result is zero, N - 1 (always), H - half borrow, C - borrow
    # Half borrow occurs when lower 4 bits of D > lower 4 bits of A
    half_borrow = (a_val & 0x0F) < (d_val & 0x0F)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", half_borrow)
    cpu.set_flag("C", result < 0)  # Borrow occurred if result is negative

    return opcode_info["cycles"][0]


def cp_a_e(cpu, opcode_info) -> int:
    """CP A, E - Compare A with E (A - E), update flags only"""
    a_val = cpu.get_register("A")
    e_val = cpu.get_register("E")

    # Perform subtraction for comparison
    result = a_val - e_val

    # Update flags: Z - 1 if result is zero, N - 1 (always), H - half borrow, C - borrow
    # Half borrow occurs when lower 4 bits of E > lower 4 bits of A
    half_borrow = (a_val & 0x0F) < (e_val & 0x0F)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", half_borrow)
    cpu.set_flag("C", result < 0)  # Borrow occurred if result is negative

    return opcode_info["cycles"][0]


def cp_a_h(cpu, opcode_info) -> int:
    """CP A, H - Compare A with H (A - H), update flags only"""
    a_val = cpu.get_register("A")
    h_val = cpu.get_register("H")

    # Perform subtraction for comparison
    result = a_val - h_val

    # Update flags: Z - 1 if result is zero, N - 1 (always), H - half borrow, C - borrow
    # Half borrow occurs when lower 4 bits of H > lower 4 bits of A
    half_borrow = (a_val & 0x0F) < (h_val & 0x0F)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", half_borrow)
    cpu.set_flag("C", result < 0)  # Borrow occurred if result is negative

    return opcode_info["cycles"][0]


def cp_a_l(cpu, opcode_info) -> int:
    """CP A, L - Compare A with L (A - L), update flags only"""
    a_val = cpu.get_register("A")
    l_val = cpu.get_register("L")

    # Perform subtraction for comparison
    result = a_val - l_val

    # Update flags: Z - 1 if result is zero, N - 1 (always), H - half borrow, C - borrow
    # Half borrow occurs when lower 4 bits of L > lower 4 bits of A
    half_borrow = (a_val & 0x0F) < (l_val & 0x0F)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", half_borrow)
    cpu.set_flag("C", result < 0)  # Borrow occurred if result is negative

    return opcode_info["cycles"][0]


def cp_a_hl(cpu, opcode_info) -> int:
    """CP A, (HL) - Compare A with memory at HL (A - (HL)), update flags only"""
    a_val = cpu.get_register("A")
    hl_addr = cpu.get_register("HL")
    mem_val = cpu.memory.get_value(hl_addr)

    # Perform subtraction for comparison
    result = a_val - mem_val

    # Update flags: Z - 1 if result is zero, N - 1 (always), H - half borrow, C - borrow
    # Half borrow occurs when lower 4 bits of memory > lower 4 bits of A
    half_borrow = (a_val & 0x0F) < (mem_val & 0x0F)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", half_borrow)
    cpu.set_flag("C", result < 0)  # Borrow occurred if result is negative

    return opcode_info["cycles"][0]


def cp_a_a(cpu, opcode_info) -> int:
    """CP A, A - Compare A with itself (A - A), update flags only"""
    a_val = cpu.get_register("A")

    # Perform subtraction for comparison
    result = a_val - a_val

    # Update flags: Z - 1 if result is zero, N - 1 (always), H - half borrow, C - borrow
    # Half borrow occurs when lower 4 bits of A > lower 4 bits of A (never)
    half_borrow = (a_val & 0x0F) < (a_val & 0x0F)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", half_borrow)
    cpu.set_flag("C", result < 0)  # Borrow occurred if result is negative

    return opcode_info["cycles"][0]


def cp_a_n8(cpu, opcode_info) -> int:
    """CP A, n8 - Compare A with immediate value (A - n8), update flags only"""
    a_val = cpu.get_register("A")
    n8_val = cpu.operand_values[1]["value"]

    # Perform subtraction for comparison
    result = a_val - n8_val

    # Update flags: Z - 1 if result is zero, N - 1 (always), H - half borrow, C - borrow
    # Half borrow occurs when lower 4 bits of n8 > lower 4 bits of A
    half_borrow = (a_val & 0x0F) < (n8_val & 0x0F)
    cpu.set_flag("Z", result == 0)
    cpu.set_flag("N", True)
    cpu.set_flag("H", half_borrow)
    cpu.set_flag("C", result < 0)  # Borrow occurred if result is negative

    return opcode_info["cycles"][0]
