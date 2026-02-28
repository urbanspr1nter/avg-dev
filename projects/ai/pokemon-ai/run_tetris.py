"""Run Tetris ROM and render the ASCII framebuffer.

Usage:
    python run_tetris.py
    python run_tetris.py --max-cycles 20000000
"""

import argparse
import time

from src.gameboy import GameBoy

DEFAULT_MAX_CYCLES = 12_000_000  # ~3 seconds of Game Boy time (reaches title screen)


def run_tetris(max_cycles):
    gb = GameBoy()
    cart = gb.load_cartridge("rom/Tetris.gb")

    print(f"ROM:    {cart.title}")
    print(f"Type:   {cart.cartridge_type_name}")
    print(f"Size:   {cart.rom_size // 1024} KB")
    print(f"Budget: {max_cycles:,} T-cycles")
    print("-" * 40)

    # Set post-boot DMG register state (skip boot ROM)
    gb.init_post_boot_state()

    start = time.time()
    gb.run(max_cycles=max_cycles)
    elapsed = time.time() - start

    print(f"Cycles: {gb.cpu.current_cycles:,}")
    print(f"Time:   {elapsed:.2f}s")
    if elapsed > 0:
        mhz = gb.cpu.current_cycles / elapsed / 1_000_000
        print(f"Speed:  {mhz:.2f} MHz (Game Boy is 4.19 MHz)")
    print(f"LCDC:   0x{gb.ppu._lcdc:02X}")
    print(f"BGP:    0x{gb.ppu._bgp:02X}")

    fb = gb.ppu.get_framebuffer()
    nonzero = sum(1 for row in fb for px in row if px > 0)
    print(f"Pixels: {nonzero} non-zero / {160 * 144} total")

    print(f"\n{'=' * 40}")
    print("ASCII Framebuffer:")
    print("=" * 40)
    print(gb.ppu.render_ascii())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Tetris and render framebuffer")
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=DEFAULT_MAX_CYCLES,
        help=f"Maximum T-cycles to run (default: {DEFAULT_MAX_CYCLES:,})",
    )
    args = parser.parse_args()
    run_tetris(args.max_cycles)
