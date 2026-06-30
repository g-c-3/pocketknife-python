"""
pocketknife.fortune
~~~~~~~~~~~~~~~~~~~
For when your code crashes and you'd rather be reminded that all suffering
is impermanent than blamed for it.

`zen_crash()` registers a sys.excepthook (much like `pocketknife.blame`'s
`git_roulette`, but with significantly less finger-pointing) that appends
a peaceful proverb to the bottom of any unhandled traceback.

Usage
-----
    from pocketknife.fortune import zen_crash

    zen_crash()

    raise ValueError("the build is broken")
    # => Traceback ... ValueError: the build is broken
    #    🪷 "The bug you chase, chases you back. Let it pass."
"""

import random
import sys
import traceback
from typing import Optional


# ---------------------------------------------------------------------------
# Proverbs
# ---------------------------------------------------------------------------

_PROVERBS = [
    "The bug you chase, chases you back. Let it pass.",
    "A stack trace is just the mountain showing you the path you climbed.",
    "Before the crash: a function. After the crash: a function. Nothing was lost.",
    "The null pointer points to nothing, and so finds peace.",
    "Even the finest code returns to dust; even the finest dust compiles to code.",
    "You did not break the build. The build was never whole to begin with.",
    "Breathe. The exception is temporary. The lesson is not.",
    "What is undefined was never meant to be defined.",
    "The river does not apologize for flooding. Neither should your code for failing.",
    "In the space between try and except, there is only now.",
    "A watched process never crashes. An unwatched one always does. Do not watch.",
    "The error message is a teacher wearing an unkind face.",
    "Let the stack unwind as the autumn leaves unwind from the branch.",
    "There is no bug. There is only code that has not yet found its way.",
    "To fix is to attach. To accept is to debug tomorrow.",
    "The traceback points backward so that you may walk forward.",
    "Even silence has a return value. Even crashes have closure.",
    "What crashes once may crash again. What is observed with patience, rarely does.",
]


def _random_proverb() -> str:
    """Return a single random proverb string."""
    return random.choice(_PROVERBS)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def zen_crash(stream=sys.stderr) -> None:
    """Register a sys.excepthook that appends a peaceful proverb to crashes.

    Call this once at the top of your script or application entry-point.
    Every subsequent *unhandled* exception will print its normal traceback
    followed by a calming, vaguely profound proverb — because stack traces
    are stressful enough without anyone telling you whose fault it is.

    Parameters
    ----------
    stream :
        Where to write the proverb. Defaults to ``sys.stderr`` to stay
        consistent with the standard traceback output.

    Example
    -------
    >>> from pocketknife.fortune import zen_crash
    >>> zen_crash()
    >>> raise RuntimeError("oops")
    Traceback (most recent call last):
      ...
    RuntimeError: oops
    🪷 "The bug you chase, chases you back. Let it pass."
    """

    def _hook(exc_type, exc_value, exc_tb):
        # Print the normal traceback first so nothing is lost.
        traceback.print_exception(exc_type, exc_value, exc_tb, file=stream)
        proverb = _random_proverb()
        print(f'\n🪷 "{proverb}"', file=stream)

    sys.excepthook = _hook


def fortune_once() -> str:
    """Return a single formatted proverb string without touching the hook.

    Useful for logging, status messages, splash screens, or just a moment
    of calm before a deploy.

    Returns
    -------
    str
        A formatted proverb string, e.g. ``'🪷 "Breathe. The exception is
        temporary. The lesson is not."'``.

    Example
    -------
    >>> from pocketknife.fortune import fortune_once
    >>> print(fortune_once())
    🪷 "Breathe. The exception is temporary. The lesson is not."
    """
    return f'🪷 "{_random_proverb()}"'


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== pocketknife.fortune demo ===\n")

    print("1. fortune_once() (no exception needed):")
    for _ in range(3):
        print("  ", fortune_once())

    print()
    print("2. Registering zen_crash() as the global exception hook...")
    zen_crash()
    print("   Hook registered. Raising a demo exception in 3... 2... 1...\n")
    raise RuntimeError("this is a demonstration crash — entirely intentional")
