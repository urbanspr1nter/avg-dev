"""TUI implementation using ncurses."""

import curses
from typing import List


def tui_app(stdscr):
    # disable line buffering - characters made available immediately
    curses.cbreak()

    # don't echo typed characters automatically
    curses.noecho()

    # show cursor (make it visible)
    curses.curs_set(1)

    height, width = stdscr.getmaxyx()

    # We need to enable keypad to translate special keys to curses key constants!
    stdscr.keypad(True)

    # Calculate the height of the components based on the terminal size
    display_height = min(20, height - 2)
    input_height = max(1, height - display_height)

    # Display message pane
    display_area = stdscr.subwin(display_height, width, 0, 0)

    # Input area (bottom line)
    input_area = stdscr.subwin(input_height, width, display_height, 0)

    # keypad mode: When the user presses special keys, translate their terminal escape sequences into curses key constants.
    input_area.keypad(True)

    display_lines: List[str] = []
    input_text = ""
    cursor_pos = 0

    while True:
        # clear and refresh the display
        display_area.clear()
        input_area.clear()

        # render the display area
        display_area.box()
        for i, line in enumerate(display_lines):
            display_area.addstr(i + 1, 1, line)

        # Render input area with cursor
        input_area.addstr(0, 0, f"> {input_text}")

        # move cursor to correct position
        input_area.move(0, cursor_pos + 2)

        # Refresh both windows
        display_area.refresh()
        input_area.refresh()

        # get the input
        try:
            key = input_area.getch()
        except Exception as e:
            break  # handle any window resize or other errors

        # process input
        if key == curses.KEY_ENTER or key == 10:
            if input_text.strip():
                display_lines.append(input_text)
                input_text = ""
                cursor_pos = 0
        elif key == curses.KEY_BACKSPACE or key == 127:
            if cursor_pos > 0:
                input_text = input_text[: cursor_pos - 1] + input_text[cursor_pos:]
                cursor_pos -= 1
        elif key == curses.KEY_LEFT:  # left arrow
            if cursor_pos > 0:
                cursor_pos -= 1
        elif key == curses.KEY_RIGHT:  # right arrow
            if cursor_pos < len(input_text):
                cursor_pos += 1
        elif key == curses.KEY_UP:
            pass  # TODO: Do something later with it
        elif key == curses.KEY_DOWN:
            pass  # TODO: Do something later with it
        elif key >= 32 and key <= 126:
            input_text = input_text[:cursor_pos] + chr(key) + input_text[cursor_pos:]
            cursor_pos += 1
        elif key == curses.KEY_RESIZE:
            height, width = stdscr.getmaxyx()

            display_height = min(20, height - 2)
            input_height = max(1, height - display_height)

            stdscr.clear()

            display_area = stdscr.subwin(display_height, width, 0, 0)
            input_area = stdscr.subwin(input_height, width, display_height, 0)

            input_area.keypad(True)

        if key == 27:  # ESC
            break


def run_tui():
    """Main TUI entry point."""
    curses.wrapper(tui_app)
