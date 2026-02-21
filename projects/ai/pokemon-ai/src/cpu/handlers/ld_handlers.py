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


def ld_a_bc(cpu, opcode_info):
    """LD A,(BC) - Load A from memory at address in BC"""
    address = cpu.get_register('BC')
    cpu.set_register('A', cpu.memory.get_value(address))
    return opcode_info["cycles"][0]


def ld_a_de(cpu, opcode_info):
    """LD A,(DE) - Load A from memory at address in DE"""
    address = cpu.get_register('DE')
    cpu.set_register('A', cpu.memory.get_value(address))
    return opcode_info["cycles"][0]


def ld_de_a(cpu, opcode_info):
    """LD (DE),A - Store A into memory at address in DE"""
    address = cpu.get_register('DE')
    cpu.memory.set_value(address, cpu.get_register('A'))
    return opcode_info["cycles"][0]


def ld_sp_hl(cpu, opcode_info):
    """LD SP,HL - Copy HL into SP"""
    cpu.registers.SP = cpu.get_register('HL')
    return opcode_info["cycles"][0]


def ld_hli_a(cpu, opcode_info):
    """LD (HL+),A - Store A at (HL), then increment HL"""
    hl = cpu.get_register('HL')
    cpu.memory.set_value(hl, cpu.get_register('A'))
    cpu.set_register('HL', (hl + 1) & 0xFFFF)
    return opcode_info["cycles"][0]


def ld_a_hli(cpu, opcode_info):
    """LD A,(HL+) - Load A from (HL), then increment HL"""
    hl = cpu.get_register('HL')
    cpu.set_register('A', cpu.memory.get_value(hl))
    cpu.set_register('HL', (hl + 1) & 0xFFFF)
    return opcode_info["cycles"][0]


def ld_hld_a(cpu, opcode_info):
    """LD (HL-),A - Store A at (HL), then decrement HL"""
    hl = cpu.get_register('HL')
    cpu.memory.set_value(hl, cpu.get_register('A'))
    cpu.set_register('HL', (hl - 1) & 0xFFFF)
    return opcode_info["cycles"][0]


def ld_a_hld(cpu, opcode_info):
    """LD A,(HL-) - Load A from (HL), then decrement HL"""
    hl = cpu.get_register('HL')
    cpu.set_register('A', cpu.memory.get_value(hl))
    cpu.set_register('HL', (hl - 1) & 0xFFFF)
    return opcode_info["cycles"][0]


def ld_hl_n16(cpu, opcode_info):
    """LD HL,n16 - Load 16-bit immediate into HL"""
    value = cpu.operand_values[1]["value"]
    cpu.set_register('HL', value)
    return opcode_info["cycles"][0]


def ld_sp_n16(cpu, opcode_info):
    """LD SP,n16 - Load 16-bit immediate into SP"""
    value = cpu.operand_values[1]["value"]
    cpu.registers.SP = value
    return opcode_info["cycles"][0]


def ld_a16_a(cpu, opcode_info):
    """LD (a16),A - Store A at absolute 16-bit address"""
    address = cpu.operand_values[0]["value"]
    cpu.memory.set_value(address, cpu.get_register('A'))
    return opcode_info["cycles"][0]


def ld_a_a16(cpu, opcode_info):
    """LD A,(a16) - Load A from absolute 16-bit address"""
    address = cpu.operand_values[1]["value"]
    cpu.set_register('A', cpu.memory.get_value(address))
    return opcode_info["cycles"][0]


def ld_a16_sp(cpu, opcode_info):
    """LD (a16),SP - Store SP at absolute 16-bit address (little-endian)"""
    address = cpu.operand_values[0]["value"]
    sp = cpu.registers.SP
    cpu.memory.set_value(address, sp & 0xFF)
    cpu.memory.set_value((address + 1) & 0xFFFF, (sp >> 8) & 0xFF)
    return opcode_info["cycles"][0]


def ld_hl_sp_e8(cpu, opcode_info):
    """LD HL,SP+e8 - Load SP plus signed 8-bit offset into HL"""
    e8_unsigned = cpu.operand_values[2]["value"]
    e8_signed = e8_unsigned if e8_unsigned <= 127 else e8_unsigned - 256
    sp = cpu.registers.SP
    result = (sp + e8_signed) & 0xFFFF
    cpu.set_register('HL', result)
    # Flags computed on unsigned byte addition
    cpu.set_flag('Z', False)
    cpu.set_flag('N', False)
    cpu.set_flag('H', ((sp & 0xF) + (e8_unsigned & 0xF)) > 0xF)
    cpu.set_flag('C', ((sp & 0xFF) + (e8_unsigned & 0xFF)) > 0xFF)
    return opcode_info["cycles"][0]
