"""
JR (Jump Relative) instruction handlers for Gameboy CPU.

These handlers implement all JR (jump relative) instructions which perform
conditional and unconditional relative jumps based on flags.
"""


def jr_nz_e8(cpu, opcode_info):
    """JR NZ,e8 - Jump relative if Zero flag not set"""
    # operand_values[0] is NZ condition
    # operand_values[1] is e8 (signed offset)
    offset = cpu.operand_values[1]["value"]
    z_flag = cpu.get_flag('Z')

    if not z_flag:  # Jump taken
        if offset > 127:
            offset = offset - 256  # Convert to signed
        cpu.registers.PC += offset
        return opcode_info["cycles"][0]  # 12 cycles
    else:  # Jump not taken
        return opcode_info["cycles"][1]  # 8 cycles
