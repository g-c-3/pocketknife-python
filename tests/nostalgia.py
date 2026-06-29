"""
pocketknife.nostalgia
~~~~~~~~~~~~~~~~~~~~~
For those who miss the good old days of 28.8k modems and green phosphor screens.

Functions
---------
dial_up_print(text, ...)
    Prints text one character at a time with realistic modem-era typing delays
    and optional ASCII "sound" bursts.

matrix_rain(duration, ...)
    Renders a Matrix-style green character rain in the terminal for a given
    number of seconds, then restores the screen.
"""

import os
import random
import sys
import time
from typing import Optional


# ---------------------------------------------------------------------------
# dial_up_print
# ---------------------------------------------------------------------------

# Authentic-ish modem negotiation noise, rendered in ASCII art
_MODEM_HANDSHAKE = r"""
  ~*~  Connecting...  ~*~

  ATH0
  ATE1V1
  ATDT 555-2600

  CONNECT 28800

  CARRIER DETECTED
  ~~~~~~~~~~~~~~~~~~
"""

_MODEM_SOUNDS = [
    "SCREEEEEEEE",
    "KSSHHHHHHH",
    "BLING BLING BLING",
    "PSHHHHHWWWW",
    "BONG BONG BONG",
    "KRRRRRRRR",
    "KSHHHHH... PING",
]


def dial_up_print(
    text: str,
    min_delay: float = 0.02,
    max_delay: float = 0.09,
    glitch_chance: float = 0.03,
    modem_intro: bool = True,
    stream=sys.stdout,
) -> None:
    """Print *text* one character at a time, simulating a 28.8k modem connection.

    Characters appear with randomised delays to mimic the uneven throughput of
    a dial-up connection. Occasional "glitches" briefly show a wrong character
    before self-correcting, just like the real thing.

    Parameters
    ----------
    text : str
        The text to print.
    min_delay : float
        Minimum per-character delay in seconds (default 0.02).
    max_delay : float
        Maximum per-character delay in seconds (default 0.09).
    glitch_chance : float
        Probability (0–1) of a glitch occurring on any given character
        (default 0.03, i.e. ~3%).
    modem_intro : bool
        If True (default), print an ASCII modem-handshake header first.
    stream :
        Output stream (defaults to ``sys.stdout``).

    Example
    -------
    >>> from pocketknife.nostalgia import dial_up_print
    >>> dial_up_print("Welcome to the Information Superhighway!")
    """
    if modem_intro:
        # Print the handshake slowly for atmosphere
        for ch in _MODEM_HANDSHAKE:
            stream.write(ch)
            stream.flush()
            time.sleep(random.uniform(0.005, 0.02))
        # Random modem sound burst
        sound = random.choice(_MODEM_SOUNDS)
        stream.write(f"\n  [ {sound} ]\n\n")
        stream.flush()
        time.sleep(0.4)

    glitch_chars = list("@#$%&*!?~^<>|\\")

    for char in text:
        delay = random.uniform(min_delay, max_delay)

        # Occasional packet loss / line noise glitch
        if random.random() < glitch_chance and char not in ("\n", "\r", "\t"):
            glitch = random.choice(glitch_chars)
            stream.write(glitch)
            stream.flush()
            time.sleep(0.06)
            # Backspace over the glitch character (works in most terminals)
            stream.write("\b \b")
            stream.flush()
            time.sleep(0.04)

        stream.write(char)
        stream.flush()
        time.sleep(delay)

    stream.write("\n")
    stream.flush()


# ---------------------------------------------------------------------------
# matrix_rain
# ---------------------------------------------------------------------------

# Katakana half-width + ASCII digits + Latin capitals — the canonical mix
_MATRIX_CHARS = (
    "ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ"
    "0123456789"
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
)

# ANSI escape helpers
_ANSI_GREEN_BRIGHT = "\033[1;32m"
_ANSI_GREEN_DIM    = "\033[0;32m"
_ANSI_WHITE_BRIGHT = "\033[1;37m"
_ANSI_RESET        = "\033[0m"
_ANSI_HIDE_CURSOR  = "\033[?25l"
_ANSI_SHOW_CURSOR  = "\033[?25h"
_ANSI_CLEAR        = "\033[2J"
_ANSI_HOME         = "\033[H"


def _move(row: int, col: int) -> str:
    """Return ANSI escape to move cursor to (row, col), 1-indexed."""
    return f"\033[{row};{col}H"


def _terminal_size() -> tuple:
    """Return (columns, rows) of the current terminal, with safe fallback."""
    try:
        size = os.get_terminal_size()
        return size.columns, size.lines
    except OSError:
        return 80, 24


def matrix_rain(
    duration: float = 5.0,
    fps: int = 15,
    stream=sys.stdout,
) -> None:
    """Render a Matrix-style green character rain in the terminal.

    Fills the terminal with falling columns of randomised Katakana/ASCII
    characters in classic green-on-black style for *duration* seconds, then
    restores the screen and cursor.

    Parameters
    ----------
    duration : float
        How long to run the animation in seconds (default 5.0).
    fps : int
        Target frames per second (default 15). Values above 30 may flicker
        depending on terminal speed.
    stream :
        Output stream (defaults to ``sys.stdout``).

    Notes
    -----
    Requires a terminal that supports ANSI escape codes (Linux, macOS, Windows
    Terminal). Plain IDLE or non-TTY pipes will fall back gracefully.

    Example
    -------
    >>> from pocketknife.nostalgia import matrix_rain
    >>> matrix_rain(duration=3.0)
    """
    cols, rows = _terminal_size()
    frame_time = 1.0 / fps

    # Each column tracks: current head position (row), trail length, speed
    # speed = rows to advance per frame (1 = every frame, 2 = every 2 frames…)
    class Column:
        def __init__(self, col_index: int):
            self.x = col_index
            self.head = random.randint(-rows, 0)   # start above the screen
            self.length = random.randint(6, rows // 2)
            self.speed = random.randint(1, 3)
            self.chars: list = [random.choice(_MATRIX_CHARS) for _ in range(rows)]
            self.frame_counter = 0

        def step(self):
            self.frame_counter += 1
            if self.frame_counter >= self.speed:
                self.frame_counter = 0
                self.head += 1
                # Randomly mutate a character in the trail for flicker effect
                mutate_row = self.head - random.randint(0, self.length)
                if 0 <= mutate_row < rows:
                    self.chars[mutate_row] = random.choice(_MATRIX_CHARS)
                # Reset when the tail clears the bottom
                if self.head - self.length > rows:
                    self.head = random.randint(-rows // 2, 0)
                    self.length = random.randint(6, rows // 2)
                    self.speed = random.randint(1, 3)

    columns = [Column(c) for c in range(1, cols + 1)]

    # Check if stream supports ANSI (rough heuristic)
    ansi_ok = hasattr(stream, "isatty") and stream.isatty()

    if not ansi_ok:
        # Non-TTY fallback: just print a brief text message
        stream.write("[matrix_rain: ANSI terminal required for rendering]\n")
        stream.flush()
        return

    try:
        stream.write(_ANSI_HIDE_CURSOR)
        stream.write(_ANSI_CLEAR)
        stream.flush()

        start = time.monotonic()
        while time.monotonic() - start < duration:
            frame_start = time.monotonic()
            buf = []

            for col in columns:
                col.step()
                head_row = col.head

                # Draw the head character (bright white)
                if 1 <= head_row <= rows:
                    buf.append(_move(head_row, col.x))
                    buf.append(_ANSI_WHITE_BRIGHT)
                    buf.append(col.chars[head_row - 1])

                # Draw the trail (bright green near head, dim further back)
                for offset in range(1, col.length + 1):
                    r = head_row - offset
                    if 1 <= r <= rows:
                        if offset < col.length // 3:
                            buf.append(_ANSI_GREEN_BRIGHT)
                        else:
                            buf.append(_ANSI_GREEN_DIM)
                        buf.append(_move(r, col.x))
                        buf.append(col.chars[r - 1])

                # Erase the character just behind the tail
                erase_row = head_row - col.length - 1
                if 1 <= erase_row <= rows:
                    buf.append(_move(erase_row, col.x))
                    buf.append(_ANSI_RESET)
                    buf.append(" ")

            stream.write("".join(buf))
            stream.flush()

            elapsed = time.monotonic() - frame_start
            sleep_time = frame_time - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    finally:
        # Always restore the terminal, even on Ctrl-C
        stream.write(_ANSI_RESET)
        stream.write(_ANSI_CLEAR)
        stream.write(_ANSI_HOME)
        stream.write(_ANSI_SHOW_CURSOR)
        stream.flush()


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== pocketknife.nostalgia demo ===\n")
    print("[ 1/2 ] dial_up_print demo — simulating a 28.8k connection...\n")
    time.sleep(0.5)

    dial_up_print(
        "Greetings, programs.\n"
        "You have (1) new message in your AOL Mailbox.\n"
        "The internet is a fad. Do not be alarmed.",
        modem_intro=True,
    )

    time.sleep(1.0)
    print("\n[ 2/2 ] matrix_rain — running for 4 seconds...\n")
    time.sleep(0.5)
    matrix_rain(duration=4.0, fps=15)

    print("Nostalgia trip complete. You may now return to the present.")
