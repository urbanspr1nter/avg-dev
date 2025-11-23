class Registers:
    AF: int = 0
    BC: int = 0
    DE: int = 0
    HL: int = 0
    SP: int = 0
    PC: int = 0


import json

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
        self.registers.PC += 1
        return opcode

    def run(self, max_cycles=-1):

        while True:
            if self.current_cycles == max_cycles:
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
                self.registers.PC += 1

                opcode_info = self.opcodes_db["cbprefixed"].get(f"0x{opcode:02X}")
            else:
                opcode_info = self.opcodes_db["unprefixed"].get(f"0x{opcode:02X}")
        
            # If we don't have the opcode implemented, raise an exception
            if opcode_info is None:
                raise NotImplementedError(f'Opcode {opcode:#04x} not implemented')

            # just increment PC as appropriate per operand.
            operands = opcode_info["operands"]
            for operand in operands:
                if "bytes" in operand:
                    num_bytes_for_operand = operand["bytes"]
                    if num_bytes_for_operand == 1:
                        self.operand_values.append(self.fetch_byte(self.registers.PC))
                    elif num_bytes_for_operand == 2:
                        self.operand_values.append(self.fetch_word(self.registers.PC))
                    else:
                        raise ValueError("Not implemented yet to fetch more than 2 bytes.")
                    
                    self.registers.PC += operand["bytes"]


            # assume the first number of cycles for now.
            self.current_cycles += opcode_info["cycles"][0] 
