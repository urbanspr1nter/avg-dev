"""
Rotation and shift instruction handlers for Gameboy CPU.

These handlers implement the RLC, RRC, RL, RR family of instructions
that rotate or shift bits in register A.
"""


def rlc_a(cpu, opcode_info) -> int:
    """RLC A - Rotate A left, old bit 7 to CF"""
    # Get current A value
    a_value = cpu.get_register("A")

    # Calculate result: rotate left through carry
    # Bit 7 becomes the new carry flag
    carry_bit = (a_value >> 7) & 1
    result = ((a_value << 1) | carry_bit) & 0xFF

    # Update flags
    cpu.set_flag("Z", False)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", carry_bit)

    # Update A register
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]  # RLC A takes 4 cycles


def rrc_a(cpu, opcode_info) -> int:
    """RRC A - Rotate A right, old bit 0 to CF"""
    # Get current A value
    a_value = cpu.get_register("A")

    # Calculate result: rotate right through carry
    # Bit 0 becomes the new carry flag
    carry_bit = a_value & 1
    result = ((a_value >> 1) | (carry_bit << 7)) & 0xFF

    # Update flags
    cpu.set_flag("Z", False)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", carry_bit)

    # Update A register
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]  # RRC A takes 4 cycles


def rl_a(cpu, opcode_info) -> int:
    """RL A - Rotate A left through CF"""
    # Get current A value and carry flag
    a_value = cpu.get_register("A")
    carry_flag = cpu.get_flag("C")

    # Calculate result: rotate left through carry
    # Bit 7 becomes the new carry flag, old carry goes to bit 0
    old_carry_bit = (a_value >> 7) & 1
    result = ((a_value << 1) | carry_flag) & 0xFF

    # Update flags
    cpu.set_flag("Z", False)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", old_carry_bit)

    # Update A register
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]  # RL A takes 4 cycles


def rr_a(cpu, opcode_info) -> int:
    """RR A - Rotate A right through CF"""
    # Get current A value and carry flag
    a_value = cpu.get_register("A")
    carry_flag = cpu.get_flag("C")

    # Calculate result: rotate right through carry
    # Bit 0 becomes the new carry flag, old carry goes to bit 7
    old_carry_bit = a_value & 1
    result = ((a_value >> 1) | (carry_flag << 7)) & 0xFF

    # Update flags
    cpu.set_flag("Z", False)
    cpu.set_flag("N", False)
    cpu.set_flag("H", False)
    cpu.set_flag("C", old_carry_bit)

    # Update A register
    cpu.set_register("A", result)

    return opcode_info["cycles"][0]  # RR A takes 4 cycles
