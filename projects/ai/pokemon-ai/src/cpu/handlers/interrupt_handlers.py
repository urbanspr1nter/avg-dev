def di(cpu, opcode_info):
    """DI - Disable Interrupts
    
    Sets the Interrupt Master Enable (IME) flag to 0, disabling all interrupts.
    This takes effect immediately after the DI instruction is executed.
    
    Cycle count: 4
    """
    cpu.interrupts.ime = False
    return opcode_info["cycles"][0]


def ei(cpu, opcode_info):
    """EI - Enable Interrupts
    
    Sets the Interrupt Master Enable (IME) flag to 1, enabling interrupts.
    Note: Interrupts are not enabled immediately - they become enabled after
    the instruction following EI is executed.
    
    Cycle count: 4
    """
    # For now, enable immediately. We'll handle the delay in a future refinement.
    cpu.interrupts.ime = True
    return opcode_info["cycles"][0]


def halt(cpu, opcode_info):
    """HALT - Halt CPU
    
    Puts the CPU into a low-power halt state until an interrupt occurs.
    When an interrupt occurs, the CPU resumes execution at the interrupt handler.
    
    Cycle count: 4 (but actual behavior depends on when interrupt occurs)
    """
    cpu.interrupts.halted = True
    
    # Check for interrupts immediately after HALT
    # If interrupts are pending and enabled, service them immediately
    if cpu.interrupts.ime:
        if_reg = cpu.memory.get_value(0xFF0F)
        ie_reg = cpu.memory.get_value(0xFFFF)
        pending = if_reg & ie_reg
        
        if pending:
            # Service the highest priority interrupt
            if pending & 0x01:  # V-Blank
                return cpu.interrupts.service_interrupt(cpu, 0x40, 0x01)
            elif pending & 0x02:  # LCD STAT
                return cpu.interrupts.service_interrupt(cpu, 0x48, 0x02)
            elif pending & 0x04:  # Timer
                return cpu.interrupts.service_interrupt(cpu, 0x50, 0x04)
            elif pending & 0x08:  # Serial
                return cpu.interrupts.service_interrupt(cpu, 0x58, 0x08)
            elif pending & 0x10:  # Joypad
                return cpu.interrupts.service_interrupt(cpu, 0x60, 0x10)
    
    return opcode_info["cycles"][0]