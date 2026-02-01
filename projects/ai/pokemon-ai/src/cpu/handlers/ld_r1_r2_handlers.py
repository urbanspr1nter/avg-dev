"""
Handler functions for LD r1, r2 instructions (0x40-0x7F).
These instructions transfer values between registers.
"""


def ld_b_b(cpu, opcode_info) -> int:
    """LD B, B - Load B into B (no-op)"""
    # Get current B value
    b_value = cpu.get_register("B")

    # Set B to itself (no change)
    cpu.set_register("B", b_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_b_c(cpu, opcode_info) -> int:
    """LD B, C - Load C into B"""
    # Get current C value
    c_value = cpu.get_register("C")

    # Set B to C's value
    cpu.set_register("B", c_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_b_d(cpu, opcode_info) -> int:
    """LD B, D - Load D into B"""
    # Get current D value
    d_value = cpu.get_register("D")

    # Set B to D's value
    cpu.set_register("B", d_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_b_e(cpu, opcode_info) -> int:
    """LD B, E - Load E into B"""
    # Get current E value
    e_value = cpu.get_register("E")

    # Set B to E's value
    cpu.set_register("B", e_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_b_h(cpu, opcode_info) -> int:
    """LD B, H - Load H into B"""
    # Get current H value
    h_value = cpu.get_register("H")

    # Set B to H's value
    cpu.set_register("B", h_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_b_l(cpu, opcode_info) -> int:
    """LD B, L - Load L into B"""
    # Get current L value
    l_value = cpu.get_register("L")

    # Set B to L's value
    cpu.set_register("B", l_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_b_hl(cpu, opcode_info) -> int:
    """LD B, (HL) - Load memory at HL into B"""
    # Get current HL value to use as memory address
    hl_value = cpu.get_register("HL")

    # Read value from memory at HL
    mem_value = cpu.memory.get_value(hl_value)

    # Set B to the memory value
    cpu.set_register("B", mem_value)

    return opcode_info["cycles"][0]  # LD r1, (HL) takes 8 cycles


def ld_b_a(cpu, opcode_info) -> int:
    """LD B, A - Load A into B"""
    # Get current A value
    a_value = cpu.get_register("A")

    # Set B to A's value
    cpu.set_register("B", a_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_c_b(cpu, opcode_info) -> int:
    """LD C, B - Load B into C"""
    # Get current B value
    b_value = cpu.get_register("B")

    # Set C to B's value
    cpu.set_register("C", b_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_c_c(cpu, opcode_info) -> int:
    """LD C, C - Load C into C (no-op)"""
    # Get current C value
    c_value = cpu.get_register("C")

    # Set C to itself (no change)
    cpu.set_register("C", c_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_c_d(cpu, opcode_info) -> int:
    """LD C, D - Load D into C"""
    # Get current D value
    d_value = cpu.get_register("D")

    # Set C to D's value
    cpu.set_register("C", d_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_c_e(cpu, opcode_info) -> int:
    """LD C, E - Load E into C"""
    # Get current E value
    e_value = cpu.get_register("E")

    # Set C to E's value
    cpu.set_register("C", e_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_c_h(cpu, opcode_info) -> int:
    """LD C, H - Load H into C"""
    # Get current H value
    h_value = cpu.get_register("H")

    # Set C to H's value
    cpu.set_register("C", h_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_c_l(cpu, opcode_info) -> int:
    """LD C, L - Load L into C"""
    # Get current L value
    l_value = cpu.get_register("L")

    # Set C to L's value
    cpu.set_register("C", l_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_c_hl(cpu, opcode_info) -> int:
    """LD C, (HL) - Load memory at HL into C"""
    # Get current HL value to use as memory address
    hl_value = cpu.get_register("HL")

    # Read value from memory at HL
    mem_value = cpu.memory.get_value(hl_value)

    # Set C to the memory value
    cpu.set_register("C", mem_value)

    return opcode_info["cycles"][0]  # LD r1, (HL) takes 8 cycles


def ld_c_a(cpu, opcode_info) -> int:
    """LD C, A - Load A into C"""
    # Get current A value
    a_value = cpu.get_register("A")

    # Set C to A's value
    cpu.set_register("C", a_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_d_b(cpu, opcode_info) -> int:
    """LD D, B - Load B into D"""
    # Get current B value
    b_value = cpu.get_register("B")

    # Set D to B's value
    cpu.set_register("D", b_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_d_c(cpu, opcode_info) -> int:
    """LD D, C - Load C into D"""
    # Get current C value
    c_value = cpu.get_register("C")

    # Set D to C's value
    cpu.set_register("D", c_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_d_d(cpu, opcode_info) -> int:
    """LD D, D - Load D into D (no-op)"""
    # Get current D value
    d_value = cpu.get_register("D")

    # Set D to itself (no change)
    cpu.set_register("D", d_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_d_e(cpu, opcode_info) -> int:
    """LD D, E - Load E into D"""
    # Get current E value
    e_value = cpu.get_register("E")

    # Set D to E's value
    cpu.set_register("D", e_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_d_h(cpu, opcode_info) -> int:
    """LD D, H - Load H into D"""
    # Get current H value
    h_value = cpu.get_register("H")

    # Set D to H's value
    cpu.set_register("D", h_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_d_l(cpu, opcode_info) -> int:
    """LD D, L - Load L into D"""
    # Get current L value
    l_value = cpu.get_register("L")

    # Set D to L's value
    cpu.set_register("D", l_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_d_hl(cpu, opcode_info) -> int:
    """LD D, (HL) - Load memory at HL into D"""
    # Get current HL value to use as memory address
    hl_value = cpu.get_register("HL")

    # Read value from memory at HL
    mem_value = cpu.memory.get_value(hl_value)

    # Set D to the memory value
    cpu.set_register("D", mem_value)

    return opcode_info["cycles"][0]  # LD r1, (HL) takes 8 cycles


def ld_d_a(cpu, opcode_info) -> int:
    """LD D, A - Load A into D"""
    # Get current A value
    a_value = cpu.get_register("A")

    # Set D to A's value
    cpu.set_register("D", a_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_e_b(cpu, opcode_info) -> int:
    """LD E, B - Load B into E"""
    # Get current B value
    b_value = cpu.get_register("B")

    # Set E to B's value
    cpu.set_register("E", b_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_e_c(cpu, opcode_info) -> int:
    """LD E, C - Load C into E"""
    # Get current C value
    c_value = cpu.get_register("C")

    # Set E to C's value
    cpu.set_register("E", c_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_e_d(cpu, opcode_info) -> int:
    """LD E, D - Load D into E"""
    # Get current D value
    d_value = cpu.get_register("D")

    # Set E to D's value
    cpu.set_register("E", d_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_e_e(cpu, opcode_info) -> int:
    """LD E, E - Load E into E (no-op)"""
    # Get current E value
    e_value = cpu.get_register("E")

    # Set E to itself (no change)
    cpu.set_register("E", e_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_e_h(cpu, opcode_info) -> int:
    """LD E, H - Load H into E"""
    # Get current H value
    h_value = cpu.get_register("H")

    # Set E to H's value
    cpu.set_register("E", h_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_e_l(cpu, opcode_info) -> int:
    """LD E, L - Load L into E"""
    # Get current L value
    l_value = cpu.get_register("L")

    # Set E to L's value
    cpu.set_register("E", l_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_e_hl(cpu, opcode_info) -> int:
    """LD E, (HL) - Load memory at HL into E"""
    # Get current HL value to use as memory address
    hl_value = cpu.get_register("HL")

    # Read value from memory at HL
    mem_value = cpu.memory.get_value(hl_value)

    # Set E to the memory value
    cpu.set_register("E", mem_value)

    return opcode_info["cycles"][0]  # LD r1, (HL) takes 8 cycles


def ld_e_a(cpu, opcode_info) -> int:
    """LD E, A - Load A into E"""
    # Get current A value
    a_value = cpu.get_register("A")

    # Set E to A's value
    cpu.set_register("E", a_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_h_b(cpu, opcode_info) -> int:
    """LD H, B - Load B into H"""
    # Get current B value
    b_value = cpu.get_register("B")

    # Set H to B's value
    cpu.set_register("H", b_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_h_c(cpu, opcode_info) -> int:
    """LD H, C - Load C into H"""
    # Get current C value
    c_value = cpu.get_register("C")

    # Set H to C's value
    cpu.set_register("H", c_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_h_d(cpu, opcode_info) -> int:
    """LD H, D - Load D into H"""
    # Get current D value
    d_value = cpu.get_register("D")

    # Set H to D's value
    cpu.set_register("H", d_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_h_e(cpu, opcode_info) -> int:
    """LD H, E - Load E into H"""
    # Get current E value
    e_value = cpu.get_register("E")

    # Set H to E's value
    cpu.set_register("H", e_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_h_h(cpu, opcode_info) -> int:
    """LD H, H - Load H into H (no-op)"""
    # Get current H value
    h_value = cpu.get_register("H")

    # Set H to itself (no change)
    cpu.set_register("H", h_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_h_l(cpu, opcode_info) -> int:
    """LD H, L - Load L into H"""
    # Get current L value
    l_value = cpu.get_register("L")

    # Set H to L's value
    cpu.set_register("H", l_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_h_hl(cpu, opcode_info) -> int:
    """LD H, (HL) - Load memory at HL into H"""
    # Get current HL value to use as memory address
    hl_value = cpu.get_register("HL")

    # Read value from memory at HL
    mem_value = cpu.memory.get_value(hl_value)

    # Set H to the memory value
    cpu.set_register("H", mem_value)

    return opcode_info["cycles"][0]  # LD r1, (HL) takes 8 cycles


def ld_h_a(cpu, opcode_info) -> int:
    """LD H, A - Load A into H"""
    # Get current A value
    a_value = cpu.get_register("A")

    # Set H to A's value
    cpu.set_register("H", a_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_l_b(cpu, opcode_info) -> int:
    """LD L, B - Load B into L"""
    # Get current B value
    b_value = cpu.get_register("B")

    # Set L to B's value
    cpu.set_register("L", b_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_l_c(cpu, opcode_info) -> int:
    """LD L, C - Load C into L"""
    # Get current C value
    c_value = cpu.get_register("C")

    # Set L to C's value
    cpu.set_register("L", c_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_l_d(cpu, opcode_info) -> int:
    """LD L, D - Load D into L"""
    # Get current D value
    d_value = cpu.get_register("D")

    # Set L to D's value
    cpu.set_register("L", d_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_l_e(cpu, opcode_info) -> int:
    """LD L, E - Load E into L"""
    # Get current E value
    e_value = cpu.get_register("E")

    # Set L to E's value
    cpu.set_register("L", e_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_l_h(cpu, opcode_info) -> int:
    """LD L, H - Load H into L"""
    # Get current H value
    h_value = cpu.get_register("H")

    # Set L to H's value
    cpu.set_register("L", h_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_l_l(cpu, opcode_info) -> int:
    """LD L, L - Load L into L (no-op)"""
    # Get current L value
    l_value = cpu.get_register("L")

    # Set L to itself (no change)
    cpu.set_register("L", l_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_l_hl(cpu, opcode_info) -> int:
    """LD L, (HL) - Load memory at HL into L"""
    # Get current HL value to use as memory address
    hl_value = cpu.get_register("HL")

    # Read value from memory at HL
    mem_value = cpu.memory.get_value(hl_value)

    # Set L to the memory value
    cpu.set_register("L", mem_value)

    return opcode_info["cycles"][0]  # LD r1, (HL) takes 8 cycles


def ld_l_a(cpu, opcode_info) -> int:
    """LD L, A - Load A into L"""
    # Get current A value
    a_value = cpu.get_register("A")

    # Set L to A's value
    cpu.set_register("L", a_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_hl_b(cpu, opcode_info) -> int:
    """LD (HL), B - Load B into memory at HL"""
    # Get current HL value to use as memory address
    hl_value = cpu.get_register("HL")

    # Get current B value
    b_value = cpu.get_register("B")

    # Write B's value to memory at HL
    cpu.memory.set_value(hl_value, b_value)

    return opcode_info["cycles"][0]  # LD (HL), r takes 8 cycles


def ld_hl_c(cpu, opcode_info) -> int:
    """LD (HL), C - Load C into memory at HL"""
    # Get current HL value to use as memory address
    hl_value = cpu.get_register("HL")

    # Get current C value
    c_value = cpu.get_register("C")

    # Write C's value to memory at HL
    cpu.memory.set_value(hl_value, c_value)

    return opcode_info["cycles"][0]  # LD (HL), r takes 8 cycles


def ld_hl_d(cpu, opcode_info) -> int:
    """LD (HL), D - Load D into memory at HL"""
    # Get current HL value to use as memory address
    hl_value = cpu.get_register("HL")

    # Get current D value
    d_value = cpu.get_register("D")

    # Write D's value to memory at HL
    cpu.memory.set_value(hl_value, d_value)

    return opcode_info["cycles"][0]  # LD (HL), r takes 8 cycles


def ld_hl_e(cpu, opcode_info) -> int:
    """LD (HL), E - Load E into memory at HL"""
    # Get current HL value to use as memory address
    hl_value = cpu.get_register("HL")

    # Get current E value
    e_value = cpu.get_register("E")

    # Write E's value to memory at HL
    cpu.memory.set_value(hl_value, e_value)

    return opcode_info["cycles"][0]  # LD (HL), r takes 8 cycles


def ld_hl_h(cpu, opcode_info) -> int:
    """LD (HL), H - Load H into memory at HL"""
    # Get current HL value to use as memory address
    hl_value = cpu.get_register("HL")

    # Get current H value
    h_value = cpu.get_register("H")

    # Write H's value to memory at HL
    cpu.memory.set_value(hl_value, h_value)

    return opcode_info["cycles"][0]  # LD (HL), r takes 8 cycles


def ld_hl_l(cpu, opcode_info) -> int:
    """LD (HL), L - Load L into memory at HL"""
    # Get current HL value to use as memory address
    hl_value = cpu.get_register("HL")

    # Get current L value
    l_value = cpu.get_register("L")

    # Write L's value to memory at HL
    cpu.memory.set_value(hl_value, l_value)

    return opcode_info["cycles"][0]  # LD (HL), r takes 8 cycles


def ld_hl_a(cpu, opcode_info) -> int:
    """LD (HL), A - Load A into memory at HL"""
    # Get current HL value to use as memory address
    hl_value = cpu.get_register("HL")

    # Get current A value
    a_value = cpu.get_register("A")

    # Write A's value to memory at HL
    cpu.memory.set_value(hl_value, a_value)

    return opcode_info["cycles"][0]  # LD (HL), r takes 8 cycles


def ld_a_b(cpu, opcode_info) -> int:
    """LD A, B - Load B into A"""
    # Get current B value
    b_value = cpu.get_register("B")

    # Set A to B's value
    cpu.set_register("A", b_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_a_c(cpu, opcode_info) -> int:
    """LD A, C - Load C into A"""
    # Get current C value
    c_value = cpu.get_register("C")

    # Set A to C's value
    cpu.set_register("A", c_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_a_d(cpu, opcode_info) -> int:
    """LD A, D - Load D into A"""
    # Get current D value
    d_value = cpu.get_register("D")

    # Set A to D's value
    cpu.set_register("A", d_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_a_e(cpu, opcode_info) -> int:
    """LD A, E - Load E into A"""
    # Get current E value
    e_value = cpu.get_register("E")

    # Set A to E's value
    cpu.set_register("A", e_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_a_h(cpu, opcode_info) -> int:
    """LD A, H - Load H into A"""
    # Get current H value
    h_value = cpu.get_register("H")

    # Set A to H's value
    cpu.set_register("A", h_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_a_l(cpu, opcode_info) -> int:
    """LD A, L - Load L into A"""
    # Get current L value
    l_value = cpu.get_register("L")

    # Set A to L's value
    cpu.set_register("A", l_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles


def ld_a_hl(cpu, opcode_info) -> int:
    """LD A, (HL) - Load memory at HL into A"""
    # Get current HL value to use as memory address
    hl_value = cpu.get_register("HL")

    # Read value from memory at HL
    mem_value = cpu.memory.get_value(hl_value)

    # Set A to the memory value
    cpu.set_register("A", mem_value)

    return opcode_info["cycles"][0]  # LD r1, (HL) takes 8 cycles


def ld_a_a(cpu, opcode_info) -> int:
    """LD A, A - Load A into A (no-op)"""
    # Get current A value
    a_value = cpu.get_register("A")

    # Set A to itself (no change)
    cpu.set_register("A", a_value)

    return opcode_info["cycles"][0]  # LD r1, r2 takes 4 cycles
