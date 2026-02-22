from src.memory.gb_memory import Memory
from src.cpu.gb_cpu import CPU
from src.timer.gb_timer import Timer
from src.serial.serial import Serial
from src.cartridge.gb_cartridge import Cartridge


class GameBoy:
    """Top-level Game Boy system that owns and wires all hardware components.

    This class exists to centralize the initialization order of the emulator's
    subsystems. Without it, callers must know the exact sequence of constructor
    calls and load_*() methods — a fragile setup that silently breaks if the
    order changes.

    Initialization order and why it matters:
    ─────────────────────────────────────────
    1. Memory FIRST — it is the shared bus that every other component references.
       Everything reads/writes through Memory, so it must exist before anything
       else can be wired to it.

    2. CPU SECOND — the CPU constructor sets memory._cpu = self, which Memory
       needs for interrupt register dispatch (IF at 0xFF0F, IE at 0xFFFF).
       If CPU is created before Memory, there's nothing to wire to.

    3. Timer THIRD (via memory.load_timer) — this does three things:
         a) Stores the timer in memory._timer for I/O register dispatch (0xFF04-0xFF07)
         b) Sets timer._memory = memory so the timer can set IF bit 2 on overflow
         c) Sets cpu._timer = timer so the CPU run loop can tick the timer
       Step (c) requires CPU to already exist (step 2), and step (b) requires
       Memory to already exist (step 1). If load_timer() is called before the
       CPU is created, the CPU never gets its _timer reference and timer ticks
       silently stop working.

    4. Serial FOURTH (via memory.load_serial) — stores the serial handler in
       memory._serial for I/O dispatch (0xFF01-0xFF02). Serial has no
       cross-references to other components, so it could technically be loaded
       at any point after Memory, but we keep it here for consistency.

    5. Cartridge LAST (via load_cartridge) — optional, loaded at runtime when a
       ROM file is provided. On real hardware, the cartridge is inserted before
       power-on, but in our emulator it can be loaded at any time since it only
       affects Memory's read/write dispatch for the ROM range (0x0000-0x7FFF).
    """

    def __init__(self):
        # Step 1: Memory is the shared bus — must be created first.
        self.memory = Memory()

        # Step 2: CPU — constructor wires memory._cpu = self for interrupt dispatch.
        self.cpu = CPU(memory=self.memory)

        # Step 3: Timer — load_timer() wires the bidirectional references:
        #   memory._timer (I/O dispatch), timer._memory (IF writes), cpu._timer (tick calls)
        self.timer = Timer()
        self.memory.load_timer(self.timer)

        # Step 4: Serial — load_serial() wires memory._serial (I/O dispatch).
        self.serial = Serial()
        self.memory.load_serial(self.serial)

        # Cartridge is not loaded here — call load_cartridge() with a ROM path.
        self.cartridge = None

    def load_cartridge(self, rom_path):
        """Load a ROM file into the system.

        Parses the cartridge header and wires ROM data into the memory bus.
        Returns the Cartridge instance for inspection (header info, etc.).
        """
        self.cartridge = Cartridge(rom_path)
        self.memory.load_cartridge(self.cartridge)
        return self.cartridge

    def run(self, max_cycles=-1):
        """Run the CPU for the given number of T-cycles (-1 = unlimited)."""
        return self.cpu.run(max_cycles=max_cycles)

    def get_serial_output(self):
        """Return any serial output captured so far (ASCII string)."""
        return self.serial.get_output()
