"""
pocketknife.xp_tracker
=======================

Turns passing tests (or any function call) into a tiny RPG. Decorate a
function with ``@award_xp(points)`` and every successful call banks XP
to a hidden JSON file on disk. Cross a level threshold and you get a
"LEVEL UP!" announcement printed to stdout.

Public API
----------
award_xp(points, path=None)
    Decorator. On successful (non-raising) call of the wrapped
    function, adds ``points`` XP and prints a level-up message if the
    level increased.

get_stats(path=None) -> dict
    Returns the current XP/level state without modifying anything.

reset_xp(path=None) -> None
    Wipes the XP file back to zero.

level_for_xp(xp) -> int
    Pure function mapping total XP to a level number. Exposed because
    it's handy to test/reason about independently of the file I/O.
"""

from __future__ import annotations

import functools
import json
from pathlib import Path
from typing import Any, Callable, Dict, Optional, TypeVar

__all__ = ["award_xp", "get_stats", "reset_xp", "level_for_xp", "DEFAULT_XP_PATH"]

F = TypeVar("F", bound=Callable[..., Any])

# Hidden file lives in the user's home directory by default so XP
# persists across projects (it's meant to feel like *your* progress).
DEFAULT_XP_PATH = Path.home() / ".pocketknife_xp.json"

# Level N -> N+1 costs this much XP. Level 1->2 costs 100, 2->3 costs
# 150, 3->4 costs 200, etc. (arithmetic progression, +50 per level).
_BASE_COST = 100
_COST_STEP = 50


def level_for_xp(xp: int) -> int:
    """Return the level (starting at 1) reached by a given total XP."""
    if xp < 0:
        raise ValueError("xp cannot be negative")

    level = 1
    remaining = xp
    cost = _BASE_COST
    while remaining >= cost:
        remaining -= cost
        level += 1
        cost += _COST_STEP
    return level


def _xp_into_current_level(xp: int) -> int:
    """How much XP has been earned *within* the current level."""
    remaining = xp
    cost = _BASE_COST
    while remaining >= cost:
        remaining -= cost
        cost += _COST_STEP
    return remaining


def _cost_of_current_level(xp: int) -> int:
    """XP required to go from the current level to the next."""
    remaining = xp
    cost = _BASE_COST
    while remaining >= cost:
        remaining -= cost
        cost += _COST_STEP
    return cost


def _load(path: Path) -> Dict[str, int]:
    if not path.exists():
        return {"xp": 0}
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, dict) or "xp" not in data:
            return {"xp": 0}
        return {"xp": int(data["xp"])}
    except (json.JSONDecodeError, ValueError, OSError):
        # Corrupt or unreadable file -- don't crash the caller's tests
        # over a cosmetic feature. Start fresh.
        return {"xp": 0}


def _save(path: Path, data: Dict[str, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh)


def get_stats(path: Optional[Path] = None) -> Dict[str, int]:
    """
    Return the current XP state without modifying it.

    Keys: 'xp' (total), 'level', 'xp_into_level', 'xp_for_next_level'.
    """
    resolved = Path(path) if path is not None else DEFAULT_XP_PATH
    data = _load(resolved)
    xp = data["xp"]
    return {
        "xp": xp,
        "level": level_for_xp(xp),
        "xp_into_level": _xp_into_current_level(xp),
        "xp_for_next_level": _cost_of_current_level(xp),
    }


def reset_xp(path: Optional[Path] = None) -> None:
    """Reset XP back to zero for the given (or default) tracker file."""
    resolved = Path(path) if path is not None else DEFAULT_XP_PATH
    _save(resolved, {"xp": 0})


def award_xp(points: int, path: Optional[Path] = None) -> Callable[[F], F]:
    """
    Decorator factory. Wrapped function earns ``points`` XP each time
    it's called *and returns without raising*. If a raised exception
    propagates, no XP is awarded (so failing tests don't pay out).

    Parameters
    ----------
    points:
        XP to award per successful call. Must be a positive integer.
    path:
        Optional override for where XP is stored (mainly for tests or
        multiple independent trackers). Defaults to a file in the
        user's home directory shared across all decorated functions.
    """
    if points <= 0:
        raise ValueError("points must be a positive integer")

    resolved_path = Path(path) if path is not None else DEFAULT_XP_PATH

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            data = _load(resolved_path)
            level_before = level_for_xp(data["xp"])

            result = fn(*args, **kwargs)  # let exceptions propagate, no XP

            data["xp"] += points
            _save(resolved_path, data)
            level_after = level_for_xp(data["xp"])

            if level_after > level_before:
                print(
                    f"\N{PARTY POPPER} LEVEL UP! {fn.__name__} pushed you "
                    f"from level {level_before} to level {level_after} "
                    f"({data['xp']} XP total)!"
                )

            return result

        return wrapper  # type: ignore[return-value]

    return decorator


if __name__ == "__main__":
    import tempfile

    demo_path = Path(tempfile.gettempdir()) / "pocketknife_xp_demo.json"
    reset_xp(demo_path)

    @award_xp(60, path=demo_path)
    def test_addition():
        assert 1 + 1 == 2

    @award_xp(60, path=demo_path)
    def test_subtraction():
        assert 5 - 3 == 2

    print("Running a couple of 'tests'...")
    test_addition()
    test_subtraction()
    test_addition()

    print("Stats:", get_stats(demo_path))
    demo_path.unlink(missing_ok=True)
