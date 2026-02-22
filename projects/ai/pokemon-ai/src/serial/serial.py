class Serial:
    """Game Boy serial port handler (0xFF01-0xFF02).

    The Game Boy serial port has two registers:
      - SB (0xFF01): Serial transfer data — the byte to send/receive
      - SC (0xFF02): Serial control — bit 7 = transfer start, bit 0 = clock select

    Blargg's test ROMs use serial as a debug output channel: write a character
    to SB, then write 0x81 to SC (start transfer with internal clock). We
    capture each transmitted byte into an output buffer for reading test results.
    """

    def __init__(self):
        self._sb = 0x00           # Serial transfer data (0xFF01)
        self._sc = 0x00           # Serial control (0xFF02)
        self._output_buffer = []  # Captured output bytes

    def read(self, address):
        """Read a serial register."""
        if address == 0xFF01:
            return self._sb
        if address == 0xFF02:
            return self._sc
        return 0xFF

    def write(self, address, value):
        """Write a serial register.

        When SC is written with bit 7 (transfer start) and bit 0 (internal
        clock) both set, the byte in SB is captured as output and bit 7 of
        SC is cleared to signal transfer complete.
        """
        value = value & 0xFF
        if address == 0xFF01:
            self._sb = value
        elif address == 0xFF02:
            self._sc = value
            if value & 0x81 == 0x81:
                self._output_buffer.append(self._sb)
                self._sc &= 0x7F  # Clear bit 7 (transfer complete)

    def get_output(self):
        """Return captured serial output as an ASCII string."""
        return "".join(chr(b) for b in self._output_buffer)

    def get_output_bytes(self):
        """Return captured serial output as a list of raw bytes."""
        return list(self._output_buffer)
