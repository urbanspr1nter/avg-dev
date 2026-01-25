def inc_b(cpu, opcode_info):
    """INC B - Increment register B"""
    # Get current value of B
    old_value = cpu.get_register("B")
    new_value = (old_value + 1) & 0xFF

    # Set the new value in B
    cpu.set_register("B", new_value)

    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag("Z", new_value == 0)
    # Negative flag: always 0 for INC
    cpu.set_flag("N", False)
    # Half-carry flag: set if carry from bit 3 (i.e., lower nibble overflow)
    cpu.set_flag("H", (old_value & 0xF) == 0xF)

    return opcode_info["cycles"][0]


def inc_c(cpu, opcode_info):
    """INC C - Increment register C"""
    # Get current value of C
    old_value = cpu.get_register("C")
    new_value = (old_value + 1) & 0xFF

    # Set the new value in C
    cpu.set_register("C", new_value)

    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag("Z", new_value == 0)
    # Negative flag: always 0 for INC
    cpu.set_flag("N", False)
    # Half-carry flag: set if carry from bit 3 (i.e., lower nibble overflow)
    cpu.set_flag("H", (old_value & 0xF) == 0xF)

    return opcode_info["cycles"][0]


def inc_d(cpu, opcode_info):
    """INC D - Increment register D"""
    # Get current value of D
    old_value = cpu.get_register("D")
    new_value = (old_value + 1) & 0xFF

    # Set the new value in D
    cpu.set_register("D", new_value)

    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag("Z", new_value == 0)
    # Negative flag: always 0 for INC
    cpu.set_flag("N", False)
    # Half-carry flag: set if carry from bit 3 (i.e., lower nibble overflow)
    cpu.set_flag("H", (old_value & 0xF) == 0xF)

    return opcode_info["cycles"][0]


def inc_e(cpu, opcode_info):
    """INC E - Increment register E"""
    # Get current value of E
    old_value = cpu.get_register("E")
    new_value = (old_value + 1) & 0xFF

    # Set the new value in E
    cpu.set_register("E", new_value)

    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag("Z", new_value == 0)
    # Negative flag: always 0 for INC
    cpu.set_flag("N", False)
    # Half-carry flag: set if carry from bit 3 (i.e., lower nibble overflow)
    cpu.set_flag("H", (old_value & 0xF) == 0xF)

    return opcode_info["cycles"][0]


def dec_e(cpu, opcode_info):
    """DEC E - Decrement register E"""
    # Get current value of E
    old_value = cpu.get_register("E")
    new_value = (old_value - 1) & 0xFF

    # Set the new value in E
    cpu.set_register("E", new_value)

    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag("Z", new_value == 0)
    # Negative flag: always 1 for DEC (result is negative in two's complement)
    cpu.set_flag("N", True)
    # Half-carry flag: set if borrow from bit 4 (i.e., lower nibble underflow)
    cpu.set_flag("H", (old_value & 0xF) == 0x0)

    return opcode_info["cycles"][0]


def dec_h(cpu, opcode_info):
    """DEC H - Decrement register H"""
    # Get current value of H
    old_value = cpu.get_register("H")
    new_value = (old_value - 1) & 0xFF

    # Set the new value in H
    cpu.set_register("H", new_value)

    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag("Z", new_value == 0)
    # Negative flag: always 1 for DEC (result is negative in two's complement)
    cpu.set_flag("N", True)
    # Half-carry flag: set if borrow from bit 4 (i.e., lower nibble underflow)
    cpu.set_flag("H", (old_value & 0xF) == 0x0)

    return opcode_info["cycles"][0]


def dec_l(cpu, opcode_info):
    """DEC L - Decrement register L"""
    # Get current value of L
    old_value = cpu.get_register("L")
    new_value = (old_value - 1) & 0xFF

    # Set the new value in L
    cpu.set_register("L", new_value)

    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag("Z", new_value == 0)
    # Negative flag: always 1 for DEC (result is negative in two's complement)
    cpu.set_flag("N", True)
    # Half-carry flag: set if borrow from bit 4 (i.e., lower nibble underflow)
    cpu.set_flag("H", (old_value & 0xF) == 0x0)

    return opcode_info["cycles"][0]


def inc_h(cpu, opcode_info):
    """INC H - Increment register H"""
    # Get current value of H
    old_value = cpu.get_register("H")
    new_value = (old_value + 1) & 0xFF

    # Set the new value in H
    cpu.set_register("H", new_value)

    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag("Z", new_value == 0)
    # Negative flag: always 0 for INC
    cpu.set_flag("N", False)
    # Half-carry flag: set if carry from bit 3 (i.e., lower nibble overflow)
    cpu.set_flag("H", (old_value & 0xF) == 0xF)

    return opcode_info["cycles"][0]


def inc_l(cpu, opcode_info):
    """INC L - Increment register L"""
    # Get current value of L
    old_value = cpu.get_register("L")
    new_value = (old_value + 1) & 0xFF

    # Set the new value in L
    cpu.set_register("L", new_value)

    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag("Z", new_value == 0)
    # Negative flag: always 0 for INC
    cpu.set_flag("N", False)
    # Half-carry flag: set if carry from bit 3 (i.e., lower nibble overflow)
    cpu.set_flag("H", (old_value & 0xF) == 0xF)

    return opcode_info["cycles"][0]


def inc_a(cpu, opcode_info):
    """INC A - Increment register A"""
    # Get current value of A
    old_value = cpu.get_register("A")
    new_value = (old_value + 1) & 0xFF

    # Set the new value in A
    cpu.set_register("A", new_value)

    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag("Z", new_value == 0)
    # Negative flag: always 0 for INC
    cpu.set_flag("N", False)
    # Half-carry flag: set if carry from bit 3 (i.e., lower nibble overflow)
    cpu.set_flag("H", (old_value & 0xF) == 0xF)

    return opcode_info["cycles"][0]


def dec_b(cpu, opcode_info):
    """DEC B - Decrement register B"""
    # Get current value of B
    old_value = cpu.get_register("B")
    new_value = (old_value - 1) & 0xFF

    # Set the new value in B
    cpu.set_register("B", new_value)

    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag("Z", new_value == 0)
    # Negative flag: always 1 for DEC (result is negative in two's complement)
    cpu.set_flag("N", True)
    # Half-carry flag: set if borrow from bit 4 (i.e., lower nibble underflow)
    cpu.set_flag("H", (old_value & 0xF) == 0x0)

    return opcode_info["cycles"][0]


def dec_c(cpu, opcode_info):
    """DEC C - Decrement register C"""
    # Get current value of C
    old_value = cpu.get_register("C")
    new_value = (old_value - 1) & 0xFF

    # Set the new value in C
    cpu.set_register("C", new_value)

    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag("Z", new_value == 0)
    # Negative flag: always 1 for DEC (result is negative in two's complement)
    cpu.set_flag("N", True)
    # Half-carry flag: set if borrow from bit 4 (i.e., lower nibble underflow)
    cpu.set_flag("H", (old_value & 0xF) == 0x0)

    return opcode_info["cycles"][0]


def dec_d(cpu, opcode_info):
    """DEC D - Decrement register D"""
    # Get current value of D
    old_value = cpu.get_register("D")
    new_value = (old_value - 1) & 0xFF

    # Set the new value in D
    cpu.set_register("D", new_value)

    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag("Z", new_value == 0)
    # Negative flag: always 1 for DEC (result is negative in two's complement)
    cpu.set_flag("N", True)
    # Half-carry flag: set if borrow from bit 4 (i.e., lower nibble underflow)
    cpu.set_flag("H", (old_value & 0xF) == 0x0)

    return opcode_info["cycles"][0]


def dec_a(cpu, opcode_info):
    """DEC A - Decrement register A"""
    # Get current value of A
    old_value = cpu.get_register("A")
    new_value = (old_value - 1) & 0xFF

    # Set the new value in A
    cpu.set_register("A", new_value)

    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag("Z", new_value == 0)
    # Negative flag: always 1 for DEC (result is negative in two's complement)
    cpu.set_flag("N", True)
    # Half-carry flag: set if borrow from bit 4 (i.e., lower nibble underflow)
    cpu.set_flag("H", (old_value & 0xF) == 0x0)

    return opcode_info["cycles"][0]


def inc_bc(cpu, opcode_info):
    """INC BC - Increment register pair BC"""
    # Get current value of BC (16-bit register pair)
    old_value = cpu.get_register_pair("BC")
    new_value = (old_value + 1) & 0xFFFF

    # Set the new value in BC
    cpu.set_register_pair("BC", new_value)

    return opcode_info["cycles"][0]


def dec_bc(cpu, opcode_info):
    """DEC BC - Decrement register pair BC"""
    # Get current value of BC (16-bit register pair)
    old_value = cpu.get_register_pair("BC")
    new_value = (old_value - 1) & 0xFFFF

    # Set the new value in BC
    cpu.set_register_pair("BC", new_value)

    return opcode_info["cycles"][0]


def inc_de(cpu, opcode_info):
    """INC DE - Increment register pair DE"""
    # Get current value of DE (16-bit register pair)
    old_value = cpu.get_register_pair("DE")
    new_value = (old_value + 1) & 0xFFFF

    # Set the new value in DE
    cpu.set_register_pair("DE", new_value)

    return opcode_info["cycles"][0]


def dec_de(cpu, opcode_info):
    """DEC DE - Decrement register pair DE"""
    # Get current value of DE (16-bit register pair)
    old_value = cpu.get_register_pair("DE")
    new_value = (old_value - 1) & 0xFFFF

    # Set the new value in DE
    cpu.set_register_pair("DE", new_value)

    return opcode_info["cycles"][0]


def inc_hl(cpu, opcode_info):
    """INC HL - Increment register pair HL"""
    # Get current value of HL (16-bit register pair)
    old_value = cpu.get_register_pair("HL")
    new_value = (old_value + 1) & 0xFFFF

    # Set the new value in HL
    cpu.set_register_pair("HL", new_value)

    return opcode_info["cycles"][0]


def dec_hl(cpu, opcode_info):
    """DEC HL - Decrement register pair HL"""
    # Get current value of HL (16-bit register pair)
    old_value = cpu.get_register_pair("HL")
    new_value = (old_value - 1) & 0xFFFF

    # Set the new value in HL
    cpu.set_register_pair("HL", new_value)

    return opcode_info["cycles"][0]


def inc_sp(cpu, opcode_info):
    """INC SP - Increment stack pointer"""
    # Get current value of SP (16-bit register)
    old_value = cpu.get_register("SP")
    new_value = (old_value + 1) & 0xFFFF

    # Set the new value in SP
    cpu.set_register("SP", new_value)

    return opcode_info["cycles"][0]


def dec_sp(cpu, opcode_info):
    """DEC SP - Decrement stack pointer"""
    # Get current value of SP (16-bit register)
    old_value = cpu.get_register("SP")
    new_value = (old_value - 1) & 0xFFFF

    # Set the new value in SP
    cpu.set_register("SP", new_value)

    return opcode_info["cycles"][0]


def inc_hl_indirect(cpu, opcode_info):
    """INC (HL) - Increment memory at address HL"""
    # Get the address from HL register pair
    address = cpu.get_register_pair("HL")

    # Read current value from memory
    old_value = cpu.memory.get_value(address)
    new_value = (old_value + 1) & 0xFF

    # Write new value back to memory
    cpu.memory.set_value(address, new_value)

    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag("Z", new_value == 0)
    # Negative flag: always 0 for INC
    cpu.set_flag("N", False)
    # Half-carry flag: set if carry from bit 3 (i.e., lower nibble overflow)
    cpu.set_flag("H", (old_value & 0xF) == 0xF)

    return opcode_info["cycles"][0]


def dec_hl_indirect(cpu, opcode_info):
    """DEC (HL) - Decrement memory at address HL"""
    # Get the address from HL register pair
    address = cpu.get_register_pair("HL")

    # Read current value from memory
    old_value = cpu.memory.get_value(address)
    new_value = (old_value - 1) & 0xFF

    # Write new value back to memory
    cpu.memory.set_value(address, new_value)

    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag("Z", new_value == 0)
    # Negative flag: always 1 for DEC (result is negative in two's complement)
    cpu.set_flag("N", True)
    # Half-carry flag: set if borrow from bit 4 (i.e., lower nibble underflow)
    cpu.set_flag("H", (old_value & 0xF) == 0x0)

    return opcode_info["cycles"][0]
