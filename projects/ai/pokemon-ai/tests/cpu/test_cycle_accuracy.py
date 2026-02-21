"""
Cycle accuracy tests: verifies every opcode's cycle count against Opcodes.json.

This test suite programmatically checks that each opcode handler returns
the correct number of cycles as specified in the authoritative Opcodes.json
reference. For conditional instructions, both taken and not-taken paths
are verified.

Total coverage: ~500 cycle checks across all unprefixed and CB-prefixed opcodes.
"""

import json
import unittest
from src.cpu.gb_cpu import CPU
from src.memory.gb_memory import Memory


# Opcodes to skip in cycle testing
SKIP_OPCODES = {
    0xCB,  # PREFIX byte, not an instruction — handled by run loop
}

# Conditional opcodes: {opcode: (flag_name, flag_value_for_taken)}
CONDITIONAL_OPCODES = {
    # JR cc
    0x20: ("Z", False),   # JR NZ
    0x28: ("Z", True),    # JR Z
    0x30: ("C", False),   # JR NC
    0x38: ("C", True),    # JR C
    # JP cc
    0xC2: ("Z", False),   # JP NZ
    0xCA: ("Z", True),    # JP Z
    0xD2: ("C", False),   # JP NC
    0xDA: ("C", True),    # JP C
    # RET cc
    0xC0: ("Z", False),   # RET NZ
    0xC8: ("Z", True),    # RET Z
    0xD0: ("C", False),   # RET NC
    0xD8: ("C", True),    # RET C
    # CALL cc
    0xC4: ("Z", False),   # CALL NZ
    0xCC: ("Z", True),    # CALL Z
    0xD4: ("C", False),   # CALL NC
    0xDC: ("C", True),    # CALL C
}

# Opcodes that pop a return address from the stack
RET_OPCODES = {0xC9, 0xD9, 0xC0, 0xC8, 0xD0, 0xD8}


class TestUnprefixedCycleAccuracy(unittest.TestCase):
    """Verify cycle counts for all unprefixed opcodes against Opcodes.json."""

    @classmethod
    def setUpClass(cls):
        with open("Opcodes.json") as f:
            cls.opcodes_db = json.load(f)

    def _make_cpu(self):
        """Create a fresh CPU with safe register defaults."""
        memory = Memory()
        cpu = CPU(memory)
        cpu.registers.SP = 0xFFFE
        cpu.set_register("HL", 0xC000)
        cpu.set_register("BC", 0xC002)
        cpu.set_register("DE", 0xC004)
        return cpu

    def _setup_opcode(self, cpu, opcode, opcode_info):
        """Place opcode and dummy operand bytes in memory at PC=0."""
        cpu.registers.PC = 0x0000
        cpu.memory.set_value(0x0000, opcode)
        # Fill operand bytes with 0x01 (safe dummy value)
        num_bytes = opcode_info["bytes"]
        for i in range(1, num_bytes):
            cpu.memory.set_value(i, 0x01)

    def _push_return_address(self, cpu):
        """Push a dummy return address for RET-family instructions."""
        cpu.push_word(0x1000)

    def test_non_conditional_cycles(self):
        """Every non-conditional unprefixed opcode returns correct cycle count."""
        tested = 0
        # Get the set of implemented opcodes from a fresh CPU
        implemented = set(self._make_cpu().opcode_handlers.keys())

        for hex_key, info in self.opcodes_db["unprefixed"].items():
            opcode = int(hex_key, 16)
            if opcode in SKIP_OPCODES or opcode in CONDITIONAL_OPCODES:
                continue
            if opcode not in implemented:
                continue

            with self.subTest(opcode=f"0x{opcode:02X}", mnemonic=info["mnemonic"]):
                cpu = self._make_cpu()
                self._setup_opcode(cpu, opcode, info)

                if opcode in RET_OPCODES:
                    self._push_return_address(cpu)

                expected = info["cycles"][0]
                cpu.run(max_cycles=expected)
                self.assertEqual(
                    cpu.current_cycles, expected,
                    f"0x{opcode:02X} ({info['mnemonic']}): "
                    f"expected {expected} cycles, got {cpu.current_cycles}"
                )
                tested += 1

        # Sanity check: we should test a large number of opcodes
        self.assertGreater(tested, 200, f"Only {tested} non-conditional opcodes tested")

    def test_conditional_taken_cycles(self):
        """Conditional instructions return cycles[0] when condition is met."""
        tested = 0
        for opcode, (flag, taken_value) in CONDITIONAL_OPCODES.items():
            hex_key = f"0x{opcode:02X}"
            info = self.opcodes_db["unprefixed"][hex_key]

            with self.subTest(opcode=hex_key, mnemonic=info["mnemonic"], path="taken"):
                cpu = self._make_cpu()
                self._setup_opcode(cpu, opcode, info)
                cpu.set_flag(flag, taken_value)

                if opcode in RET_OPCODES:
                    self._push_return_address(cpu)

                expected = info["cycles"][0]
                cpu.run(max_cycles=expected)
                self.assertEqual(
                    cpu.current_cycles, expected,
                    f"{hex_key} ({info['mnemonic']}) taken: "
                    f"expected {expected}, got {cpu.current_cycles}"
                )
                tested += 1

        self.assertEqual(tested, 16, f"Expected 16 conditional taken tests, got {tested}")

    def test_conditional_not_taken_cycles(self):
        """Conditional instructions return cycles[1] when condition is not met."""
        tested = 0
        for opcode, (flag, taken_value) in CONDITIONAL_OPCODES.items():
            hex_key = f"0x{opcode:02X}"
            info = self.opcodes_db["unprefixed"][hex_key]

            with self.subTest(opcode=hex_key, mnemonic=info["mnemonic"], path="not_taken"):
                cpu = self._make_cpu()
                self._setup_opcode(cpu, opcode, info)
                cpu.set_flag(flag, not taken_value)

                expected = info["cycles"][1]
                cpu.run(max_cycles=expected)
                self.assertEqual(
                    cpu.current_cycles, expected,
                    f"{hex_key} ({info['mnemonic']}) not taken: "
                    f"expected {expected}, got {cpu.current_cycles}"
                )
                tested += 1

        self.assertEqual(tested, 16, f"Expected 16 conditional not-taken tests, got {tested}")


class TestCBPrefixedCycleAccuracy(unittest.TestCase):
    """Verify cycle counts for all 256 CB-prefixed opcodes against Opcodes.json."""

    @classmethod
    def setUpClass(cls):
        with open("Opcodes.json") as f:
            cls.opcodes_db = json.load(f)

    def test_all_cb_cycles(self):
        """Every CB-prefixed opcode returns correct cycle count."""
        tested = 0
        for hex_key, info in self.opcodes_db["cbprefixed"].items():
            cb_opcode = int(hex_key, 16)

            with self.subTest(opcode=f"CB 0x{cb_opcode:02X}", mnemonic=info["mnemonic"]):
                memory = Memory()
                cpu = CPU(memory)
                cpu.registers.SP = 0xFFFE
                cpu.set_register("HL", 0xC000)
                cpu.registers.PC = 0x0000

                memory.set_value(0x0000, 0xCB)
                memory.set_value(0x0001, cb_opcode)

                expected = info["cycles"][0]
                cpu.run(max_cycles=expected)
                self.assertEqual(
                    cpu.current_cycles, expected,
                    f"CB 0x{cb_opcode:02X} ({info['mnemonic']}): "
                    f"expected {expected}, got {cpu.current_cycles}"
                )
                tested += 1

        self.assertEqual(tested, 256, f"Expected 256 CB opcodes tested, got {tested}")


if __name__ == "__main__":
    unittest.main()
