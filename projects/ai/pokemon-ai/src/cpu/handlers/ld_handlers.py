"""
LD (Load) instruction handlers for Gameboy CPU.

These handlers implement all LD (load) instructions which transfer data between:
- Registers and immediate values
- Registers and memory
- Memory locations
"""


def ld_bc_n16(cpu, opcode_info):
    """LD BC,n16 - Load 16-bit immediate into BC"""
    # operand_values[0] is BC register
    # operand_values[1] is n16 immediate value
    value = cpu.operand_values[1]["value"]
    cpu.set_register('BC', value)
    return opcode_info["cycles"][0]


def ld_b_n8(cpu, opcode_info):
    """LD B,n8 - Load 8-bit immediate into B"""
    # operand_values[0] is B register
    # operand_values[1] is n8 immediate value
    value = cpu.operand_values[1]["value"]
    cpu.set_register('B', value)
    return opcode_info["cycles"][0]


def ld_c_n8(cpu, opcode_info):
    """LD C,n8 - Load 8-bit immediate into C"""
    # operand_values[0] is C register
    # operand_values[1] is n8 immediate value
    value = cpu.operand_values[1]["value"]
    cpu.set_register('C', value)
    return opcode_info["cycles"][0]


def ld_d_n8(cpu, opcode_info):
    """LD D,n8 - Load 8-bit immediate into D"""
    # operand_values[0] is D register
    # operand_values[1] is n8 immediate value
    value = cpu.operand_values[1]["value"]
    cpu.set_register('D', value)
    return opcode_info["cycles"][0]


def ld_e_n8(cpu, opcode_info):
    """LD E,n8 - Load 8-bit immediate into E"""
    # operand_values[0] is E register
    # operand_values[1] is n8 immediate value
    value = cpu.operand_values[1]["value"]
    cpu.set_register('E', value)
    return opcode_info["cycles"][0]


def ld_h_n8(cpu, opcode_info):
    """LD H,n8 - Load 8-bit immediate into H"""
    # operand_values[0] is H register
    # operand_values[1] is n8 immediate value
    value = cpu.operand_values[1]["value"]
    cpu.set_register('H', value)
    return opcode_info["cycles"][0]


def ld_l_n8(cpu, opcode_info):
    """LD L,n8 - Load 8-bit immediate into L"""
    # operand_values[0] is L register
    # operand_values[1] is n8 immediate value
    value = cpu.operand_values[1]["value"]
    cpu.set_register('L', value)
    return opcode_info["cycles"][0]


def ld_a_n8(cpu, opcode_info):
    """LD A,n8 - Load 8-bit immediate into A"""
    # operand_values[0] is A register
    # operand_values[1] is n8 immediate value
    value = cpu.operand_values[1]["value"]
    cpu.set_register('A', value)
    return opcode_info["cycles"][0]


def ld_de_n16(cpu, opcode_info):
    """LD DE,n16 - Load 16-bit immediate into DE"""
    # operand_values[0] is DE register
    # operand_values[1] is n16 immediate value
    value = cpu.operand_values[1]["value"]
    cpu.set_register('DE', value)
    return opcode_info["cycles"][0]


def ld_bc_a(cpu, opcode_info):
    """LD (BC),A - Load A into memory at address in BC"""
    # operand_values[0] is BC register (indirect addressing)
    # operand_values[1] is A register
    bc_address = cpu.get_register('BC')
    a_value = cpu.get_register('A')
    cpu.memory.set_value(bc_address, a_value)
    return opcode_info["cycles"][0]


def ld_hl_n8(cpu, opcode_info):
    """LD (HL),n8 - Load 8-bit immediate into memory at address in HL"""
    # operand_values[0] is HL register (indirect addressing)
    # operand_values[1] is n8 immediate value
    hl_address = cpu.get_register('HL')
    value = cpu.operand_values[1]["value"]
    cpu.memory.set_value(hl_address, value)
    return opcode_info["cycles"][0]
