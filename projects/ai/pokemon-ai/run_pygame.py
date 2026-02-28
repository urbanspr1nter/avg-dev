"""Run a Game Boy ROM with the pygame frontend.

Usage:
    python run_pygame.py rom/Tetris.gb
    python run_pygame.py rom/Tetris.gb --scale 4
"""

import argparse

from src.gameboy import GameBoy
from src.frontend.pygame_frontend import PygameFrontend


def main():
    parser = argparse.ArgumentParser(description="Run a Game Boy ROM with pygame")
    parser.add_argument("rom", help="Path to the .gb ROM file")
    parser.add_argument(
        "--scale",
        type=int,
        default=3,
        help="Window scale factor (default: 3 = 480x432)",
    )
    args = parser.parse_args()

    gb = GameBoy()
    cart = gb.load_cartridge(args.rom)
    print(f"ROM:   {cart.title}")
    print(f"Type:  {cart.cartridge_type_name}")
    print(f"Size:  {cart.rom_size // 1024} KB")

    if cart.load_battery():
        print(f"Save:  loaded from {cart.sav_path}")

    gb.init_post_boot_state()

    frontend = PygameFrontend(gb, scale=args.scale)
    try:
        frontend.run()
    finally:
        if cart.save_battery():
            print(f"Save:  written to {cart.sav_path}")


if __name__ == "__main__":
    main()
