"""
pocketknife.safe_math
======================

Arithmetic that doesn't blow up in your face. Division by zero, None
values slipping in from a database, NaN propagating silently through a
pipeline -- these are the kind of boring crashes that safe wrappers
exist to absorb. This module collects the handful of "just give me a
sensible default" math operations you end up writing in every project.

Example
-------
>>> divide(10, 2)
5.0
>>> divide(10, 0)         # no ZeroDivisionError
>>> divide(10, 0, default=-1)
-1
>>> percent(25, 200)
12.5
>>> clamp(150, lo=0, hi=100)
100
"""

from __future__ import annotations

import math
from typing import Optional, Union

_Numeric = Union[int, float]


def divide(
    numerator: _Numeric,
    denominator: _Numeric,
    *,
    default: Optional[_Numeric] = None,
) -> Optional[float]:
    """Divide two numbers, returning ``default`` instead of raising.

    Handles division by zero *and* type errors (e.g. ``None`` slipping
    in from a database row) without crashing the caller.

    Args:
        numerator: The number to divide.
        denominator: The number to divide by.
        default: Value to return when division is impossible (zero
            denominator, non-numeric inputs, or a NaN/Inf result that
            would be meaningless). Defaults to ``None``.

    Returns:
        ``float(numerator) / float(denominator)`` on success, or
        ``default`` if anything goes wrong.

    Example:
        >>> divide(9, 3)
        3.0
        >>> divide(1, 0)        # ZeroDivisionError → default
        >>> divide(1, 0, default=0.0)
        0.0
        >>> divide("x", 2)     # TypeError → default
    """
    try:
        result = float(numerator) / float(denominator)
    except (ZeroDivisionError, TypeError, ValueError):
        return default
    if not math.isfinite(result):
        return default
    return result


def percent(
    part: _Numeric,
    whole: _Numeric,
    *,
    default: Optional[float] = None,
    ndigits: Optional[int] = None,
) -> Optional[float]:
    """Return what percentage ``part`` is of ``whole``.

    Equivalent to ``(part / whole) * 100``, with the same safe-division
    guarantees as ``divide``.

    Args:
        part: The partial value.
        whole: The total value. If zero, ``default`` is returned.
        default: Returned when the percentage cannot be computed.
            Defaults to ``None``.
        ndigits: If given, round the result to this many decimal places.

    Returns:
        A float percentage, or ``default`` on error.

    Example:
        >>> percent(1, 4)
        25.0
        >>> percent(0, 0)
    """
    result = divide(part, whole, default=None)
    if result is None:
        return default
    result = result * 100
    if ndigits is not None:
        result = round(result, ndigits)
    return result


def clamp(
    value: _Numeric,
    *,
    lo: Optional[_Numeric] = None,
    hi: Optional[_Numeric] = None,
) -> _Numeric:
    """Constrain ``value`` to the range [``lo``, ``hi``].

    Either bound can be omitted (``None``) to leave that side open.

    Args:
        value: The number to clamp.
        lo: Lower bound (inclusive). Omit to leave unbounded below.
        hi: Upper bound (inclusive). Omit to leave unbounded above.

    Returns:
        ``value`` clamped to the given range.

    Raises:
        ValueError: If both ``lo`` and ``hi`` are given and ``lo > hi``.

    Example:
        >>> clamp(150, lo=0, hi=100)
        100
        >>> clamp(-5, lo=0)
        0
        >>> clamp(42, lo=0, hi=100)
        42
    """
    if lo is not None and hi is not None and lo > hi:
        raise ValueError(f"lo ({lo!r}) must be <= hi ({hi!r})")
    if lo is not None and value < lo:
        return lo
    if hi is not None and value > hi:
        return hi
    return value


def safe_round(
    value: _Numeric,
    ndigits: int = 0,
    *,
    default: Optional[float] = None,
) -> Optional[float]:
    """Round a number, returning ``default`` on any error.

    A thin safety wrapper around ``round()`` for cases where ``value``
    might be ``None``, a string, or some other non-numeric type that
    slipped through.

    Args:
        value: The number to round.
        ndigits: Decimal places to round to. Defaults to 0 (integer).
        default: Returned on ``TypeError`` or ``ValueError``.

    Returns:
        The rounded float, or ``default`` on error.

    Example:
        >>> safe_round(3.14159, 2)
        3.14
        >>> safe_round(None, 2)
    """
    try:
        return round(float(value), ndigits)
    except (TypeError, ValueError):
        return default


if __name__ == "__main__":
    print("pocketknife.safe_math demo\n")

    print("divide():")
    print(f"  divide(10, 2)              -> {divide(10, 2)}")
    print(f"  divide(10, 0)              -> {divide(10, 0)!r}  (no crash)")
    print(f"  divide(10, 0, default=-1)  -> {divide(10, 0, default=-1)}")
    print(f"  divide('x', 2)             -> {divide('x', 2)!r}  (bad input)")
    print(f"  divide(float('inf'), 1)    -> {divide(float('inf'), 1)!r}  (non-finite)")

    print("\npercent():")
    print(f"  percent(1, 4)              -> {percent(1, 4)}")
    print(f"  percent(25, 200)           -> {percent(25, 200)}")
    print(f"  percent(0, 0)              -> {percent(0, 0)!r}")
    print(f"  percent(1, 3, ndigits=2)   -> {percent(1, 3, ndigits=2)}")

    print("\nclamp():")
    print(f"  clamp(150, lo=0, hi=100)   -> {clamp(150, lo=0, hi=100)}")
    print(f"  clamp(-5, lo=0)            -> {clamp(-5, lo=0)}")
    print(f"  clamp(42, lo=0, hi=100)    -> {clamp(42, lo=0, hi=100)}")

    print("\nsafe_round():")
    print(f"  safe_round(3.14159, 2)     -> {safe_round(3.14159, 2)}")
    print(f"  safe_round(None, 2)        -> {safe_round(None, 2)!r}")
    print(f"  safe_round('bad')          -> {safe_round('bad')!r}")

    print("\nDemo complete.")
