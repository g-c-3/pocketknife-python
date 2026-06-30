"""
pocketknife.pet
~~~~~~~~~~~~~~~~
A tiny terminal bird that needs you. Every day.

`feed_the_bird()` is a minimal Tamagotchi-style virtual pet that lives in a
small JSON state file on disk. Its mood degrades the longer you go without
feeding it, and resets to happy each time you check in. No dependencies,
no daemon, no notifications — just guilt, delivered on demand.

Usage
-----
    from pocketknife.pet import feed_the_bird

    feed_the_bird()
    # 🐦 Tweet! Your bird is doing great. (fed today)

State is stored in ~/.pocketknife_bird.json by default (configurable via
the `state_path` parameter, mainly for testing).
"""

import json
import os
import time
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_STATE_PATH = Path.home() / ".pocketknife_bird.json"

_SECONDS_PER_DAY = 86400

# Mood thresholds, in whole days since last feeding.
_MOOD_THRESHOLDS = [
    (0, "ecstatic", "🐦 Tweet! Your bird is doing great."),
    (1, "content", "🐤 Your bird seems okay, but could use some attention."),
    (3, "lonely", "😟 Your bird looks a little lonely. It's been a few days."),
    (7, "sulking", "😢 Your bird is giving you the silent treatment. A week, really?"),
    (14, "forlorn", "💔 Your bird has lost hope. It's been two weeks."),
]
_ABANDONED_MOOD = ("abandoned", "🪦 Your bird has moved on emotionally. It's been over a month.")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _load_state(state_path: Path) -> dict:
    """Load pet state from disk, returning a fresh default if missing/corrupt."""
    try:
        with open(state_path, "r") as f:
            data = json.load(f)
        if not isinstance(data, dict) or "last_fed" not in data:
            raise ValueError("malformed state file")
        return data
    except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError):
        return {"last_fed": None, "feed_count": 0, "created": time.time()}


def _save_state(state_path: Path, state: dict) -> bool:
    """Save pet state to disk. Returns True on success, False on failure."""
    try:
        state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(state_path, "w") as f:
            json.dump(state, f)
        return True
    except OSError:
        return False


def _days_since(timestamp: Optional[float], now: float) -> Optional[float]:
    """Return whole-ish days elapsed since timestamp, or None if never fed."""
    if timestamp is None:
        return None
    return (now - timestamp) / _SECONDS_PER_DAY


def _mood_for_days(days: Optional[float]) -> tuple:
    """Return (mood_name, message) for a given days-since-last-feeding value.

    A None value (never fed before) is treated as a brand-new bird.
    """
    if days is None:
        return "newborn", "🥚 A new bird has hatched! Feed it daily to keep it happy."

    if days >= 30:
        return _ABANDONED_MOOD

    # Walk thresholds from highest to lowest, picking the first one the
    # elapsed days satisfies.
    mood, message = _MOOD_THRESHOLDS[0][1], _MOOD_THRESHOLDS[0][2]
    for threshold_days, name, msg in _MOOD_THRESHOLDS:
        if days >= threshold_days:
            mood, message = name, msg
    return mood, message


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def feed_the_bird(
    state_path: Optional[Path] = None,
    stream=None,
    _now: Optional[float] = None,
) -> dict:
    """Feed the terminal bird, printing its current mood and resetting it to happy.

    Reads persisted state from *state_path* (default
    ``~/.pocketknife_bird.json``), reports the bird's mood based on how long
    it's been since the last feeding, then updates the state to record this
    feeding and saves it back to disk.

    Parameters
    ----------
    state_path : Path, optional
        Where to store/read the bird's state. Defaults to
        ``~/.pocketknife_bird.json``. Mainly overridden for testing.
    stream :
        Where to print the mood message. Defaults to ``sys.stdout``
        (resolved at call time).
    _now : float, optional
        Internal hook for testing — overrides "the current time" as a Unix
        timestamp. Not intended for normal use.

    Returns
    -------
    dict
        The bird's updated state: ``{"last_fed": <ts>, "feed_count": <int>,
        "created": <ts>, "mood": <str>, "days_since_last_feeding": <float|None>}``.

    Example
    -------
    >>> from pocketknife.pet import feed_the_bird
    >>> state = feed_the_bird()
    🐦 Tweet! Your bird is doing great.
    >>> state["feed_count"] >= 1
    True
    """
    if stream is None:
        import sys
        stream = sys.stdout

    path = Path(state_path) if state_path is not None else DEFAULT_STATE_PATH
    now = _now if _now is not None else time.time()

    state = _load_state(path)
    days = _days_since(state.get("last_fed"), now)
    mood, message = _mood_for_days(days)

    stream.write(message + "\n")
    if days is not None and days >= 1:
        whole_days = int(days)
        unit = "day" if whole_days == 1 else "days"
        stream.write(f"   (last fed {whole_days} {unit} ago)\n")
    stream.flush()

    state["last_fed"] = now
    state["feed_count"] = state.get("feed_count", 0) + 1
    if "created" not in state:
        state["created"] = now
    state["mood"] = mood
    state["days_since_last_feeding"] = days

    _save_state(path, state)

    return state


def bird_status(
    state_path: Optional[Path] = None,
    _now: Optional[float] = None,
) -> dict:
    """Check the bird's current mood without feeding it (read-only).

    Unlike :func:`feed_the_bird`, this does NOT reset the bird's mood or
    update the saved state — it's purely informational.

    Parameters
    ----------
    state_path : Path, optional
        Where to read the bird's state from. Defaults to
        ``~/.pocketknife_bird.json``.
    _now : float, optional
        Internal hook for testing.

    Returns
    -------
    dict
        ``{"mood": <str>, "message": <str>, "days_since_last_feeding": <float|None>,
        "feed_count": <int>}``.

    Example
    -------
    >>> from pocketknife.pet import bird_status
    >>> status = bird_status()
    >>> "mood" in status
    True
    """
    path = Path(state_path) if state_path is not None else DEFAULT_STATE_PATH
    now = _now if _now is not None else time.time()

    state = _load_state(path)
    days = _days_since(state.get("last_fed"), now)
    mood, message = _mood_for_days(days)

    return {
        "mood": mood,
        "message": message,
        "days_since_last_feeding": days,
        "feed_count": state.get("feed_count", 0),
    }


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import tempfile

    print("=== pocketknife.pet demo ===\n")
    print("(using a temporary state file so this demo doesn't touch your real bird)\n")

    with tempfile.TemporaryDirectory() as tmp:
        demo_path = Path(tmp) / "demo_bird.json"

        print("1. First feeding (brand new bird):")
        feed_the_bird(state_path=demo_path)

        print("\n2. Feeding again immediately:")
        feed_the_bird(state_path=demo_path)

        print("\n3. Checking status without feeding:")
        status = bird_status(state_path=demo_path)
        print(f"   Mood: {status['mood']}, fed {status['feed_count']} times so far")

        print("\n4. Simulating 5 days of neglect, then feeding:")
        five_days_ago_now = time.time() + (5 * _SECONDS_PER_DAY)
        feed_the_bird(state_path=demo_path, _now=five_days_ago_now)

        print("\n5. Simulating 35 days of neglect (abandoned bird):")
        far_future = time.time() + (40 * _SECONDS_PER_DAY)
        feed_the_bird(state_path=demo_path, _now=far_future)

    print("\nDemo complete. Your real bird is waiting at ~/.pocketknife_bird.json")
