"""
Miscellaneous instruction handlers for Gameboy CPU.

These handlers implement instructions that don't fit into other categories,
such as NOP (no operation), HALT, STOP, etc.
"""


def nop(cpu, opcode_info):
    """NOP - No operation"""
    return opcode_info["cycles"][0]


def stop(cpu, opcode_info):
    """STOP - Halt CPU and LCD until button press (stub).

    On real hardware, STOP halts both the CPU and LCD display until a joypad
    button is pressed. Full behavior requires joypad and LCD subsystems.
    For now this is a no-op stub that just consumes the correct cycles.
    """
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


def daa(cpu, opcode_info):
    """DAA - Decimal Adjust Accumulator for BCD arithmetic"""
    a = cpu.get_register("A")
    n_flag = cpu.get_flag("N")
    c_flag = cpu.get_flag("C")
    h_flag = cpu.get_flag("H")

    if not n_flag:
        # After addition
        if c_flag or a > 0x99:
            a += 0x60
            c_flag = True
        if h_flag or (a & 0x0F) > 0x09:
            a += 0x06
    else:
        # After subtraction
        if c_flag:
            a -= 0x60
        if h_flag:
            a -= 0x06

    a &= 0xFF
    cpu.set_register("A", a)
    cpu.set_flag("Z", a == 0)
    cpu.set_flag("H", False)
    cpu.set_flag("C", c_flag)
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
