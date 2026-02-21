"""
Jump instruction handlers for the Gameboy CPU emulator.

This module contains handlers for all jump and control flow instructions:
- Unconditional jumps (JP, JP HL)
- Relative jumps (JR)
- Conditional jumps (JR with flags)
- Call/Return instructions
- Restart instructions
"""


def jp_nn(cpu, opcode_info) -> int:
    """JP nn - Jump to address"""
    # Get the 16-bit address from operand_values (already combined)
    addr = cpu.operand_values[0]["value"]
    cpu.registers.PC = addr
    return opcode_info["cycles"][0]


def jp_hl(cpu, opcode_info) -> int:
    """JP HL - Jump to address in HL register"""
    hl_value = cpu.get_register("HL")
    cpu.registers.PC = hl_value
    return opcode_info["cycles"][0]


def jr_n(cpu, opcode_info) -> int:
    """JR n - Relative jump (unconditional)"""
    # Get the signed 8-bit offset from operand_values
    offset = cpu.operand_values[0]["value"]
    if offset > 127:
        offset -= 256  # Sign extend to get negative value

    # Calculate new PC: current PC - 1 + offset (PC is after opcode and operand)
    new_pc = cpu.registers.PC - 1 + offset
    cpu.registers.PC = new_pc
    return opcode_info["cycles"][0]


def jr_nz_n(cpu, opcode_info) -> int:
    """JR NZ, n - Relative jump if Z flag is not set"""
    offset = cpu.operand_values[0]["value"]
    if offset > 127:
        offset -= 256

    # Check Z flag
    z_flag = cpu.get_flag("Z")
    if not z_flag:
        new_pc = cpu.registers.PC - 1 + offset
        cpu.registers.PC = new_pc
        return opcode_info["cycles"][0]  # Jump taken: 12 cycles

    # Jump not taken: PC is already past both opcode and operand, so back up by 1
    cpu.registers.PC -= 1
    return opcode_info["cycles"][1]  # Jump not taken: 8 cycles


def jr_z_n(cpu, opcode_info) -> int:
    """JR Z, n - Relative jump if Z flag is set"""
    offset = cpu.operand_values[0]["value"]
    if offset > 127:
        offset -= 256

    # Check Z flag
    z_flag = cpu.get_flag("Z")
    if z_flag:
        new_pc = cpu.registers.PC - 1 + offset
        cpu.registers.PC = new_pc
        return opcode_info["cycles"][0]  # Jump taken: 12 cycles

    # Jump not taken: PC is already past both opcode and operand, so back up by 1
    cpu.registers.PC -= 1
    return opcode_info["cycles"][1]  # Jump not taken: 8 cycles


def jr_nc_n(cpu, opcode_info) -> int:
    """JR NC, n - Relative jump if C flag is not set"""
    offset = cpu.operand_values[0]["value"]
    if offset > 127:
        offset -= 256

    # Check C flag
    c_flag = cpu.get_flag("C")
    if not c_flag:
        new_pc = cpu.registers.PC - 1 + offset
        cpu.registers.PC = new_pc
        return opcode_info["cycles"][0]  # Jump taken: 12 cycles

    # Jump not taken: PC is already past both opcode and operand, so back up by 1
    cpu.registers.PC -= 1
    return opcode_info["cycles"][1]  # Jump not taken: 8 cycles


def jr_c_n(cpu, opcode_info) -> int:
    """JR C, n - Relative jump if C flag is set"""
    offset = cpu.operand_values[0]["value"]
    if offset > 127:
        offset -= 256

    # Check C flag
    c_flag = cpu.get_flag("C")
    if c_flag:
        new_pc = cpu.registers.PC - 1 + offset
        cpu.registers.PC = new_pc
        return opcode_info["cycles"][0]  # Jump taken: 12 cycles

    # Jump not taken: PC is already past both opcode and operand, so back up by 1
    cpu.registers.PC -= 1
    return opcode_info["cycles"][1]  # Jump not taken: 8 cycles


def jp_nz_nn(cpu, opcode_info) -> int:
    """JP NZ, a16 - Jump to address if Z flag not set"""
    addr = cpu.operand_values[0]["value"]
    if not cpu.get_flag("Z"):
        cpu.registers.PC = addr
        return opcode_info["cycles"][0]
    return opcode_info["cycles"][1]


def jp_z_nn(cpu, opcode_info) -> int:
    """JP Z, a16 - Jump to address if Z flag set"""
    addr = cpu.operand_values[0]["value"]
    if cpu.get_flag("Z"):
        cpu.registers.PC = addr
        return opcode_info["cycles"][0]
    return opcode_info["cycles"][1]


def jp_nc_nn(cpu, opcode_info) -> int:
    """JP NC, a16 - Jump to address if C flag not set"""
    addr = cpu.operand_values[0]["value"]
    if not cpu.get_flag("C"):
        cpu.registers.PC = addr
        return opcode_info["cycles"][0]
    return opcode_info["cycles"][1]


def jp_c_nn(cpu, opcode_info) -> int:
    """JP C, a16 - Jump to address if C flag set"""
    addr = cpu.operand_values[0]["value"]
    if cpu.get_flag("C"):
        cpu.registers.PC = addr
        return opcode_info["cycles"][0]
    return opcode_info["cycles"][1]


def call_nn(cpu, opcode_info) -> int:
    """CALL nn - Call subroutine at address"""
    # Get the 16-bit address from operand_values (already combined)
    addr = cpu.operand_values[0]["value"]

    # Push current return address onto stack (PC is already past the CALL instruction)
    return_addr = cpu.registers.PC
    cpu.push_word(return_addr)

    # Jump to subroutine
    cpu.registers.PC = addr
    return opcode_info["cycles"][0]


def call_nz_nn(cpu, opcode_info) -> int:
    """CALL NZ, nn - Call if Z flag is not set"""
    addr = cpu.operand_values[0]["value"]

    # Check Z flag
    z_flag = cpu.get_flag("Z")
    if not z_flag:
        return_addr = cpu.registers.PC
        cpu.push_word(return_addr)
        cpu.registers.PC = addr
        return opcode_info["cycles"][0]  # Call taken: 24 cycles

    # Call not taken: PC is already past the instruction (opcode + operands)
    return opcode_info["cycles"][1]  # Call not taken: 12 cycles


def call_z_nn(cpu, opcode_info) -> int:
    """CALL Z, nn - Call if Z flag is set"""
    addr = cpu.operand_values[0]["value"]

    # Check Z flag
    z_flag = cpu.get_flag("Z")
    if z_flag:
        return_addr = cpu.registers.PC
        cpu.push_word(return_addr)
        cpu.registers.PC = addr
        return opcode_info["cycles"][0]  # Call taken: 24 cycles

    # Call not taken: PC is already past the instruction (opcode + operands)
    return opcode_info["cycles"][1]  # Call not taken: 12 cycles


def call_nc_nn(cpu, opcode_info) -> int:
    """CALL NC, nn - Call if C flag is not set"""
    addr = cpu.operand_values[0]["value"]

    # Check C flag
    c_flag = cpu.get_flag("C")
    if not c_flag:
        return_addr = cpu.registers.PC
        cpu.push_word(return_addr)
        cpu.registers.PC = addr
        return opcode_info["cycles"][0]  # Call taken: 24 cycles

    # Call not taken: PC is already past the instruction (opcode + operands)
    return opcode_info["cycles"][1]  # Call not taken: 12 cycles


def call_c_nn(cpu, opcode_info) -> int:
    """CALL C, nn - Call if C flag is set"""
    addr = cpu.operand_values[0]["value"]

    # Check C flag
    c_flag = cpu.get_flag("C")
    if c_flag:
        return_addr = cpu.registers.PC
        cpu.push_word(return_addr)
        cpu.registers.PC = addr
        return opcode_info["cycles"][0]  # Call taken: 24 cycles

    # Call not taken: PC is already past the instruction (opcode + operands)
    return opcode_info["cycles"][1]  # Call not taken: 12 cycles


def ret(cpu, opcode_info) -> int:
    """RET - Return from subroutine"""
    # Pop return address from stack
    return_addr = cpu.pop_word()
    cpu.registers.PC = return_addr
    return opcode_info["cycles"][0]


def ret_nz(cpu, opcode_info) -> int:
    """RET NZ - Return if Z flag is not set"""
    # Check Z flag
    z_flag = cpu.get_flag("Z")
    if not z_flag:
        return_addr = cpu.pop_word()
        cpu.registers.PC = return_addr
        return opcode_info["cycles"][0]  # Return taken: 16 cycles

    # Return not taken: just continue execution
    return opcode_info["cycles"][1]  # Return not taken: 8 cycles


def ret_z(cpu, opcode_info) -> int:
    """RET Z - Return if Z flag is set"""
    # Check Z flag
    z_flag = cpu.get_flag("Z")
    if z_flag:
        return_addr = cpu.pop_word()
        cpu.registers.PC = return_addr
        return opcode_info["cycles"][0]  # Return taken: 16 cycles

    # Return not taken
    return opcode_info["cycles"][1]  # Return not taken: 8 cycles


def ret_nc(cpu, opcode_info) -> int:
    """RET NC - Return if C flag is not set"""
    # Check C flag
    c_flag = cpu.get_flag("C")
    if not c_flag:
        return_addr = cpu.pop_word()
        cpu.registers.PC = return_addr
        return opcode_info["cycles"][0]  # Return taken: 16 cycles

    # Return not taken
    return opcode_info["cycles"][1]  # Return not taken: 8 cycles


def ret_c(cpu, opcode_info) -> int:
    """RET C - Return if C flag is set"""
    # Check C flag
    c_flag = cpu.get_flag("C")
    if c_flag:
        return_addr = cpu.pop_word()
        cpu.registers.PC = return_addr
        return opcode_info["cycles"][0]  # Return taken: 16 cycles

    # Return not taken
    return opcode_info["cycles"][1]  # Return not taken: 8 cycles


def reti(cpu, opcode_info) -> int:
    """RETI - Return and enable interrupts"""
    # Pop return address from stack
    return_addr = cpu.pop_word()
    cpu.registers.PC = return_addr

    # Enable interrupts (IME flag)
    cpu.interrupts.ime = True

    return opcode_info["cycles"][0]


def rst_00h(cpu, opcode_info) -> int:
    """RST 00H - Restart to address 0x00"""
    # Push current PC onto stack (return after RST instruction)
    cpu.push_word(cpu.registers.PC & 0xFFFF)

    # Jump to restart address
    cpu.registers.PC = 0x00
    return opcode_info["cycles"][0]


def rst_08h(cpu, opcode_info) -> int:
    """RST 08H - Restart to address 0x08"""
    cpu.push_word(cpu.registers.PC & 0xFFFF)
    cpu.registers.PC = 0x08
    return opcode_info["cycles"][0]


def rst_10h(cpu, opcode_info) -> int:
    """RST 10H - Restart to address 0x10"""
    cpu.push_word(cpu.registers.PC & 0xFFFF)
    cpu.registers.PC = 0x10
    return opcode_info["cycles"][0]


def rst_18h(cpu, opcode_info) -> int:
    """RST 18H - Restart to address 0x18"""
    cpu.push_word(cpu.registers.PC & 0xFFFF)
    cpu.registers.PC = 0x18
    return opcode_info["cycles"][0]


def rst_20h(cpu, opcode_info) -> int:
    """RST 20H - Restart to address 0x20"""
    cpu.push_word(cpu.registers.PC & 0xFFFF)
    cpu.registers.PC = 0x20
    return opcode_info["cycles"][0]


def rst_28h(cpu, opcode_info) -> int:
    """RST 28H - Restart to address 0x28"""
    cpu.push_word(cpu.registers.PC & 0xFFFF)
    cpu.registers.PC = 0x28
    return opcode_info["cycles"][0]


def rst_30h(cpu, opcode_info) -> int:
    """RST 30H - Restart to address 0x30"""
    cpu.push_word(cpu.registers.PC & 0xFFFF)
    cpu.registers.PC = 0x30
    return opcode_info["cycles"][0]


def rst_38h(cpu, opcode_info) -> int:
    """RST 38H - Restart to address 0x38"""
    cpu.push_word(cpu.registers.PC & 0xFFFF)
    cpu.registers.PC = 0x38
    return opcode_info["cycles"][0]
