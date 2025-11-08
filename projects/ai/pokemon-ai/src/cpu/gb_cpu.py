class Registers:
    AF: int = 0
    BC: int = 0
    DE: int = 0
    HL: int = 0
    SP: int = 0
    PC: int = 0

class CPU:
    def __init__(self, memory=None):
        self.registers = Registers()
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
