"""
pocketknife.blame
~~~~~~~~~~~~~~~~~
Because *someone* has to be responsible.

On any unhandled exception, `git_roulette()` reaches into your repo's git log,
picks a random contributor, and very fairly assigns blame to them.

Usage
-----
    from pocketknife.blame import git_roulette

    # Register once at startup — all subsequent crashes will name a culprit.
    git_roulette()

    raise ValueError("something is very wrong")
    # => Traceback ... ValueError: something is very wrong
    #    🎲 Git Roulette says: this is definitely Jordan's fault.
"""

import random
import subprocess
import sys
import traceback
from typing import List, Optional


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_git_authors() -> List[str]:
    """Return a deduplicated list of author names from `git log`.

    Returns an empty list if git is unavailable, the command fails, or the
    repository has no commits yet.
    """
    try:
        result = subprocess.run(
            ["git", "log", "--format=%an"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return []
        names = [name.strip() for name in result.stdout.splitlines() if name.strip()]
        # Deduplicate while preserving order so common contributors aren't
        # disproportionately blamed... or maybe they should be.
        seen: set = set()
        unique: List[str] = []
        for name in names:
            if name not in seen:
                seen.add(name)
                unique.append(name)
        return unique
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return []


def _pick_culprit(authors: List[str]) -> Optional[str]:
    """Pick a random author from the list, or None if the list is empty."""
    return random.choice(authors) if authors else None


def _blame_message(culprit: Optional[str]) -> str:
    """Return a formatted blame string for the given culprit (or a fallback)."""
    templates = [
        "this is definitely {name}'s fault.",
        "have you tried blaming {name}?",
        "{name} was the last one to touch this.",
        "classic {name} moment.",
        "sources close to the repo point to {name}.",
        "{name} said it was fine. It was not fine.",
        "ask {name}. They'll know.",
        "git log doesn't lie. {name} was here.",
    ]
    no_git_messages = [
        "blame is unavailable (no git history found). Blame yourself.",
        "git log returned nothing. The culprit remains at large.",
        "no contributors found — you're flying solo and this is entirely on you.",
    ]

    if culprit is None:
        return random.choice(no_git_messages)
    return random.choice(templates).format(name=culprit)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def git_roulette(stream=sys.stderr) -> None:
    """Register a sys.excepthook that blames a random git contributor on crash.

    Call this once at the top of your script or application entry-point.
    All subsequent *unhandled* exceptions will append a blame line to the
    standard traceback output.

    Parameters
    ----------
    stream:
        Where to write the blame message. Defaults to ``sys.stderr`` to stay
        consistent with the standard traceback output.

    Example
    -------
    >>> from pocketknife.blame import git_roulette
    >>> git_roulette()
    >>> raise RuntimeError("oops")
    Traceback (most recent call last):
      ...
    RuntimeError: oops
    🎲 Git Roulette says: this is definitely Jordan's fault.
    """

    def _hook(exc_type, exc_value, exc_tb):
        # Print the normal traceback first so nothing is lost.
        traceback.print_exception(exc_type, exc_value, exc_tb, file=stream)
        authors = _get_git_authors()
        culprit = _pick_culprit(authors)
        message = _blame_message(culprit)
        print(f"\n🎲 Git Roulette says: {message}", file=stream)

    sys.excepthook = _hook


def blame_once() -> str:
    """Return a one-off blame string without registering a global hook.

    Useful for logging, testing, or manually inserting blame into output.

    Returns
    -------
    str
        A formatted blame string, e.g. ``"🎲 Git Roulette says: classic Jordan moment."``.

    Example
    -------
    >>> from pocketknife.blame import blame_once
    >>> print(blame_once())
    🎲 Git Roulette says: classic Jordan moment.
    """
    authors = _get_git_authors()
    culprit = _pick_culprit(authors)
    message = _blame_message(culprit)
    return f"🎲 Git Roulette says: {message}"


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== pocketknife.blame demo ===\n")

    print("1. blame_once() (no exception needed):")
    for _ in range(3):
        print("  ", blame_once())

    print()
    print("2. Registering git_roulette() as the global exception hook...")
    git_roulette()
    print("   Hook registered. Raising a demo exception in 3... 2... 1...\n")
    raise RuntimeError("this is a demonstration crash — entirely intentional")
