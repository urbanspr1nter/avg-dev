import unittest
from src.cpu.gb_cpu import CPU
from src.memory.gb_memory import Memory


class CBTestBase(unittest.TestCase):
    """Base class for CB-prefixed opcode tests."""

    def setUp(self):
        self.memory = Memory()
        self.cpu = CPU(self.memory)

    def _run_cb(self, cb_opcode, max_cycles=8):
        """Helper to set up and execute a CB-prefixed instruction."""
        self.memory.set_value(0x0000, 0xCB)
        self.memory.set_value(0x0001, cb_opcode)
        self.cpu.registers.PC = 0x0000
        self.cpu.run(max_cycles=max_cycles)


class TestCBRLC(CBTestBase):
    """RLC - Rotate Left Circular (CB 0x00-0x07)"""

    def test_rlc_b(self):
        """RLC B: 0x85 -> 0x0B, C=1"""
        self.cpu.set_register('B', 0x85)
        self._run_cb(0x00)
        self.assertEqual(self.cpu.get_register('B'), 0x0B)
        self.assertFalse(self.cpu.get_flag('Z'))
        self.assertTrue(self.cpu.get_flag('C'))
        self.assertEqual(self.cpu.current_cycles, 8)
        self.assertEqual(self.cpu.registers.PC, 0x0002)

    def test_rlc_a(self):
        """RLC A: 0x01 -> 0x02, C=0"""
        self.cpu.set_register('A', 0x01)
        self._run_cb(0x07)
        self.assertEqual(self.cpu.get_register('A'), 0x02)
        self.assertFalse(self.cpu.get_flag('C'))

    def test_rlc_zero(self):
        """RLC B: 0x00 -> 0x00, Z=1, C=0"""
        self.cpu.set_register('B', 0x00)
        self._run_cb(0x00)
        self.assertEqual(self.cpu.get_register('B'), 0x00)
        self.assertTrue(self.cpu.get_flag('Z'))
        self.assertFalse(self.cpu.get_flag('C'))

    def test_rlc_hl_indirect(self):
        """RLC (HL): memory at HL rotated, 16 cycles"""
        self.cpu.set_register('HL', 0xC000)
        self.memory.set_value(0xC000, 0x80)
        self._run_cb(0x06, max_cycles=16)
        self.assertEqual(self.memory.get_value(0xC000), 0x01)
        self.assertTrue(self.cpu.get_flag('C'))
        self.assertEqual(self.cpu.current_cycles, 16)


class TestCBRRC(CBTestBase):
    """RRC - Rotate Right Circular (CB 0x08-0x0F)"""

    def test_rrc_c(self):
        """RRC C: 0x01 -> 0x80, C=1"""
        self.cpu.set_register('C', 0x01)
        self._run_cb(0x09)
        self.assertEqual(self.cpu.get_register('C'), 0x80)
        self.assertTrue(self.cpu.get_flag('C'))

    def test_rrc_a(self):
        """RRC A: 0x02 -> 0x01, C=0"""
        self.cpu.set_register('A', 0x02)
        self._run_cb(0x0F)
        self.assertEqual(self.cpu.get_register('A'), 0x01)
        self.assertFalse(self.cpu.get_flag('C'))

    def test_rrc_zero(self):
        """RRC D: 0x00 -> 0x00, Z=1"""
        self.cpu.set_register('D', 0x00)
        self._run_cb(0x0A)
        self.assertEqual(self.cpu.get_register('D'), 0x00)
        self.assertTrue(self.cpu.get_flag('Z'))

    def test_rrc_hl_indirect(self):
        """RRC (HL): 16 cycles"""
        self.cpu.set_register('HL', 0xC000)
        self.memory.set_value(0xC000, 0x03)
        self._run_cb(0x0E, max_cycles=16)
        self.assertEqual(self.memory.get_value(0xC000), 0x81)
        self.assertTrue(self.cpu.get_flag('C'))
        self.assertEqual(self.cpu.current_cycles, 16)


class TestCBRL(CBTestBase):
    """RL - Rotate Left through Carry (CB 0x10-0x17)"""

    def test_rl_d_carry_in(self):
        """RL D: 0x80 with C=1 -> 0x01, C=1"""
        self.cpu.set_register('D', 0x80)
        self.cpu.set_flag('C', True)
        self._run_cb(0x12)
        self.assertEqual(self.cpu.get_register('D'), 0x01)
        self.assertTrue(self.cpu.get_flag('C'))

    def test_rl_e_no_carry(self):
        """RL E: 0x40 with C=0 -> 0x80, C=0"""
        self.cpu.set_register('E', 0x40)
        self.cpu.set_flag('C', False)
        self._run_cb(0x13)
        self.assertEqual(self.cpu.get_register('E'), 0x80)
        self.assertFalse(self.cpu.get_flag('C'))

    def test_rl_zero_result(self):
        """RL B: 0x80 with C=0 -> 0x00, Z=1, C=1"""
        self.cpu.set_register('B', 0x80)
        self.cpu.set_flag('C', False)
        self._run_cb(0x10)
        self.assertEqual(self.cpu.get_register('B'), 0x00)
        self.assertTrue(self.cpu.get_flag('Z'))
        self.assertTrue(self.cpu.get_flag('C'))

    def test_rl_hl_indirect(self):
        """RL (HL): 16 cycles"""
        self.cpu.set_register('HL', 0xC000)
        self.memory.set_value(0xC000, 0x11)
        self.cpu.set_flag('C', False)
        self._run_cb(0x16, max_cycles=16)
        self.assertEqual(self.memory.get_value(0xC000), 0x22)
        self.assertEqual(self.cpu.current_cycles, 16)


class TestCBRR(CBTestBase):
    """RR - Rotate Right through Carry (CB 0x18-0x1F)"""

    def test_rr_h_carry_in(self):
        """RR H: 0x01 with C=1 -> 0x80, C=1"""
        self.cpu.set_register('H', 0x01)
        self.cpu.set_flag('C', True)
        self._run_cb(0x1C)
        self.assertEqual(self.cpu.get_register('H'), 0x80)
        self.assertTrue(self.cpu.get_flag('C'))

    def test_rr_l_no_carry(self):
        """RR L: 0x02 with C=0 -> 0x01, C=0"""
        self.cpu.set_register('L', 0x02)
        self.cpu.set_flag('C', False)
        self._run_cb(0x1D)
        self.assertEqual(self.cpu.get_register('L'), 0x01)
        self.assertFalse(self.cpu.get_flag('C'))

    def test_rr_zero_result(self):
        """RR A: 0x01 with C=0 -> 0x00, Z=1, C=1"""
        self.cpu.set_register('A', 0x01)
        self.cpu.set_flag('C', False)
        self._run_cb(0x1F)
        self.assertEqual(self.cpu.get_register('A'), 0x00)
        self.assertTrue(self.cpu.get_flag('Z'))
        self.assertTrue(self.cpu.get_flag('C'))

    def test_rr_hl_indirect(self):
        """RR (HL): 16 cycles"""
        self.cpu.set_register('HL', 0xC000)
        self.memory.set_value(0xC000, 0x44)
        self.cpu.set_flag('C', True)
        self._run_cb(0x1E, max_cycles=16)
        self.assertEqual(self.memory.get_value(0xC000), 0xA2)
        self.assertEqual(self.cpu.current_cycles, 16)


class TestCBSLA(CBTestBase):
    """SLA - Shift Left Arithmetic (CB 0x20-0x27)"""

    def test_sla_b(self):
        """SLA B: 0x42 -> 0x84, C=0"""
        self.cpu.set_register('B', 0x42)
        self._run_cb(0x20)
        self.assertEqual(self.cpu.get_register('B'), 0x84)
        self.assertFalse(self.cpu.get_flag('C'))

    def test_sla_carry_out(self):
        """SLA C: 0xFF -> 0xFE, C=1"""
        self.cpu.set_register('C', 0xFF)
        self._run_cb(0x21)
        self.assertEqual(self.cpu.get_register('C'), 0xFE)
        self.assertTrue(self.cpu.get_flag('C'))

    def test_sla_zero(self):
        """SLA A: 0x80 -> 0x00, Z=1, C=1"""
        self.cpu.set_register('A', 0x80)
        self._run_cb(0x27)
        self.assertEqual(self.cpu.get_register('A'), 0x00)
        self.assertTrue(self.cpu.get_flag('Z'))
        self.assertTrue(self.cpu.get_flag('C'))

    def test_sla_hl_indirect(self):
        """SLA (HL): 16 cycles"""
        self.cpu.set_register('HL', 0xC000)
        self.memory.set_value(0xC000, 0x21)
        self._run_cb(0x26, max_cycles=16)
        self.assertEqual(self.memory.get_value(0xC000), 0x42)
        self.assertEqual(self.cpu.current_cycles, 16)


class TestCBSRA(CBTestBase):
    """SRA - Shift Right Arithmetic (CB 0x28-0x2F)"""

    def test_sra_positive(self):
        """SRA D: 0x42 -> 0x21, C=0 (bit 7 stays 0)"""
        self.cpu.set_register('D', 0x42)
        self._run_cb(0x2A)
        self.assertEqual(self.cpu.get_register('D'), 0x21)
        self.assertFalse(self.cpu.get_flag('C'))

    def test_sra_negative_preserved(self):
        """SRA E: 0x80 -> 0xC0, C=0 (bit 7 preserved)"""
        self.cpu.set_register('E', 0x80)
        self._run_cb(0x2B)
        self.assertEqual(self.cpu.get_register('E'), 0xC0)
        self.assertFalse(self.cpu.get_flag('C'))

    def test_sra_carry_out(self):
        """SRA B: 0x01 -> 0x00, Z=1, C=1"""
        self.cpu.set_register('B', 0x01)
        self._run_cb(0x28)
        self.assertEqual(self.cpu.get_register('B'), 0x00)
        self.assertTrue(self.cpu.get_flag('Z'))
        self.assertTrue(self.cpu.get_flag('C'))

    def test_sra_ff(self):
        """SRA A: 0xFF -> 0xFF, C=1 (bit 7 preserved, bit 0 to carry)"""
        self.cpu.set_register('A', 0xFF)
        self._run_cb(0x2F)
        self.assertEqual(self.cpu.get_register('A'), 0xFF)
        self.assertFalse(self.cpu.get_flag('Z'))
        self.assertTrue(self.cpu.get_flag('C'))

    def test_sra_hl_indirect(self):
        """SRA (HL): 16 cycles"""
        self.cpu.set_register('HL', 0xC000)
        self.memory.set_value(0xC000, 0x8A)
        self._run_cb(0x2E, max_cycles=16)
        self.assertEqual(self.memory.get_value(0xC000), 0xC5)
        self.assertEqual(self.cpu.current_cycles, 16)


class TestCBSWAP(CBTestBase):
    """SWAP - Swap nibbles (CB 0x30-0x37)"""

    def test_swap_b(self):
        """SWAP B: 0xAB -> 0xBA"""
        self.cpu.set_register('B', 0xAB)
        self._run_cb(0x30)
        self.assertEqual(self.cpu.get_register('B'), 0xBA)
        self.assertFalse(self.cpu.get_flag('Z'))
        self.assertFalse(self.cpu.get_flag('C'))

    def test_swap_zero(self):
        """SWAP A: 0x00 -> 0x00, Z=1"""
        self.cpu.set_register('A', 0x00)
        self._run_cb(0x37)
        self.assertEqual(self.cpu.get_register('A'), 0x00)
        self.assertTrue(self.cpu.get_flag('Z'))
        self.assertFalse(self.cpu.get_flag('C'))

    def test_swap_f0(self):
        """SWAP C: 0xF0 -> 0x0F"""
        self.cpu.set_register('C', 0xF0)
        self._run_cb(0x31)
        self.assertEqual(self.cpu.get_register('C'), 0x0F)

    def test_swap_hl_indirect(self):
        """SWAP (HL): 16 cycles"""
        self.cpu.set_register('HL', 0xC000)
        self.memory.set_value(0xC000, 0x12)
        self._run_cb(0x36, max_cycles=16)
        self.assertEqual(self.memory.get_value(0xC000), 0x21)
        self.assertEqual(self.cpu.current_cycles, 16)


class TestCBSRL(CBTestBase):
    """SRL - Shift Right Logical (CB 0x38-0x3F)"""

    def test_srl_h(self):
        """SRL H: 0x42 -> 0x21, C=0"""
        self.cpu.set_register('H', 0x42)
        self._run_cb(0x3C)
        self.assertEqual(self.cpu.get_register('H'), 0x21)
        self.assertFalse(self.cpu.get_flag('C'))

    def test_srl_bit7_cleared(self):
        """SRL L: 0x80 -> 0x40, C=0 (bit 7 always cleared unlike SRA)"""
        self.cpu.set_register('L', 0x80)
        self._run_cb(0x3D)
        self.assertEqual(self.cpu.get_register('L'), 0x40)
        self.assertFalse(self.cpu.get_flag('C'))

    def test_srl_carry_and_zero(self):
        """SRL A: 0x01 -> 0x00, Z=1, C=1"""
        self.cpu.set_register('A', 0x01)
        self._run_cb(0x3F)
        self.assertEqual(self.cpu.get_register('A'), 0x00)
        self.assertTrue(self.cpu.get_flag('Z'))
        self.assertTrue(self.cpu.get_flag('C'))

    def test_srl_hl_indirect(self):
        """SRL (HL): 16 cycles"""
        self.cpu.set_register('HL', 0xC000)
        self.memory.set_value(0xC000, 0xFF)
        self._run_cb(0x3E, max_cycles=16)
        self.assertEqual(self.memory.get_value(0xC000), 0x7F)
        self.assertTrue(self.cpu.get_flag('C'))
        self.assertEqual(self.cpu.current_cycles, 16)


class TestCBBIT(CBTestBase):
    """BIT - Test bit (CB 0x40-0x7F)"""

    def test_bit_0_b_set(self):
        """BIT 0,B: bit 0 is set -> Z=0"""
        self.cpu.set_register('B', 0x01)
        self._run_cb(0x40)
        self.assertFalse(self.cpu.get_flag('Z'))
        self.assertTrue(self.cpu.get_flag('H'))
        self.assertFalse(self.cpu.get_flag('N'))

    def test_bit_0_b_clear(self):
        """BIT 0,B: bit 0 is clear -> Z=1"""
        self.cpu.set_register('B', 0xFE)
        self._run_cb(0x40)
        self.assertTrue(self.cpu.get_flag('Z'))

    def test_bit_7_a(self):
        """BIT 7,A: test highest bit"""
        self.cpu.set_register('A', 0x80)
        self._run_cb(0x7F)
        self.assertFalse(self.cpu.get_flag('Z'))

    def test_bit_7_a_clear(self):
        """BIT 7,A: bit 7 clear -> Z=1"""
        self.cpu.set_register('A', 0x7F)
        self._run_cb(0x7F)
        self.assertTrue(self.cpu.get_flag('Z'))

    def test_bit_3_d(self):
        """BIT 3,D: test middle bit"""
        self.cpu.set_register('D', 0x08)
        self._run_cb(0x5A)
        self.assertFalse(self.cpu.get_flag('Z'))

    def test_bit_preserves_carry(self):
        """BIT does not change carry flag"""
        self.cpu.set_register('B', 0x00)
        self.cpu.set_flag('C', True)
        self._run_cb(0x40)
        self.assertTrue(self.cpu.get_flag('C'))

    def test_bit_hl_indirect(self):
        """BIT 4,(HL): 12 cycles"""
        self.cpu.set_register('HL', 0xC000)
        self.memory.set_value(0xC000, 0x10)
        self._run_cb(0x66, max_cycles=12)
        self.assertFalse(self.cpu.get_flag('Z'))
        self.assertEqual(self.cpu.current_cycles, 12)

    def test_bit_hl_indirect_clear(self):
        """BIT 4,(HL): bit clear -> Z=1, 12 cycles"""
        self.cpu.set_register('HL', 0xC000)
        self.memory.set_value(0xC000, 0x00)
        self._run_cb(0x66, max_cycles=12)
        self.assertTrue(self.cpu.get_flag('Z'))
        self.assertEqual(self.cpu.current_cycles, 12)

    def test_bit_all_bits_on_register(self):
        """Test all 8 bit positions on register E with value 0xA5 (10100101)"""
        # Bits set: 0, 2, 5, 7
        expected_z = [False, True, False, True, True, False, True, False]
        for bit in range(8):
            self.setUp()
            self.cpu.set_register('E', 0xA5)
            # BIT n, E opcodes: 0x43 + n*8 (E is target index 3)
            self._run_cb(0x43 + bit * 8)
            self.assertEqual(
                self.cpu.get_flag('Z'), expected_z[bit],
                f"BIT {bit},E failed for value 0xA5"
            )


class TestCBRES(CBTestBase):
    """RES - Reset bit (CB 0x80-0xBF)"""

    def test_res_0_b(self):
        """RES 0,B: clear bit 0"""
        self.cpu.set_register('B', 0xFF)
        self._run_cb(0x80)
        self.assertEqual(self.cpu.get_register('B'), 0xFE)

    def test_res_7_a(self):
        """RES 7,A: clear bit 7"""
        self.cpu.set_register('A', 0xFF)
        self._run_cb(0xBF)
        self.assertEqual(self.cpu.get_register('A'), 0x7F)

    def test_res_already_clear(self):
        """RES on already-clear bit: no change"""
        self.cpu.set_register('C', 0x00)
        self._run_cb(0x81)
        self.assertEqual(self.cpu.get_register('C'), 0x00)

    def test_res_no_flag_change(self):
        """RES does not affect any flags"""
        self.cpu.set_register('D', 0xFF)
        self.cpu.set_flag('Z', True)
        self.cpu.set_flag('C', True)
        self.cpu.set_flag('H', True)
        self.cpu.set_flag('N', True)
        self._run_cb(0x82)
        self.assertTrue(self.cpu.get_flag('Z'))
        self.assertTrue(self.cpu.get_flag('C'))
        self.assertTrue(self.cpu.get_flag('H'))
        self.assertTrue(self.cpu.get_flag('N'))

    def test_res_hl_indirect(self):
        """RES 5,(HL): 16 cycles"""
        self.cpu.set_register('HL', 0xC000)
        self.memory.set_value(0xC000, 0xFF)
        self._run_cb(0xAE, max_cycles=16)
        self.assertEqual(self.memory.get_value(0xC000), 0xDF)
        self.assertEqual(self.cpu.current_cycles, 16)

    def test_res_all_bits(self):
        """RES each bit 0-7 on register H starting from 0xFF"""
        for bit in range(8):
            self.setUp()
            self.cpu.set_register('H', 0xFF)
            # RES n, H: 0x84 + n*8 (H is target index 4)
            self._run_cb(0x84 + bit * 8)
            expected = 0xFF & ~(1 << bit)
            self.assertEqual(
                self.cpu.get_register('H'), expected,
                f"RES {bit},H failed"
            )


class TestCBSET(CBTestBase):
    """SET - Set bit (CB 0xC0-0xFF)"""

    def test_set_0_b(self):
        """SET 0,B: set bit 0"""
        self.cpu.set_register('B', 0x00)
        self._run_cb(0xC0)
        self.assertEqual(self.cpu.get_register('B'), 0x01)

    def test_set_7_a(self):
        """SET 7,A: set bit 7"""
        self.cpu.set_register('A', 0x00)
        self._run_cb(0xFF)
        self.assertEqual(self.cpu.get_register('A'), 0x80)

    def test_set_already_set(self):
        """SET on already-set bit: no change"""
        self.cpu.set_register('L', 0xFF)
        self._run_cb(0xFD)
        self.assertEqual(self.cpu.get_register('L'), 0xFF)

    def test_set_no_flag_change(self):
        """SET does not affect any flags"""
        self.cpu.set_register('E', 0x00)
        self.cpu.set_flag('Z', False)
        self.cpu.set_flag('C', False)
        self._run_cb(0xC3)
        self.assertFalse(self.cpu.get_flag('Z'))
        self.assertFalse(self.cpu.get_flag('C'))

    def test_set_hl_indirect(self):
        """SET 3,(HL): 16 cycles"""
        self.cpu.set_register('HL', 0xC000)
        self.memory.set_value(0xC000, 0x00)
        self._run_cb(0xDE, max_cycles=16)
        self.assertEqual(self.memory.get_value(0xC000), 0x08)
        self.assertEqual(self.cpu.current_cycles, 16)

    def test_set_all_bits(self):
        """SET each bit 0-7 on register L starting from 0x00"""
        for bit in range(8):
            self.setUp()
            self.cpu.set_register('L', 0x00)
            # SET n, L: 0xC5 + n*8 (L is target index 5)
            self._run_cb(0xC5 + bit * 8)
            expected = 1 << bit
            self.assertEqual(
                self.cpu.get_register('L'), expected,
                f"SET {bit},L failed"
            )


class TestCBAllTargets(CBTestBase):
    """Verify all 8 targets work for a representative operation (RLC)."""

    def test_rlc_all_registers(self):
        """RLC on each register target: B(0x00), C(0x01), D(0x02), E(0x03), H(0x04), L(0x05), A(0x07)"""
        targets = [
            (0x00, 'B'), (0x01, 'C'), (0x02, 'D'), (0x03, 'E'),
            (0x04, 'H'), (0x05, 'L'), (0x07, 'A'),
        ]
        for cb_opcode, reg in targets:
            self.setUp()
            self.cpu.set_register(reg, 0x81)
            self._run_cb(cb_opcode)
            self.assertEqual(
                self.cpu.get_register(reg), 0x03,
                f"RLC {reg} (CB {cb_opcode:#04x}) failed: 0x81 should become 0x03"
            )
            self.assertTrue(self.cpu.get_flag('C'), f"RLC {reg} should set carry")


class TestCBFlagBehavior(CBTestBase):
    """Verify N and H flags are always cleared for rotate/shift/swap."""

    def test_rotate_clears_n_h(self):
        """All rotate/shift/swap ops clear N and H flags"""
        ops = [0x00, 0x08, 0x10, 0x18, 0x20, 0x28, 0x30, 0x38]  # One per type, target B
        for cb_opcode in ops:
            self.setUp()
            self.cpu.set_register('B', 0x42)
            self.cpu.set_flag('N', True)
            self.cpu.set_flag('H', True)
            self._run_cb(cb_opcode)
            self.assertFalse(
                self.cpu.get_flag('N'),
                f"CB {cb_opcode:#04x} should clear N flag"
            )
            self.assertFalse(
                self.cpu.get_flag('H'),
                f"CB {cb_opcode:#04x} should clear H flag"
            )


if __name__ == "__main__":
    unittest.main()
