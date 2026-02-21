def di(cpu, opcode_info):
    """DI - Disable Interrupts
    
    Sets the Interrupt Master Enable (IME) flag to 0, disabling all interrupts.
    This takes effect immediately after the DI instruction is executed.
    
    Cycle count: 4
    """
    cpu.interrupts.ime = False
    cpu.interrupts.ime_pending = False
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
    The run loop handles idling and wake-up when halted.

    Four cases:
      IME=1 + pending interrupt  -> service immediately, don't stay halted
      IME=1 + no pending         -> enter halt, wait for interrupt
      IME=0 + pending interrupt  -> HALT bug: don't halt, next byte read twice
      IME=0 + no pending         -> enter halt, wait for interrupt

    When ime_pending is set (EI delay), it is promoted to IME=1 first.

    Cycle count: 4 (plus 20 if interrupt serviced immediately)
    """
    if_reg = cpu.memory.get_value(0xFF0F)
    ie_reg = cpu.memory.get_value(0xFFFF)
    pending = if_reg & ie_reg

    # Promote EI delay if active
    ime_effective = cpu.interrupts.ime
    if cpu.interrupts.ime_pending:
        cpu.interrupts.ime_pending = False
        cpu.interrupts.ime = True
        cpu.interrupts.ime_handled_by_instruction = True
        ime_effective = True

    if pending and ime_effective:
        # IME=1 + pending: service interrupt immediately (don't actually halt)
        cpu.interrupts.halted = True  # service_interrupt will clear this
        for bit, addr in ((0x01, 0x40), (0x02, 0x48), (0x04, 0x50), (0x08, 0x58), (0x10, 0x60)):
            if pending & bit:
                return opcode_info["cycles"][0] + cpu.interrupts.service_interrupt(cpu, addr, bit)
    elif pending and not ime_effective:
        # IME=0 + pending: HALT bug — CPU doesn't halt, next byte read twice
        cpu.interrupts.halt_bug = True
    else:
        # No pending interrupt: enter halt state (run loop will idle)
        cpu.interrupts.halted = True

    return opcode_info["cycles"][0]