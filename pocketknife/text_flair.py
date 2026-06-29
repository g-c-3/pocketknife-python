"""
pocketknife.text_flair
======================
Text transformation utilities for when plain text just isn't enough drama.

Functions
---------
spongecase(text)    — aLtErNaTiNg CaPs LiKe ThIs
leetspeak(text)     — c0nv3rts t3xt t0 l33t 5p34k
clapy(text)         — inserts 👏 clap 👏 emojis 👏 between 👏 words
"""

import random


# ---------------------------------------------------------------------------
# spongecase
# ---------------------------------------------------------------------------

def spongecase(text: str) -> str:
    """
    Return *text* with letters alternating between upper and lower case,
    à la Mocking SpongeBob meme.

    The transformation ignores non-letter characters — they pass through
    unchanged and do **not** consume an alternation slot.

    Parameters
    ----------
    text : str
        The input string to transform.

    Returns
    -------
    str
        The spongecase version of *text*.

    Examples
    --------
    >>> spongecase("hello world")
    'hElLo wOrLd'
    >>> spongecase("Python 3.12 is great!")
    'pYtHoN 3.12 iS gReAt!'
    """
    result = []
    upper = False  # start with lowercase
    for char in text:
        if char.isalpha():
            result.append(char.upper() if upper else char.lower())
            upper = not upper
        else:
            result.append(char)
    return "".join(result)


# ---------------------------------------------------------------------------
# leetspeak
# ---------------------------------------------------------------------------

_LEET_MAP: dict[str, str] = {
    "a": "4", "A": "4",
    "e": "3", "E": "3",
    "i": "1", "I": "1",
    "o": "0", "O": "0",
    "s": "5", "S": "5",
    "t": "7", "T": "7",
    "b": "8", "B": "8",
    "g": "9", "G": "9",
    "l": "1", "L": "1",
}


def leetspeak(text: str, intensity: float = 1.0) -> str:
    """
    Convert *text* to l33t 5p34k by substituting letters with look-alike
    digits and symbols.

    Parameters
    ----------
    text : str
        The input string to transform.
    intensity : float, optional
        A value between 0.0 and 1.0 controlling how aggressively letters
        are swapped. 1.0 (default) replaces every eligible letter; 0.5
        randomly replaces ~half of them. Useful for subtle l33t mode.

    Returns
    -------
    str
        The l33tspeak version of *text*.

    Raises
    ------
    ValueError
        If *intensity* is outside [0.0, 1.0].

    Examples
    --------
    >>> leetspeak("elite hacker")
    '3l173 h4ck3r'
    >>> leetspeak("leet")
    '1337'
    """
    if not 0.0 <= intensity <= 1.0:
        raise ValueError(f"intensity must be between 0.0 and 1.0, got {intensity!r}")

    result = []
    for char in text:
        if char in _LEET_MAP and random.random() <= intensity:
            result.append(_LEET_MAP[char])
        else:
            result.append(char)
    return "".join(result)


# ---------------------------------------------------------------------------
# clapy
# ---------------------------------------------------------------------------

def clapy(text: str, emoji: str = "👏") -> str:
    """
    Insert a clap emoji between every word in *text*, because sometimes
    you need to make 👏 a 👏 point 👏 emphatically.

    Leading/trailing whitespace is stripped; runs of internal whitespace
    are collapsed to a single space before clapping.

    Parameters
    ----------
    text : str
        The input string to transform.
    emoji : str, optional
        The separator emoji to use. Defaults to ``"👏"``. Swap for any
        string you like, e.g. ``"🔥"`` or ``" ✨ "``.

    Returns
    -------
    str
        The clapy version of *text*.

    Examples
    --------
    >>> clapy("read the room")
    'read 👏 the 👏 room'
    >>> clapy("ok boomer", emoji="💅")
    'ok 💅 boomer'
    """
    words = text.strip().split()
    if not words:
        return ""
    separator = f" {emoji} "
    return separator.join(words)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    samples = [
        "Why are you the way that you are",
        "Python is the best programming language",
        "Deploy on Friday what could go wrong",
    ]

    print("=" * 55)
    print("  pocketknife.text_flair  —  demo")
    print("=" * 55)

    for s in samples:
        print(f"\nOriginal : {s}")
        print(f"Sponge   : {spongecase(s)}")
        print(f"Leet     : {leetspeak(s)}")
        print(f"Clapy    : {clapy(s)}")

    print("\n--- intensity demo (leetspeak at 50%) ---")
    msg = "social engineering attacks are serious business"
    print(f"Full l33t : {leetspeak(msg)}")
    print(f"Half l33t : {leetspeak(msg, intensity=0.5)}")
    print(f"Custom 👏 : {clapy('read the room')}")
