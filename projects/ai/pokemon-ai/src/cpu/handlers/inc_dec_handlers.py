def inc_b(cpu, opcode_info):
    """INC B - Increment register B"""
    # Get current value of B
    old_value = cpu.get_register('B')
    new_value = (old_value + 1) & 0xFF
    
    # Set the new value in B
    cpu.set_register('B', new_value)
    
    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag('Z', new_value == 0)
    # Negative flag: always 0 for INC
    cpu.set_flag('N', False)
    # Half-carry flag: set if carry from bit 3 (i.e., lower nibble overflow)
    cpu.set_flag('H', (old_value & 0xF) == 0xF)
    
    return opcode_info["cycles"][0]


def inc_c(cpu, opcode_info):
    """INC C - Increment register C"""
    # Get current value of C
    old_value = cpu.get_register('C')
    new_value = (old_value + 1) & 0xFF
    
    # Set the new value in C
    cpu.set_register('C', new_value)
    
    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag('Z', new_value == 0)
    # Negative flag: always 0 for INC
    cpu.set_flag('N', False)
    # Half-carry flag: set if carry from bit 3 (i.e., lower nibble overflow)
    cpu.set_flag('H', (old_value & 0xF) == 0xF)
    
    return opcode_info["cycles"][0]


def inc_d(cpu, opcode_info):
    """INC D - Increment register D"""
    # Get current value of D
    old_value = cpu.get_register('D')
    new_value = (old_value + 1) & 0xFF
    
    # Set the new value in D
    cpu.set_register('D', new_value)
    
    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag('Z', new_value == 0)
    # Negative flag: always 0 for INC
    cpu.set_flag('N', False)
    # Half-carry flag: set if carry from bit 3 (i.e., lower nibble overflow)
    cpu.set_flag('H', (old_value & 0xF) == 0xF)
    
    return opcode_info["cycles"][0]


def inc_e(cpu, opcode_info):
    """INC E - Increment register E"""
    # Get current value of E
    old_value = cpu.get_register('E')
    new_value = (old_value + 1) & 0xFF
    
    # Set the new value in E
    cpu.set_register('E', new_value)
    
    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag('Z', new_value == 0)
    # Negative flag: always 0 for INC
    cpu.set_flag('N', False)
    # Half-carry flag: set if carry from bit 3 (i.e., lower nibble overflow)
    cpu.set_flag('H', (old_value & 0xF) == 0xF)
    
    return opcode_info["cycles"][0]


def inc_h(cpu, opcode_info):
    """INC H - Increment register H"""
    # Get current value of H
    old_value = cpu.get_register('H')
    new_value = (old_value + 1) & 0xFF
    
    # Set the new value in H
    cpu.set_register('H', new_value)
    
    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag('Z', new_value == 0)
    # Negative flag: always 0 for INC
    cpu.set_flag('N', False)
    # Half-carry flag: set if carry from bit 3 (i.e., lower nibble overflow)
    cpu.set_flag('H', (old_value & 0xF) == 0xF)
    
    return opcode_info["cycles"][0]


def inc_l(cpu, opcode_info):
    """INC L - Increment register L"""
    # Get current value of L
    old_value = cpu.get_register('L')
    new_value = (old_value + 1) & 0xFF
    
    # Set the new value in L
    cpu.set_register('L', new_value)
    
    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag('Z', new_value == 0)
    # Negative flag: always 0 for INC
    cpu.set_flag('N', False)
    # Half-carry flag: set if carry from bit 3 (i.e., lower nibble overflow)
    cpu.set_flag('H', (old_value & 0xF) == 0xF)
    
    return opcode_info["cycles"][0]


def inc_a(cpu, opcode_info):
    """INC A - Increment register A"""
    # Get current value of A
    old_value = cpu.get_register('A')
    new_value = (old_value + 1) & 0xFF
    
    # Set the new value in A
    cpu.set_register('A', new_value)
    
    # Update flags based on result
    # Zero flag: set if result is 0
    cpu.set_flag('Z', new_value == 0)
    # Negative flag: always 0 for INC
    cpu.set_flag('N', False)
    # Half-carry flag: set if carry from bit 3 (i.e., lower nibble overflow)
    cpu.set_flag('H', (old_value & 0xF) == 0xF)
    
    return opcode_info["cycles"][0]
