"""Run a Blargg test ROM and print serial output.

Usage:
    python run_blargg.py rom/blargg/instr_timing.gb
    python run_blargg.py rom/blargg/cpu_instrs.gb
    python run_blargg.py rom/blargg/instr_timing.gb --max-cycles 50000000
"""

import argparse
import sys
import time

from src.gameboy import GameBoy

DEFAULT_MAX_CYCLES = 30_000_000  # 30M T-cycles (~7 seconds of Game Boy time)


def run_blargg(rom_path, max_cycles):
    gb = GameBoy()
    cart = gb.load_cartridge(rom_path)

    print(f"ROM:    {cart.title}")
    print(f"Type:   {cart.cartridge_type_name}")
    print(f"Size:   {cart.rom_size // 1024} KB")
    print(f"Budget: {max_cycles:,} T-cycles")
    print("-" * 40)

    gb.cpu.registers.PC = 0x0100  # Skip boot ROM, start at cartridge entry point

    start = time.time()
    cycles_run = gb.run(max_cycles=max_cycles)
    elapsed = time.time() - start

    output = gb.get_serial_output()

    print(f"\n--- Serial Output ---")
    if output:
        print(output)
    else:
        print("(no output)")

    print(f"--- Stats ---")
    print(f"Cycles:  {gb.cpu.current_cycles:,}")
    print(f"Time:    {elapsed:.2f}s")
    if elapsed > 0:
        mhz = gb.cpu.current_cycles / elapsed / 1_000_000
        print(f"Speed:   {mhz:.2f} MHz (Game Boy is 4.19 MHz)")

    # Check for pass/fail in output
    if "Passed" in output:
        print("\nRESULT: PASSED")
        return 0
    elif "Failed" in output:
        print("\nRESULT: FAILED")
        return 1
    else:
        print("\nRESULT: INCONCLUSIVE (test may need more cycles)")
        return 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a Blargg test ROM")
    parser.add_argument("rom", help="Path to the .gb ROM file")
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=DEFAULT_MAX_CYCLES,
        help=f"Maximum T-cycles to run (default: {DEFAULT_MAX_CYCLES:,})",
    )
    args = parser.parse_args()

    sys.exit(run_blargg(args.rom, args.max_cycles))
