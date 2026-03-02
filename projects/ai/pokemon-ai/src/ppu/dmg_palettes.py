"""GBC boot ROM color palettes for original Game Boy games.

When a Game Boy Color runs a DMG (original Game Boy) cartridge, the boot ROM
selects a color palette based on the ROM header checksum (byte 0x014D) and
optionally the 4th character of the game title (byte 0x0137) for disambiguation.

Each palette set contains 3 palettes of 4 RGB colors each:
  - BG:   background and window pixels
  - OBJ0: sprites using OBP0
  - OBJ1: sprites using OBP1

The shade value (0-3) from the DMG palette registers (BGP/OBP0/OBP1) indexes
into these color palettes to produce the final RGB output.
"""

# Named palette definitions: shade 0 (lightest) → shade 3 (darkest)
_GRAYSCALE = ((255, 255, 255), (170, 170, 170), (85, 85, 85), (0, 0, 0))
_RED = ((255, 255, 255), (255, 132, 132), (148, 58, 58), (0, 0, 0))
_GREEN = ((255, 255, 255), (123, 255, 49), (0, 132, 0), (0, 0, 0))
_BLUE = ((255, 255, 255), (132, 132, 255), (66, 66, 148), (0, 0, 0))
_DARK_GREEN = ((255, 255, 255), (99, 255, 132), (0, 132, 66), (0, 0, 0))
_BROWN = ((255, 255, 255), (255, 173, 99), (132, 66, 66), (0, 0, 0))
_DARK_BLUE = ((255, 255, 255), (99, 132, 255), (66, 66, 148), (0, 0, 0))
_PASTEL = ((255, 255, 255), (255, 255, 132), (132, 132, 99), (0, 0, 0))
_ORANGE = ((255, 255, 255), (255, 173, 0), (132, 66, 0), (0, 0, 0))
_YELLOW = ((255, 255, 255), (255, 255, 0), (255, 0, 0), (0, 0, 0))
_DARK_BROWN = ((255, 255, 255), (173, 132, 66), (99, 66, 0), (0, 0, 0))
_INVERTED = ((0, 0, 0), (85, 85, 85), (170, 170, 170), (255, 255, 255))

# Palette combinations: (BG, OBJ0, OBJ1)
_PALETTE_SETS = {
    'RED':          (_RED, _RED, _GREEN),
    'BLUE':         (_BLUE, _BLUE, _RED),
    'GREEN':        (_GREEN, _GREEN, _RED),
    'BROWN':        (_BROWN, _BROWN, _GREEN),
    'DARK_GREEN':   (_DARK_GREEN, _DARK_GREEN, _RED),
    'DARK_BLUE':    (_DARK_BLUE, _DARK_BLUE, _GREEN),
    'PASTEL':       (_PASTEL, _PASTEL, _RED),
    'ORANGE':       (_ORANGE, _ORANGE, _GREEN),
    'YELLOW':       (_YELLOW, _YELLOW, _GREEN),
    'DARK_BROWN':   (_DARK_BROWN, _DARK_BROWN, _RED),
    'INVERTED':     (_INVERTED, _INVERTED, _INVERTED),
    'GRAYSCALE':    (_GRAYSCALE, _GRAYSCALE, _GRAYSCALE),
}

# GBC boot ROM: header checksum → palette set name
# Based on the GBC boot ROM palette lookup table.
# Some checksums map to different palettes depending on the 4th title character.
_CHECKSUM_TABLE = {
    0x01: 'BROWN',
    0x0D: 'BROWN',
    0x10: 'RED',
    0x14: 'BROWN',
    0x15: 'GREEN',
    0x17: 'BROWN',
    0x19: 'DARK_GREEN',
    0x1D: 'DARK_BLUE',
    0x27: 'PASTEL',
    0x28: 'ORANGE',
    0x29: 'RED',
    0x34: 'BROWN',
    0x36: 'BROWN',
    0x39: 'DARK_BLUE',
    0x43: 'BROWN',
    0x46: 'YELLOW',
    0x49: 'BROWN',
    0x4B: 'BROWN',
    0x52: 'BROWN',
    0x58: 'RED',
    0x59: 'BLUE',       # Disambiguation needed: Pokemon Red vs Blue
    0x5C: 'BROWN',
    0x5D: 'DARK_GREEN',
    0x61: 'BROWN',
    0x66: 'DARK_GREEN',
    0x67: 'DARK_GREEN',
    0x68: 'BROWN',
    0x69: 'GREEN',
    0x6B: 'BROWN',
    0x6D: 'ORANGE',
    0x71: 'BROWN',
    0x73: 'BROWN',
    0x75: 'BROWN',
    0x86: 'GREEN',
    0x88: 'DARK_BLUE',
    0x8B: 'BROWN',
    0x90: 'BROWN',
    0x92: 'DARK_GREEN',
    0x95: 'DARK_GREEN',
    0x97: 'RED',
    0x99: 'DARK_BLUE',
    0x9A: 'BROWN',
    0x9C: 'BROWN',
    0x9D: 'BLUE',
    0xA2: 'DARK_GREEN',
    0xA5: 'GREEN',
    0xAA: 'BROWN',
    0xB3: 'DARK_BLUE',
    0xBF: 'RED',
    0xC6: 'BROWN',
    0xCE: 'DARK_BLUE',
    0xD1: 'BROWN',
    0xD3: 'DARK_GREEN',
    0xDB: 'YELLOW',
    0xE0: 'BROWN',
    0xE8: 'DARK_BLUE',
    0xF0: 'BROWN',
    0xF2: 'BROWN',
    0xF4: 'DARK_BLUE',
    0xF6: 'BROWN',
    0xFF: 'DARK_GREEN',
}

# Disambiguation: (checksum, 4th title char) → palette override
_TITLE_CHAR_OVERRIDES = {
    (0x59, 'E'): 'RED',
    (0x20, 'E'): 'RED',
}

# Title-based overrides for well-known games (fallback when checksum not in table)
_TITLE_OVERRIDES = {
    'POKEMON RED': 'RED',
    'POKEMON BLUE': 'BLUE',
    'POKEMON GREEN': 'GREEN',
    'POKEMON YELLO': 'YELLOW',      # Title truncated to 14 chars
    'POKEMON YELLOW': 'YELLOW',
    'TETRIS': 'BLUE',
    'ZELDA': 'GREEN',
    'METROID2': 'GREEN',
    'KIRBY DREAM LA': 'PASTEL',
    'MARIO LAND2': 'BROWN',
    'SUPER MARIOLAND': 'BROWN',
    'MEGAMAN': 'BLUE',
    'DONKEY KONG': 'BROWN',
}


def get_palette(header_checksum, title=''):
    """Look up the GBC boot ROM color palette for a DMG cartridge.

    Args:
        header_checksum: byte 0x014D from the ROM header
        title: game title string from the ROM header

    Returns:
        (bg_palette, obj0_palette, obj1_palette) where each palette is a
        tuple of 4 (R, G, B) tuples mapping shade 0-3 to RGB colors.
    """
    # Check (checksum, 4th char) disambiguation first
    fourth_char = title[3] if len(title) > 3 else ''
    key = (header_checksum, fourth_char)
    if key in _TITLE_CHAR_OVERRIDES:
        name = _TITLE_CHAR_OVERRIDES[key]
        return _PALETTE_SETS[name]

    # Standard checksum lookup
    name = _CHECKSUM_TABLE.get(header_checksum)
    if name is not None:
        return _PALETTE_SETS[name]

    # Title-based fallback for well-known games
    if title in _TITLE_OVERRIDES:
        name = _TITLE_OVERRIDES[title]
        return _PALETTE_SETS[name]

    # Default: grayscale
    return _PALETTE_SETS['GRAYSCALE']
