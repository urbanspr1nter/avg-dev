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
    # Set pending flag instead of immediate enable
    cpu.interrupts.ime_pending = True
    return opcode_info["cycles"][0]


def halt(cpu, opcode_info):
    """HALT - Halt CPU

    Puts the CPU into a low-power halt state until an interrupt occurs.
    When an interrupt occurs, the CPU resumes execution at the interrupt handler.

    Cycle count: 4 (but actual behavior depends on when interrupt occurs)
    """
    cpu.interrupts.halted = True

    # If interrupts are enabled (or will be via EI delay), check for pending interrupts
    if cpu.interrupts.ime or cpu.interrupts.ime_pending:
        if_reg = cpu.memory.get_value(0xFF0F)
        ie_reg = cpu.memory.get_value(0xFFFF)
        pending = if_reg & ie_reg

        if pending:
            # If IME was pending from EI delay, promote it immediately.
            # HALT can't wait for the normal end-of-instruction enable.
            if cpu.interrupts.ime_pending:
                cpu.interrupts.ime_pending = False
                cpu.interrupts.ime = True
                cpu.interrupts.ime_handled_by_instruction = True

            # Service highest priority pending interrupt
            # (service_interrupt will disable IME and clear halted)
            for bit, addr in ((0x01, 0x40), (0x02, 0x48), (0x04, 0x50), (0x08, 0x58), (0x10, 0x60)):
                if pending & bit:
                    return opcode_info["cycles"][0] + cpu.interrupts.service_interrupt(cpu, addr, bit)

    return opcode_info["cycles"][0]