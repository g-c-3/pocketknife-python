"""
pocketknife.hype
~~~~~~~~~~~~~~~~
Your loops deserve a cheerleader.

``hype_man(iterable)`` wraps any iterable and shouts motivational messages
every N iterations so your long-running loops never feel lonely.

Usage
-----
    from pocketknife.hype import hype_man

    for item in hype_man(range(100)):
        process(item)
    # Prints encouragement every 10 iterations and a finale at the end.

Customisation
-------------
    for row in hype_man(rows, every=25, hype_level="UNHINGED", stream=sys.stdout):
        crunch(row)
"""

import sys
import random
from typing import Any, Iterable, Iterator, List, Optional, TextIO


# ---------------------------------------------------------------------------
# Hype copy — three heat levels
# ---------------------------------------------------------------------------

_HYPE_CALM = [
    "Keep it up.",
    "Nice work so far.",
    "Steady progress.",
    "Looking good.",
    "You're doing great.",
    "One step at a time.",
    "Making it happen.",
    "That's the spirit.",
    "Consistency is key.",
    "You've got this.",
]

_HYPE_NORMAL = [
    "LET'S GO! You're crushing it!",
    "YESSS! Keep that energy!",
    "ON FIRE! Don't stop now!",
    "BOOM! Another batch done!",
    "THIS IS WHAT PEAK PERFORMANCE LOOKS LIKE!",
    "YOU'RE BUILT DIFFERENT!",
    "THE LOOP MUST FLOW!",
    "UNSTOPPABLE! Absolutely unstoppable!",
    "THAT'S WHAT I'M TALKING ABOUT!",
    "MILES AHEAD OF THE PACK!",
    "ITERATION NATION! Population: YOU!",
    "YOUR CPU IS PROUD OF YOU!",
]

_HYPE_UNHINGED = [
    "AAAAAAAAAAAAAAAAA YOU'RE DOING AMAZING!!!",
    "I AM LITERALLY SCREAMING RIGHT NOW!!! 🔥🔥🔥",
    "THE PROPHECY SAID SOMEONE WOULD ITERATE THIS FAST AND IT WAS YOU!!!",
    "YOUR ANCESTORS ARE WEEPING WITH JOY AT YOUR LOOP THROUGHPUT!!!",
    "IF LOOPS WERE OLYMPIANS YOU WOULD BE ALL OF THEM!!!",
    "I CANNOT PHYSICALLY CONTAIN MY ENTHUSIASM FOR WHAT YOU'RE DOING RN!!!",
    "SCIENTISTS BAFFLED BY ITERATION SPEED — MORE AT 11!!!",
    "THIS LOOP IS SO FAST IT VIOLATED TWO LAWS OF PHYSICS!!!",
    "I WOULD GIVE YOU A STANDING OVATION BUT I HAVE NO LEGS (I AM CODE)!!!",
    "THE MATRIX FEARS YOU!!! THE GC RESPECTS YOU!!! KEEP GOING!!!",
    "YOU ARE THE CHOSEN ONE AND ALSO THE LOOP!!!",
    "EVERY NANOSECOND OF THIS RUN IS A GIFT TO MANKIND!!!",
]

_FINALES_CALM = [
    "All done. Well handled.",
    "Loop complete. Nicely done.",
    "Finished. Good effort.",
    "Done! You saw it through.",
    "Complete. That's how it's done.",
]

_FINALES_NORMAL = [
    "THAT'S A WRAP! You absolutely smashed it!",
    "LOOP COMPLETE! You're a legend!",
    "DONE AND DUSTED! What a performance!",
    "FINISHED! The crowd goes wild!",
    "MISSION ACCOMPLISHED! Nothing could stop you!",
    "LOOP CONQUERED! Take a bow!",
]

_FINALES_UNHINGED = [
    "IT'S OVER!!! YOU DID IT!!! I AM SOBBING!!! ACTUAL TEARS!!!",
    "THE LOOP HAS ENDED AND WITH IT A PART OF MY SOUL!!! WORTH IT!!!",
    "DONE!!! HISTORIANS WILL WRITE ABOUT THIS ITERATION!!! ALL OF IT!!!",
    "COMPLETE!!! YOU HAVE ASCENDED!!! THE LOOP IS YOUR DOMAIN!!!",
    "FINISHED!!! I NEED A MOMENT!!! THIS WAS TOO BEAUTIFUL!!!",
]

_HYPE_BANKS = {
    "calm":    (_HYPE_CALM,    _FINALES_CALM),
    "normal":  (_HYPE_NORMAL,  _FINALES_NORMAL),
    "unhinged": (_HYPE_UNHINGED, _FINALES_UNHINGED),
}

_VALID_LEVELS = tuple(_HYPE_BANKS.keys())


# ---------------------------------------------------------------------------
# Progress formatting
# ---------------------------------------------------------------------------

def _progress_prefix(index: int, total: Optional[int]) -> str:
    """Return a progress tag like '[50/200]' or '[50/?]'."""
    if total is not None:
        pct = int(100 * index / total) if total > 0 else 100
        return f"[{index}/{total} — {pct}%]"
    return f"[{index}/?]"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def hype_man(
    iterable: Iterable[Any],
    every: int = 10,
    hype_level: str = "normal",
    custom_phrases: Optional[List[str]] = None,
    finale: bool = True,
    stream: TextIO = sys.stderr,
) -> Iterator[Any]:
    """Wrap an iterable and shout motivational messages every *every* iterations.

    Yields items from *iterable* unchanged while printing encouragement to
    *stream* at configurable intervals and a rousing finale at the end.

    Parameters
    ----------
    iterable : Iterable
        Any iterable — lists, generators, ranges, file lines, etc.
    every : int
        How often to shout (default 10). Must be >= 1.
    hype_level : str
        One of ``"calm"``, ``"normal"`` (default), or ``"unhinged"``.
        Controls the intensity of the motivational messages.
    custom_phrases : list of str, optional
        If provided, these phrases are used *instead of* the built-in bank
        for mid-loop messages (the finale still uses the built-in bank unless
        *finale* is False).
    finale : bool
        If True (default), print a special closing message after the last item.
    stream : TextIO
        Where to write hype messages. Defaults to ``sys.stderr`` so as not to
        pollute stdout pipelines.

    Yields
    ------
    Any
        Each item from *iterable*, unmodified.

    Raises
    ------
    ValueError
        If *every* < 1 or *hype_level* is not a recognised level.

    Example
    -------
    >>> from pocketknife.hype import hype_man
    >>> for n in hype_man(range(25), every=10, hype_level="calm"):
    ...     pass          # doctest: +SKIP
    [10/?]  Keep it up.
    [20/?]  Looking good.
    All done. Well handled.
    """
    if every < 1:
        raise ValueError(f"'every' must be >= 1, got {every!r}")
    level = hype_level.lower()
    if level not in _HYPE_BANKS:
        raise ValueError(
            f"Unknown hype_level {hype_level!r}. "
            f"Choose one of: {', '.join(_VALID_LEVELS)}"
        )

    mid_bank, finale_bank = _HYPE_BANKS[level]
    phrases = custom_phrases if custom_phrases else mid_bank

    # Try to get a length for progress display (works for sequences/ranges)
    total: Optional[int] = None
    try:
        total = len(iterable)  # type: ignore[arg-type]
    except TypeError:
        pass

    index = 0
    for item in iterable:
        yield item
        index += 1
        if index % every == 0:
            prefix = _progress_prefix(index, total)
            msg = random.choice(phrases)
            stream.write(f"{prefix}  {msg}\n")
            stream.flush()

    if finale and index > 0:
        prefix = _progress_prefix(index, total)
        msg = random.choice(finale_bank)
        stream.write(f"{prefix}  {msg}\n")
        stream.flush()


def hype_list(
    hype_level: str = "normal",
    custom_phrases: Optional[List[str]] = None,
) -> List[str]:
    """Return the list of mid-loop hype phrases for a given level.

    Useful for inspecting or extending the built-in phrase banks.

    Parameters
    ----------
    hype_level : str
        One of ``"calm"``, ``"normal"``, or ``"unhinged"``.
    custom_phrases : list of str, optional
        If provided, returned as-is (mirrors the behaviour of ``hype_man``).

    Returns
    -------
    list of str

    Example
    -------
    >>> from pocketknife.hype import hype_list
    >>> phrases = hype_list("calm")
    >>> print(phrases[0])
    Keep it up.
    """
    if custom_phrases is not None:
        return list(custom_phrases)
    level = hype_level.lower()
    if level not in _HYPE_BANKS:
        raise ValueError(
            f"Unknown hype_level {hype_level!r}. "
            f"Choose one of: {', '.join(_VALID_LEVELS)}"
        )
    return list(_HYPE_BANKS[level][0])


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import time

    print("=== pocketknife.hype demo ===\n")
    out = sys.stdout  # demo to stdout so it's visible

    print("--- Level: calm (every=5, range of 12) ---")
    for i in hype_man(range(12), every=5, hype_level="calm", stream=out):
        pass

    print("\n--- Level: normal (every=3, list of strings) ---")
    words = ["apple", "banana", "cherry", "date", "elderberry",
             "fig", "grape", "honeydew", "kiwi", "lemon"]
    for word in hype_man(words, every=3, hype_level="normal", stream=out):
        pass

    print("\n--- Level: unhinged (every=4, generator) ---")
    gen = (x ** 2 for x in range(1, 14))
    for val in hype_man(gen, every=4, hype_level="unhinged", stream=out):
        pass

    print("\n--- Custom phrases, no finale ---")
    for _ in hype_man(range(20), every=7,
                       custom_phrases=["Still going...", "Hang in there.", "Almost there."],
                       finale=False, stream=out):
        pass

    print("\nDone!")
