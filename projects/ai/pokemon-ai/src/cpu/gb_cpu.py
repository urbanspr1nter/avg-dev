class Registers:
    AF: int = 0
    BC: int = 0
    DE: int = 0
    HL: int = 0
    SP: int = 0
    PC: int = 0


import json
from src.cpu.handlers.ld_handlers import (
    ld_bc_n16,
    ld_bc_a,
    ld_b_n8,
    ld_c_n8,
    ld_d_n8,
    ld_e_n8,
    ld_h_n8,
    ld_l_n8,
    ld_a_n8,
    ld_de_n16,
    ld_hl_n8,
    ld_a_bc,
    ld_a_de,
    ld_de_a,
    ld_sp_hl,
    ld_hli_a,
    ld_a_hli,
    ld_hld_a,
    ld_a_hld,
    ld_hl_n16,
    ld_sp_n16,
    ld_a16_a,
    ld_a_a16,
    ld_a16_sp,
    ld_hl_sp_e8,
)
from src.cpu.handlers.ldh_handlers import (
    ldh_ff_n_a,
    ldh_a_ff_n,
    ldh_ff_c_a,
    ldh_a_ff_c,
)
from src.cpu.handlers.ld_r1_r2_handlers import (
    ld_b_b,
    ld_b_c,
    ld_b_d,
    ld_b_e,
    ld_b_h,
    ld_b_l,
    ld_b_hl,
    ld_b_a,
    ld_c_b,
    ld_c_c,
    ld_c_d,
    ld_c_e,
    ld_c_h,
    ld_c_l,
    ld_c_hl,
    ld_c_a,
    ld_d_b,
    ld_d_c,
    ld_d_d,
    ld_d_e,
    ld_d_h,
    ld_d_l,
    ld_d_hl,
    ld_d_a,
    ld_e_b,
    ld_e_c,
    ld_e_d,
    ld_e_e,
    ld_e_h,
    ld_e_l,
    ld_e_hl,
    ld_e_a,
    ld_h_b,
    ld_h_c,
    ld_h_d,
    ld_h_e,
    ld_h_h,
    ld_h_l,
    ld_h_hl,
    ld_h_a,
    ld_l_b,
    ld_l_c,
    ld_l_d,
    ld_l_e,
    ld_l_h,
    ld_l_l,
    ld_l_hl,
    ld_l_a,
    ld_hl_b,
    ld_hl_c,
    ld_hl_d,
    ld_hl_e,
    ld_hl_h,
    ld_hl_l,
    ld_hl_a,
    ld_a_b,
    ld_a_c,
    ld_a_d,
    ld_a_e,
    ld_a_h,
    ld_a_l,
    ld_a_hl,
    ld_a_a,
)
from src.cpu.handlers.misc_handlers import nop, stop, scf, ccf, cpl, daa
from src.cpu.handlers.interrupt_handlers import di, ei, halt
from src.cpu.handlers.arith_handlers import (
    adc_a_b,
    adc_a_c,
    adc_a_d,
    adc_a_e,
    adc_a_h,
    adc_a_l,
    adc_a_a,
    adc_a_hl,
    add_hl_bc,
    add_hl_de,
    add_hl_hl,
    add_hl_sp,
    add_a_b,
    add_a_c,
    add_a_d,
    add_a_e,
    add_a_h,
    add_a_l,
    add_a_a,
    add_a_n8,
    add_a_hl,
    sub_a_b,
    sub_a_c,
    sub_a_d,
    sub_a_e,
    sub_a_h,
    sub_a_l,
    sub_a_a,
    sub_a_hl,
    sub_a_n8,
    sbc_a_b,
    sbc_a_c,
    sbc_a_d,
    sbc_a_e,
    sbc_a_h,
    sbc_a_l,
    sbc_a_a,
    sbc_a_hl,
    sbc_a_n8,
    adc_a_n8,
    add_sp_e8,
)
from src.cpu.handlers.bitwise_handlers import (
    and_a_b,
    and_a_c,
    and_a_d,
    and_a_e,
    and_a_h,
    and_a_l,
    and_a_a,
    and_a_hl,
    and_a_n8,
    or_a_b,
    or_a_c,
    or_a_d,
    or_a_e,
    or_a_h,
    or_a_l,
    or_a_a,
    or_a_hl,
    or_a_n8,
    xor_a_b,
    xor_a_c,
    xor_a_d,
    xor_a_e,
    xor_a_h,
    xor_a_l,
    xor_a_a,
    xor_a_hl,
    xor_a_n8,
    cp_a_b,
    cp_a_c,
    cp_a_d,
    cp_a_e,
    cp_a_h,
    cp_a_l,
    cp_a_a,
    cp_a_hl,
    cp_a_n8,
)
from src.cpu.handlers.inc_dec_handlers import (
    dec_a,
    dec_b,
    dec_c,
    dec_d,
    dec_e,
    dec_h,
    dec_l,
    inc_a,
    inc_b,
    inc_c,
    inc_d,
    inc_e,
    inc_h,
    inc_l,
    inc_bc,
    dec_bc,
    inc_de,
    dec_de,
    inc_hl,
    dec_hl,
    inc_sp,
    dec_sp,
    inc_hl_indirect,
    dec_hl_indirect,
)
from src.cpu.handlers.rotate_handlers import (
    rlc_a,
    rrc_a,
    rl_a,
    rr_a,
)
from src.cpu.handlers.stack_handlers import (
    push_af,
    push_bc,
    push_de,
    push_hl,
    pop_af,
    pop_bc,
    pop_de,
    pop_hl,
)
from src.cpu.handlers.cb_handlers import build_cb_dispatch
from src.cpu.handlers.jump_handlers import (
    jp_nn,
    jp_nz_nn,
    jp_z_nn,
    jp_nc_nn,
    jp_c_nn,
    jp_hl,
    jr_n,
    jr_nz_n,
    jr_z_n,
    jr_nc_n,
    jr_c_n,
    call_nn,
    call_nz_nn,
    call_z_nn,
    call_nc_nn,
    call_c_nn,
    ret,
    ret_nz,
    ret_z,
    ret_nc,
    ret_c,
    reti,
    rst_00h,
    rst_08h,
    rst_10h,
    rst_18h,
    rst_20h,
    rst_28h,
    rst_30h,
    rst_38h,
)


class Interrupts:
    """Game Boy interrupt system."""

    def __init__(self, cpu=None):
        self.ime = False  # Interrupt Master Enable flag
        self.halted = False  # HALT state flag
        self.enabled = False  # Legacy flag, kept for compatibility
        self.ime_pending = False  # EI instruction delay flag
        self.ime_handled_by_instruction = False  # Flag to track if current instruction already handled IME enable
        self.halt_bug = False  # HALT bug: next instruction byte read twice when HALT with IME=0 and pending interrupt
        self._cpu = cpu  # Reference to CPU for memory access

    def check_interrupts(self, cpu):
        """Check for pending interrupts and service them if enabled.
        
        Returns:
            int: Number of cycles used (0 if no interrupt serviced)
        """
        if not self.ime:
            return 0  # No cycles used if interrupts disabled
        
        if_reg = cpu.memory.get_value(0xFF0F)  # Interrupt Flag register
        ie_reg = cpu.memory.get_value(0xFFFF)  # Interrupt Enable register
        pending = if_reg & ie_reg
        
        # Check interrupts in priority order (V-Blank has highest priority)
        if pending & 0x01:  # V-Blank interrupt
            return self.service_interrupt(cpu, 0x40, 0x01)
        elif pending & 0x02:  # LCD STAT interrupt
            return self.service_interrupt(cpu, 0x48, 0x02)
        elif pending & 0x04:  # Timer interrupt
            return self.service_interrupt(cpu, 0x50, 0x04)
        elif pending & 0x08:  # Serial interrupt
            return self.service_interrupt(cpu, 0x58, 0x08)
        elif pending & 0x10:  # Joypad interrupt
            return self.service_interrupt(cpu, 0x60, 0x10)
        
        return 0
    
    def service_interrupt(self, cpu, handler_address, interrupt_bit):
        """Service an interrupt.
        
        Args:
            cpu: CPU instance
            handler_address: Address of interrupt handler
            interrupt_bit: Bit to clear in IF register
            
        Returns:
            int: Number of cycles used (20 for interrupt handling)
        """
        # Disable interrupts during service
        self.ime = False
        self.halted = False
        
        # Push current PC to stack (16-bit operation)
        cpu.push_word(cpu.registers.PC)
        
        # Jump to handler
        cpu.registers.PC = handler_address
        
        # Clear the specific interrupt flag
        if_reg = cpu.memory.get_value(0xFF0F)
        cpu.memory.set_value(0xFF0F, if_reg & ~interrupt_bit)
        
        return 20  # Interrupt handling takes 20 cycles

    def get_if_register(self) -> int:
        """Get current IF (Interrupt Flag) register value."""
        # Read directly from memory array to avoid circular calls
        return self._cpu.memory.memory[0xFF0F] & 0x1F
    
    def set_if_register(self, value: int):
        """Set IF (Interrupt Flag) register value."""
        # Write directly to memory array to avoid circular calls
        self._cpu.memory.memory[0xFF0F] = value & 0x1F
    
    def get_ie_register(self) -> int:
        """Get current IE (Interrupt Enable) register value."""
        # Read directly from memory array to avoid circular calls
        return self._cpu.memory.memory[0xFFFF] & 0x1F
    
    def set_ie_register(self, value: int):
        """Set IE (Interrupt Enable) register value."""
        # Write directly to memory array to avoid circular calls
        # Store full 8-bit value in memory, but only lower 5 bits are used for interrupts
        self._cpu.memory.memory[0xFFFF] = value & 0xFF


class CPU:
    def __init__(self, memory=None):
        self.registers = Registers()
        self.current_cycles = 0
        self.operand_values = []

        # Minimal interrupts interface for RETI instruction
        self.interrupts = Interrupts(self)

        self.opcodes_db = {}
        with open("Opcodes.json", "r") as f:
            self.opcodes_db = json.load(f)

        # Memory instance can be injected for testing or real use.
        if memory is None:
            from src.memory.gb_memory import Memory

            self.memory = Memory()
        else:
            self.memory = memory
        
        # Set CPU reference in memory for interrupt register handling
        self.memory._cpu = self

        # Timer reference — picked up from memory if already loaded (e.g. unit
        # tests that load timer before CPU), or set later by Memory.load_timer()
        # when using the normal GameBoy initialization order (Memory -> CPU ->
        # load_timer). Both paths are covered so timer works regardless of order.
        self._timer = self.memory._timer

        # Initialize dispatch table for opcode handlers
        self.opcode_handlers = {
            0x00: nop,
            0x10: stop,
            0x01: ld_bc_n16,
            0x02: ld_bc_a,
            0x03: inc_bc,
            0x04: inc_b,
            0x05: dec_b,
            0x08: ld_a16_sp,
            0x09: add_hl_bc,
            0x0A: ld_a_bc,
            0x0B: dec_bc,
            0x0C: inc_c,
            0x0D: dec_c,
            0x12: ld_de_a,
            0x13: inc_de,
            0x14: inc_d,
            0x15: dec_d,
            0x19: add_hl_de,
            0x1A: ld_a_de,
            0x1B: dec_de,
            0x1C: inc_e,
            0x1D: dec_e,
            0x21: ld_hl_n16,
            0x22: ld_hli_a,
            0x23: inc_hl,
            0x24: inc_h,
            0x25: dec_h,
            0x29: add_hl_hl,
            0x2A: ld_a_hli,
            0x2B: dec_hl,
            0x2C: inc_l,
            0x2D: dec_l,
            0x31: ld_sp_n16,
            0x32: ld_hld_a,
            0x33: inc_sp,
            0x34: inc_hl_indirect,
            0x35: dec_hl_indirect,
            0x39: add_hl_sp,
            0x3A: ld_a_hld,
            0x3B: dec_sp,
            0x3C: inc_a,
            0x3D: dec_a,
            0x07: rlc_a,
            0x0F: rrc_a,
            0x17: rl_a,
            0x1F: rr_a,
            0x06: ld_b_n8,
            0x0E: ld_c_n8,
            0x11: ld_de_n16,
            0x16: ld_d_n8,
            0x1E: ld_e_n8,
            0x26: ld_h_n8,
            0x2E: ld_l_n8,
            0x2F: cpl,
            0x36: ld_hl_n8,
            0x37: scf,
            0x3F: ccf,
            0x3E: ld_a_n8,
            # Interrupt control instructions
            0xF3: di,
            0xFB: ei,
            0x76: halt,
            # LD r1, r2 instructions (register to register transfers)
            0x40: ld_b_b,
            0x41: ld_b_c,
            0x42: ld_b_d,
            0x43: ld_b_e,
            0x44: ld_b_h,
            0x45: ld_b_l,
            0x46: ld_b_hl,
            0x47: ld_b_a,
            0x48: ld_c_b,
            0x49: ld_c_c,
            0x4A: ld_c_d,
            0x4B: ld_c_e,
            0x4C: ld_c_h,
            0x4D: ld_c_l,
            0x4E: ld_c_hl,
            0x4F: ld_c_a,
            0x50: ld_d_b,
            0x51: ld_d_c,
            0x52: ld_d_d,
            0x53: ld_d_e,
            0x54: ld_d_h,
            0x55: ld_d_l,
            0x56: ld_d_hl,
            0x57: ld_d_a,
            0x58: ld_e_b,
            0x59: ld_e_c,
            0x5A: ld_e_d,
            0x5B: ld_e_e,
            0x5C: ld_e_h,
            0x5D: ld_e_l,
            0x5E: ld_e_hl,
            0x5F: ld_e_a,
            0x60: ld_h_b,
            0x61: ld_h_c,
            0x62: ld_h_d,
            0x63: ld_h_e,
            0x64: ld_h_h,
            0x65: ld_h_l,
            0x66: ld_h_hl,
            0x67: ld_h_a,
            0x68: ld_l_b,
            0x69: ld_l_c,
            0x6A: ld_l_d,
            0x6B: ld_l_e,
            0x6C: ld_l_h,
            0x6D: ld_l_l,
            0x6E: ld_l_hl,
            0x6F: ld_l_a,
            0x70: ld_hl_b,
            0x71: ld_hl_c,
            0x72: ld_hl_d,
            0x73: ld_hl_e,
            0x74: ld_hl_h,
            0x75: ld_hl_l,
            0x77: ld_hl_a,
            0x78: ld_a_b,
            0x79: ld_a_c,
            0x7A: ld_a_d,
            0x7B: ld_a_e,
            0x7C: ld_a_h,
            0x7D: ld_a_l,
            0x7E: ld_a_hl,
            0x7F: ld_a_a,
            0x80: add_a_b,
            0x81: add_a_c,
            0x82: add_a_d,
            0x83: add_a_e,
            0x84: add_a_h,
            0x85: add_a_l,
            0x86: add_a_hl,
            0x87: add_a_a,
            0x88: adc_a_b,
            0x89: adc_a_c,
            0x8A: adc_a_d,
            0x8B: adc_a_e,
            0x8C: adc_a_h,
            0x8D: adc_a_l,
            0x8E: adc_a_hl,
            0x8F: adc_a_a,
            0x90: sub_a_b,
            0x91: sub_a_c,
            0x92: sub_a_d,
            0x93: sub_a_e,
            0x94: sub_a_h,
            0x95: sub_a_l,
            0x96: sub_a_hl,
            0x97: sub_a_a,
            0x98: sbc_a_b,
            0x99: sbc_a_c,
            0x9A: sbc_a_d,
            0x9B: sbc_a_e,
            0x9C: sbc_a_h,
            0x9D: sbc_a_l,
            0x9E: sbc_a_hl,
            0x9F: sbc_a_a,
            0xA0: and_a_b,
            0xA1: and_a_c,
            0xA2: and_a_d,
            0xA3: and_a_e,
            0xA4: and_a_h,
            0xA5: and_a_l,
            0xA6: and_a_hl,
            0xA7: and_a_a,
            0xE6: and_a_n8,
            0xB0: or_a_b,
            0xB1: or_a_c,
            0xB2: or_a_d,
            0xB3: or_a_e,
            0xB4: or_a_h,
            0xB5: or_a_l,
            0xB6: or_a_hl,
            0xB7: or_a_a,
            0xF6: or_a_n8,
            0xA8: xor_a_b,
            0xA9: xor_a_c,
            0xAA: xor_a_d,
            0xAB: xor_a_e,
            0xAC: xor_a_h,
            0xAD: xor_a_l,
            0xAE: xor_a_hl,
            0xAF: xor_a_a,
            0xEE: xor_a_n8,
            0xB8: cp_a_b,
            0xB9: cp_a_c,
            0xBA: cp_a_d,
            0xBB: cp_a_e,
            0xBC: cp_a_h,
            0xBD: cp_a_l,
            0xBE: cp_a_hl,
            0xBF: cp_a_a,
            0xFE: cp_a_n8,
            # Stack operations
            0xC1: pop_bc,
            0xC5: push_bc,
            0xD1: pop_de,
            0xD5: push_de,
            0xE1: pop_hl,
            0xE5: push_hl,
            0xF1: pop_af,
            0xF5: push_af,
            # Immediate value arithmetic operations
            0xC6: add_a_n8,
            0xD6: sub_a_n8,
            0xDE: sbc_a_n8,
            # LDH (Load Half) instructions for HRAM/I/O access
            0xE0: ldh_ff_n_a,
            0xF0: ldh_a_ff_n,
            0xE2: ldh_ff_c_a,
            0xF2: ldh_a_ff_c,
            # Absolute address and SP-relative load/store instructions
            0xEA: ld_a16_a,
            0xFA: ld_a_a16,
            0xF8: ld_hl_sp_e8,
            0xF9: ld_sp_hl,
            # Arithmetic with immediate
            0xCE: adc_a_n8,
            0xE8: add_sp_e8,
            # Miscellaneous
            0x27: daa,
            # Jump instructions
            0xC3: jp_nn,
            0xC2: jp_nz_nn,
            0xCA: jp_z_nn,
            0xD2: jp_nc_nn,
            0xDA: jp_c_nn,
            0x18: jr_n,
            0x20: jr_nz_n,
            0x28: jr_z_n,
            0x30: jr_nc_n,
            0x38: jr_c_n,
            0xE9: jp_hl,
            # Call/Return instructions
            0xCD: call_nn,
            0xC4: call_nz_nn,
            0xCC: call_z_nn,
            0xD4: call_nc_nn,
            0xDC: call_c_nn,
            0xC9: ret,
            0xC0: ret_nz,
            0xC8: ret_z,
            0xD0: ret_nc,
            0xD8: ret_c,
            0xD9: reti,
            # Restart instructions
            0xC7: rst_00h,
            0xCF: rst_08h,
            0xD7: rst_10h,
            0xDF: rst_18h,
            0xE7: rst_20h,
            0xEF: rst_28h,
            0xF7: rst_30h,
            0xFF: rst_38h,
        }

        # CB-prefixed opcode dispatch table (256 entries)
        self.cb_opcode_handlers = build_cb_dispatch()

    def get_register(self, code):
        """Return the value of a register or its high/low byte."""
        if code == "AF":
            return self.registers.AF
        elif code == "A":
            return (self.registers.AF >> 8) & 0xFF
        elif code == "BC":
            return self.registers.BC
        elif code == "B":
            return (self.registers.BC >> 8) & 0xFF
        elif code == "C":
            return self.registers.BC & 0xFF
        elif code == "DE":
            return self.registers.DE
        elif code == "D":
            return (self.registers.DE >> 8) & 0xFF
        elif code == "E":
            return self.registers.DE & 0xFF
        elif code == "HL":
            return self.registers.HL
        elif code == "H":
            return (self.registers.HL >> 8) & 0xFF
        elif code == "L":
            return self.registers.HL & 0xFF
        elif code == "SP":
            return self.registers.SP
        elif code == "PC":
            return self.registers.PC
        else:
            raise ValueError(f"Unknown register code: {code}")

    def get_register_pair(self, pair_name):
        """Return the 16-bit value of a register pair.

        Args:
            pair_name: 'BC', 'DE', 'HL', or 'SP'

        Returns:
            int: The 16-bit value
        """
        if pair_name == "BC":
            return self.registers.BC
        elif pair_name == "DE":
            return self.registers.DE
        elif pair_name == "HL":
            return self.registers.HL
        elif pair_name == "SP":
            return self.registers.SP
        else:
            raise ValueError(f"Unknown register pair: {pair_name}")

    def set_register_pair(self, pair_name, value):
        """Set the 16-bit value of a register pair.

        Args:
            pair_name: 'BC', 'DE', 'HL', or 'SP'
            value: The 16-bit value to set
        """
        if pair_name == "BC":
            self.registers.BC = value
        elif pair_name == "DE":
            self.registers.DE = value
        elif pair_name == "HL":
            self.registers.HL = value
        elif pair_name == "SP":
            self.registers.SP = value
        else:
            raise ValueError(f"Unknown register pair: {pair_name}")

    def set_register(self, code, value):
        """Set the value of a register or its high/low byte."""
        if code == "AF":
            self.registers.AF = value
        elif code == "A":
            self.registers.AF = ((value & 0xFF) << 8) | (self.registers.AF & 0x00FF)
        elif code == "BC":
            self.registers.BC = value
        elif code == "B":
            self.registers.BC = ((value & 0xFF) << 8) | (self.registers.BC & 0x00FF)
        elif code == "C":
            self.registers.BC = (self.registers.BC & 0xFF00) | (value & 0xFF)
        elif code == "DE":
            self.registers.DE = value
        elif code == "D":
            self.registers.DE = ((value & 0xFF) << 8) | (self.registers.DE & 0x00FF)
        elif code == "E":
            self.registers.DE = (self.registers.DE & 0xFF00) | (value & 0xFF)
        elif code == "HL":
            self.registers.HL = value
        elif code == "H":
            self.registers.HL = ((value & 0xFF) << 8) | (self.registers.HL & 0x00FF)
        elif code == "L":
            self.registers.HL = (self.registers.HL & 0xFF00) | (value & 0xFF)
        elif code == "SP":
            self.registers.SP = value
        elif code == "PC":
            self.registers.PC = value
        else:
            raise ValueError(f"Unknown register code: {code}")

    # Flag manipulation helpers

    def get_flag(self, flag):
        """Get the value of a CPU flag.

        Args:
            flag: 'Z', 'N', 'H', or 'C'

        Returns:
            bool: True if flag is set, False otherwise
        """
        flags = self.registers.AF & 0xFF
        if flag == "Z":
            return (flags & 0x80) != 0
        elif flag == "N":
            return (flags & 0x40) != 0
        elif flag == "H":
            return (flags & 0x20) != 0
        elif flag == "C":
            return (flags & 0x10) != 0
        else:
            raise ValueError(f"Unknown flag: {flag}")

    def set_flag(self, flag, value):
        """Set a CPU flag to a specific value.

        Args:
            flag: 'Z', 'N', 'H', or 'C'
            value: bool or int (0/1) - True/1 to set, False/0 to clear
        """
        flags = self.registers.AF & 0xFF

        if flag == "Z":
            if value:
                flags |= 0x80
            else:
                flags &= ~0x80
        elif flag == "N":
            if value:
                flags |= 0x40
            else:
                flags &= ~0x40
        elif flag == "H":
            if value:
                flags |= 0x20
            else:
                flags &= ~0x20
        elif flag == "C":
            if value:
                flags |= 0x10
            else:
                flags &= ~0x10
        else:
            raise ValueError(f"Unknown flag: {flag}")

        # Update AF register with new flags (preserve A register in high byte)
        self.registers.AF = (self.registers.AF & 0xFF00) | flags

    # Flag calculation helpers

    def calc_zero_flag(self, result):
        """Calculate Zero flag based on result.

        Args:
            result: int - The result value to check

        Returns:
            bool: True if result is 0, False otherwise
        """
        return (result & 0xFF) == 0

    def calc_half_carry_add_8bit(self, a, b, carry=0):
        """Calculate Half-carry flag for 8-bit addition.

        Args:
            a: int - First operand
            b: int - Second operand
            carry: int - Carry in (0 or 1)

        Returns:
            bool: True if carry from bit 3 to bit 4, False otherwise
        """
        return ((a & 0xF) + (b & 0xF) + carry) > 0xF

    def calc_carry_add_8bit(self, a, b, carry=0):
        """Calculate Carry flag for 8-bit addition.

        Args:
            a: int - First operand
            b: int - Second operand
            carry: int - Carry in (0 or 1)

        Returns:
            bool: True if carry from bit 7, False otherwise
        """
        return (a + b + carry) > 0xFF

    def calc_half_carry_sub_8bit(self, a, b, carry=0):
        """Calculate Half-carry flag for 8-bit subtraction.

        Args:
            a: int - First operand (minuend)
            b: int - Second operand (subtrahend)
            carry: int - Borrow in (0 or 1)

        Returns:
            bool: True if borrow from bit 4, False otherwise
        """
        return (int(a & 0xF) - int(b & 0xF) - carry) < 0

    def calc_carry_sub_8bit(self, a, b, carry=0):
        """Calculate Carry flag for 8-bit subtraction.

        Args:
            a: int - First operand (minuend)
            b: int - Second operand (subtrahend)
            carry: int - Borrow in (0 or 1)

        Returns:
            bool: True if borrow occurred, False otherwise
        """
        return (a - b - carry) < 0

    def calc_half_carry_add_16bit(self, a, b):
        """Calculate Half-carry flag for 16-bit addition.

        Args:
            a: int - First operand
            b: int - Second operand

        Returns:
            bool: True if carry from bit 11 to bit 12, False otherwise
        """
        return ((a & 0xFFF) + (b & 0xFFF)) > 0xFFF

    def calc_carry_add_16bit(self, a, b):
        """Calculate Carry flag for 16-bit addition.

        Args:
            a: int - First operand
            b: int - Second operand

        Returns:
            bool: True if carry from bit 15, False otherwise
        """
        return (a + b) > 0xFFFF

    # Stack operation helpers

    def push_word(self, value):
        """Push a 16-bit word onto the stack.

        The stack grows downward in memory. SP is decremented by 2,
        then the word is written in little-endian format.

        Args:
            value: int - 16-bit value to push
        """
        self.registers.SP = (self.registers.SP - 1) & 0xFFFF
        self.memory.set_value(self.registers.SP, (value >> 8) & 0xFF)  # High byte
        self.registers.SP = (self.registers.SP - 1) & 0xFFFF
        self.memory.set_value(self.registers.SP, value & 0xFF)  # Low byte

    def pop_word(self):
        """Pop a 16-bit word from the stack.

        The word is read in little-endian format, then SP is incremented by 2.

        Returns:
            int: 16-bit value popped from stack
        """
        low = self.memory.get_value(self.registers.SP)
        self.registers.SP = (self.registers.SP + 1) & 0xFFFF
        high = self.memory.get_value(self.registers.SP)
        self.registers.SP = (self.registers.SP + 1) & 0xFFFF
        return (high << 8) | low

    def fetch_byte(self, address):
        """Fetch a single byte from memory at the given address."""
        return self.memory.get_value(address)

    def fetch_word(self, address):
        """Fetch a 16-bit word from memory at the given address (little-endian)."""
        low = self.memory.get_value(address)
        high = self.memory.get_value(address + 1)
        return (high << 8) | low

    def fetch(self):
        """Fetch the current opcode from memory at PC and increment PC."""
        opcode = self.fetch_byte(self.registers.PC)
        self.registers.PC = (self.registers.PC + 1) & 0xFFFF
        return opcode

    def run(self, max_cycles=-1):
        cycles_consumed = 0
        while True:
            if max_cycles >= 0 and self.current_cycles >= max_cycles:
                break

            # Handle HALT state: idle until an interrupt wakes CPU
            if self.interrupts.halted:
                if_reg = self.memory.get_value(0xFF0F)
                ie_reg = self.memory.get_value(0xFFFF)
                if if_reg & ie_reg:
                    # Any pending interrupt wakes CPU (regardless of IME)
                    self.interrupts.halted = False
                    # Fall through to normal interrupt check / instruction fetch
                else:
                    # No interrupt pending — consume one machine cycle and loop
                    self.current_cycles += 4
                    cycles_consumed += 4
                    if self._timer:
                        self._timer.tick(4)
                    continue

            # Check if we need to enable IME after the previous instruction
            # This implements the EI delay: IME is enabled after the instruction following EI
            ime_was_pending = self.interrupts.ime_pending
            # Reset flag that tracks if IME was already handled by this instruction
            self.interrupts.ime_handled_by_instruction = False

            # Check for interrupts if IME is already enabled (not during EI delay)
            if self.interrupts.ime:
                interrupt_cycles = self.interrupts.check_interrupts(self)
                if interrupt_cycles > 0:
                    self.current_cycles += interrupt_cycles
                    cycles_consumed += interrupt_cycles
                    continue  # Skip normal instruction fetch after interrupt

            self.operand_values = []

            # Fetch the opcode
            opcode = self.fetch()

            # HALT bug: undo PC increment so the byte after HALT is read twice
            if self.interrupts.halt_bug:
                self.registers.PC = (self.registers.PC - 1) & 0xFFFF
                self.interrupts.halt_bug = False

            # Look up the opcode in our database
            opcode_info = None
            is_cb_prefix = False

            # Check if it's a prefixed opcode (0xCB)
            if opcode == 0xCB:
                is_cb_prefix = True
                # Fetch the second byte for prefixed instructions
                opcode = self.fetch_byte(self.registers.PC)
                self.registers.PC = (self.registers.PC + 1) & 0xFFFF

                opcode_info = self.opcodes_db["cbprefixed"].get(f"0x{opcode:02X}")
            else:
                opcode_info = self.opcodes_db["unprefixed"].get(f"0x{opcode:02X}")

            # If we don't have the opcode implemented, raise an exception
            if opcode_info is None:
                raise NotImplementedError(f"Opcode {opcode:#04x} not implemented")

            # Fetch and construct operand dictionaries
            operands = opcode_info["operands"]
            for operand in operands:
                operand_name = operand["name"]
                operand_immediate = operand["immediate"]

                if "bytes" in operand:
                    # Operand has data to fetch from instruction stream
                    num_bytes_for_operand = operand["bytes"]
                    if num_bytes_for_operand == 1:
                        fetched_value = self.fetch_byte(self.registers.PC)
                    elif num_bytes_for_operand == 2:
                        fetched_value = self.fetch_word(self.registers.PC)
                    else:
                        raise ValueError(
                            "Not implemented yet to fetch more than 2 bytes."
                        )

                    self.registers.PC = (self.registers.PC + operand["bytes"]) & 0xFFFF

                    # Determine operand type
                    if operand_name == "a16":
                        operand_type = "immediate_address"
                    else:
                        # n8, n16, e8, r8
                        operand_type = "immediate_value"

                    self.operand_values.append(
                        {
                            "name": operand_name,
                            "value": fetched_value,
                            "immediate": operand_immediate,
                            "type": operand_type,
                        }
                    )
                else:
                    # Register operand (no bytes to fetch)
                    if operand_immediate:
                        operand_type = "register"
                    else:
                        operand_type = "register_indirect"

                    # Skip condition codes - these are part of the opcode mnemonic
                    # Only skip for conditional instructions (which have multiple cycle counts)
                    is_conditional = len(opcode_info.get("cycles", [])) > 1
                    if is_conditional and operand_name in ["Z", "NZ", "C", "NC"]:
                        pass
                    else:
                        self.operand_values.append(
                            {
                                "name": operand_name,
                                "value": operand_name,
                                "immediate": operand_immediate,
                                "type": operand_type,
                            }
                        )

            # Dispatch to the handler and accumulate cycles
            if is_cb_prefix:
                handler = self.cb_opcode_handlers.get(opcode)
            else:
                handler = self.opcode_handlers.get(opcode)
            if handler is None:
                raise NotImplementedError(
                    f"Handler for opcode {opcode:#04x} not implemented"
                )

            cycles_used = handler(self, opcode_info)
            self.current_cycles += cycles_used
            cycles_consumed += cycles_used
            if self._timer:
                self._timer.tick(cycles_used)

            # Handle delayed IME enable from EI instruction
            # This happens AFTER the instruction executes for correct EI delay timing
            # Only enable if:
            #   - ime_pending was set BEFORE this instruction started
            #   - ime_pending is STILL set (DI would have cleared it)
            #   - the instruction didn't already handle IME itself (e.g., HALT)
            if ime_was_pending and self.interrupts.ime_pending and not self.interrupts.ime_handled_by_instruction:
                self.interrupts.ime = True
                self.interrupts.ime_pending = False

        # End of while loop
        return cycles_consumed
