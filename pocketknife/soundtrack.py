"""
pocketknife.soundtrack
~~~~~~~~~~~~~~~~~~~~~~
Every function deserves a theme song.

`run_with_music(fn, url, *args, **kwargs)` runs *fn*, times how long it
takes, and prints a music link before and after — so you (and anyone
watching your terminal) know exactly what to queue up while the code runs,
and how far into the track you'd have gotten by the time it finished.

Usage
-----
    from pocketknife.soundtrack import run_with_music

    def slow_thing():
        time.sleep(3)
        return 42

    result = run_with_music(slow_thing, "https://open.spotify.com/track/...")
    # 🎵 Now playing: https://open.spotify.com/track/...
    # ⏳ Running slow_thing()...
    # ✅ Done in 3.00s — you made it through the intro.
"""

import time
from typing import Any, Callable, Optional


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _duration_commentary(elapsed: float) -> str:
    """Return a flavor-text comment about elapsed time, song-listening style."""
    if elapsed < 1:
        return "barely enough time to read the track title."
    if elapsed < 5:
        return "you made it through the intro."
    if elapsed < 15:
        return "first verse, easy."
    if elapsed < 30:
        return "through the first chorus by now."
    if elapsed < 60:
        return "deep into the second verse."
    if elapsed < 180:
        return "you've probably heard the whole song."
    if elapsed < 600:
        return "time for an encore. Maybe two."
    return "honestly, put on a whole album for this one."


def _format_elapsed(elapsed: float) -> str:
    """Format an elapsed-time float as a human-readable string."""
    if elapsed < 60:
        return f"{elapsed:.2f}s"
    minutes, seconds = divmod(elapsed, 60)
    return f"{int(minutes)}m {seconds:.1f}s"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def run_with_music(
    fn: Callable[..., Any],
    url: str,
    *args,
    stream=None,
    **kwargs,
) -> Any:
    """Run *fn(*args, **kwargs)*, printing a music link timed to its duration.

    Prints the music link and a "now playing" message before *fn* starts,
    then reports the elapsed time and a bit of flavor commentary once it
    finishes. The function's return value (or raised exception) passes
    through unchanged — this is a transparent wrapper, not a sandbox.

    Parameters
    ----------
    fn : Callable
        The function to run and time.
    url : str
        A music link (Spotify, YouTube, SoundCloud, whatever) to display.
    *args :
        Positional arguments forwarded to *fn*.
    stream :
        Where to print messages. Defaults to ``sys.stdout`` (resolved at
        call time, not import time).
    **kwargs :
        Keyword arguments forwarded to *fn*.

    Returns
    -------
    Any
        Whatever *fn* returns.

    Raises
    ------
    Exception
        Whatever *fn* raises — re-raised after the timing message is still
        printed, so you know how long it took to fail.

    Example
    -------
    >>> from pocketknife.soundtrack import run_with_music
    >>> def add(a, b):
    ...     return a + b
    >>> run_with_music(add, "https://open.spotify.com/track/abc123", 2, 3)
    🎵 Now playing: https://open.spotify.com/track/abc123
    ⏳ Running add()...
    ✅ Done in 0.00s — barely enough time to read the track title.
    5
    """
    if stream is None:
        import sys
        stream = sys.stdout

    fn_name = getattr(fn, "__name__", repr(fn))

    stream.write(f"🎵 Now playing: {url}\n")
    stream.write(f"⏳ Running {fn_name}()...\n")
    stream.flush()

    start = time.perf_counter()
    try:
        result = fn(*args, **kwargs)
    except Exception:
        elapsed = time.perf_counter() - start
        commentary = _duration_commentary(elapsed)
        stream.write(f"💥 Failed after {_format_elapsed(elapsed)} — {commentary}\n")
        stream.flush()
        raise

    elapsed = time.perf_counter() - start
    commentary = _duration_commentary(elapsed)
    stream.write(f"✅ Done in {_format_elapsed(elapsed)} — {commentary}\n")
    stream.flush()

    return result


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== pocketknife.soundtrack demo ===\n")

    def quick_add(a, b):
        return a + b

    def slow_burn():
        time.sleep(1.2)
        return "done thinking"

    def will_explode():
        time.sleep(0.3)
        raise RuntimeError("forgot to carry the one")

    print("1. Quick function with a track:\n")
    result = run_with_music(
        quick_add, "https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b", 2, 3
    )
    print(f"   --> Returned: {result}\n")

    print("2. A slower function (~1.2s):\n")
    result = run_with_music(
        slow_burn, "https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT"
    )
    print(f"   --> Returned: {result!r}\n")

    print("3. A function that fails — timing still reported:\n")
    try:
        run_with_music(
            will_explode, "https://open.spotify.com/track/7qiZfU4dY1lWllzX7mPBI3"
        )
    except RuntimeError as exc:
        print(f"   --> Caught expected exception: {exc}\n")

    print("Demo complete. Hope you enjoyed the soundtrack.")
