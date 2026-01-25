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
)
from src.cpu.handlers.jr_handlers import jr_nz_e8
from src.cpu.handlers.misc_handlers import nop
from src.cpu.handlers.inc_dec_handlers import (
    dec_a, dec_b, dec_c, dec_d, dec_e, dec_h, dec_l,
    inc_a, inc_b, inc_c, inc_d, inc_e, inc_h, inc_l,
)

class CPU:
    def __init__(self, memory=None):
        self.registers = Registers()
        self.current_cycles = 0
        self.operand_values = []

        self.opcodes_db = {}
        with open("Opcodes.json", "r") as f:
            self.opcodes_db = json.load(f)

        # Memory instance can be injected for testing or real use.
        if memory is None:
            from src.memory.gb_memory import Memory
            self.memory = Memory()
        else:
            self.memory = memory

        # Initialize dispatch table for opcode handlers
        self.opcode_handlers = {
            0x00: nop,
            0x01: ld_bc_n16,
            0x02: ld_bc_a,
            0x04: inc_b,
            0x05: dec_b,
            0x0C: inc_c,
            0x0D: dec_c,
            0x14: inc_d,
            0x15: dec_d,
            0x1C: inc_e,
            0x1D: dec_e,
            0x24: inc_h,
            0x25: dec_h,
            0x2C: inc_l,
            0x2D: dec_l,
            0x3C: inc_a,
            0x3D: dec_a,
            0x06: ld_b_n8,
            0x0E: ld_c_n8,
            0x11: ld_de_n16,
            0x16: ld_d_n8,
            0x1E: ld_e_n8,
            0x26: ld_h_n8,
            0x2E: ld_l_n8,
            0x3E: ld_a_n8,
            0x20: jr_nz_e8,
        }

    def get_register(self, code):
        """Return the value of a register or its high/low byte."""
        if code == 'AF':
            return self.registers.AF
        elif code == 'A':
            return (self.registers.AF >> 8) & 0xFF
        elif code == 'BC':
            return self.registers.BC
        elif code == 'B':
            return (self.registers.BC >> 8) & 0xFF
        elif code == 'C':
            return self.registers.BC & 0xFF
        elif code == 'DE':
            return self.registers.DE
        elif code == 'D':
            return (self.registers.DE >> 8) & 0xFF
        elif code == 'E':
            return self.registers.DE & 0xFF
        elif code == 'HL':
            return self.registers.HL
        elif code == 'H':
            return (self.registers.HL >> 8) & 0xFF
        elif code == 'L':
            return self.registers.HL & 0xFF
        elif code == 'SP':
            return self.registers.SP
        elif code == 'PC':
            return self.registers.PC
        else:
            raise ValueError(f'Unknown register code: {code}')


    def set_register(self, code, value):
        """Set the value of a register or its high/low byte."""
        if code == 'AF':
            self.registers.AF = value
        elif code == 'A':
            self.registers.AF = ((value & 0xFF) << 8) | (self.registers.AF & 0x00FF)
        elif code == 'BC':
            self.registers.BC = value
        elif code == 'B':
            self.registers.BC = ((value & 0xFF) << 8) | (self.registers.BC & 0x00FF)
        elif code == 'C':
            self.registers.BC = (self.registers.BC & 0xFF00) | (value & 0xFF)
        elif code == 'DE':
            self.registers.DE = value
        elif code == 'D':
            self.registers.DE = ((value & 0xFF) << 8) | (self.registers.DE & 0x00FF)
        elif code == 'E':
            self.registers.DE = (self.registers.DE & 0xFF00) | (value & 0xFF)
        elif code == 'HL':
            self.registers.HL = value
        elif code == 'H':
            self.registers.HL = ((value & 0xFF) << 8) | (self.registers.HL & 0x00FF)
        elif code == 'L':
            self.registers.HL = (self.registers.HL & 0xFF00) | (value & 0xFF)
        elif code == 'SP':
            self.registers.SP = value
        elif code == 'PC':
            self.registers.PC = value
        else:
            raise ValueError(f'Unknown register code: {code}')

    # Flag manipulation helpers

    def get_flag(self, flag):
        """Get the value of a CPU flag.
        
        Args:
            flag: 'Z', 'N', 'H', or 'C'
        
        Returns:
            bool: True if flag is set, False otherwise
        """
        flags = self.registers.AF & 0xFF
        if flag == 'Z':
            return (flags & 0x80) != 0
        elif flag == 'N':
            return (flags & 0x40) != 0
        elif flag == 'H':
            return (flags & 0x20) != 0
        elif flag == 'C':
            return (flags & 0x10) != 0
        else:
            raise ValueError(f'Unknown flag: {flag}')

    def set_flag(self, flag, value):
        """Set a CPU flag to a specific value.
        
        Args:
            flag: 'Z', 'N', 'H', or 'C'
            value: bool or int (0/1) - True/1 to set, False/0 to clear
        """
        flags = self.registers.AF & 0xFF
        
        if flag == 'Z':
            if value:
                flags |= 0x80
            else:
                flags &= ~0x80
        elif flag == 'N':
            if value:
                flags |= 0x40
            else:
                flags &= ~0x40
        elif flag == 'H':
            if value:
                flags |= 0x20
            else:
                flags &= ~0x20
        elif flag == 'C':
            if value:
                flags |= 0x10
            else:
                flags &= ~0x10
        else:
            raise ValueError(f'Unknown flag: {flag}')
        
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

        while True:
            if max_cycles >= 0 and self.current_cycles >= max_cycles:
                break

            self.operand_values = []

            """Execute one CPU instruction cycle."""
            # Fetch the opcode
            opcode = self.fetch()
        
            # Look up the opcode in our database
            opcode_info = None

            # Check if it's a prefixed opcode (0xCB)
            if opcode == 0xCB:
                # Fetch the second byte for prefixed instructions
                opcode = self.fetch_byte(self.registers.PC)
                self.registers.PC = (self.registers.PC + 1) & 0xFFFF

                opcode_info = self.opcodes_db["cbprefixed"].get(f"0x{opcode:02X}")
            else:
                opcode_info = self.opcodes_db["unprefixed"].get(f"0x{opcode:02X}")
        
            # If we don't have the opcode implemented, raise an exception
            if opcode_info is None:
                raise NotImplementedError(f'Opcode {opcode:#04x} not implemented')

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
                        raise ValueError("Not implemented yet to fetch more than 2 bytes.")
                    
                    self.registers.PC = (self.registers.PC + operand["bytes"]) & 0xFFFF
                    
                    # Determine operand type
                    if operand_name == "a16":
                        operand_type = "immediate_address"
                    else:
                        # n8, n16, e8, r8
                        operand_type = "immediate_value"
                    
                    self.operand_values.append({
                        "name": operand_name,
                        "value": fetched_value,
                        "immediate": operand_immediate,
                        "type": operand_type
                    })
                else:
                    # Register operand (no bytes to fetch)
                    if operand_immediate:
                        operand_type = "register"
                    else:
                        operand_type = "register_indirect"
                    
                    self.operand_values.append({
                        "name": operand_name,
                        "value": operand_name,
                        "immediate": operand_immediate,
                        "type": operand_type
                    })

            # Dispatch to the handler and accumulate cycles
            handler = self.opcode_handlers.get(opcode)
            if handler is None:
                raise NotImplementedError(f'Handler for opcode {opcode:#04x} not implemented')
            
            cycles_used = handler(self, opcode_info)
            self.current_cycles += cycles_used 
