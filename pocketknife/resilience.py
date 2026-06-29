"""
pocketknife.resilience
~~~~~~~~~~~~~~~~~~~~~~

Utilities for making code that fails… try again, or give up gracefully.

Functions / Decorators
----------------------
stubborn(retries=3, delay=1, backoff=1.0, exceptions=(Exception,))
    Decorator.  Retries the wrapped function up to *retries* times before
    re-raising the last exception.  Optional exponential back-off via
    *backoff* multiplier.

fallback(fn, default, exceptions=(Exception,))
    Calls *fn()* and returns its result.  If *fn* raises any exception in
    *exceptions*, returns *default* instead.
"""

from __future__ import annotations

import functools
import time
from typing import Any, Callable, Tuple, Type


# ---------------------------------------------------------------------------
# @stubborn
# ---------------------------------------------------------------------------

def stubborn(
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 1.0,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
):
    """Decorator — retry a failing function up to *retries* extra times.

    Parameters
    ----------
    retries : int
        Number of *extra* attempts after the first failure (default 3, so up
        to 4 total calls).
    delay : float
        Seconds to wait between attempts (default 1.0).
    backoff : float
        Multiplier applied to *delay* after each failure (default 1.0 — no
        back-off).  Set to e.g. ``2.0`` for exponential back-off.
    exceptions : tuple of exception types
        Only retry on these exception types (default ``(Exception,)``).

    Returns
    -------
    Callable
        The decorated function, which raises the *last* exception if all
        attempts are exhausted.

    Raises
    ------
    TypeError
        If *retries* is not a non-negative integer, or *delay* / *backoff* are
        not non-negative numbers.

    Examples
    --------
    >>> attempt = 0
    >>> @stubborn(retries=2, delay=0)
    ... def flaky():
    ...     global attempt
    ...     attempt += 1
    ...     if attempt < 3:
    ...         raise ValueError("not yet")
    ...     return "ok"
    >>> flaky()
    'ok'
    """
    if not isinstance(retries, int) or retries < 0:
        raise TypeError(f"retries must be a non-negative integer, got {retries!r}")
    if not isinstance(delay, (int, float)) or delay < 0:
        raise TypeError(f"delay must be a non-negative number, got {delay!r}")
    if not isinstance(backoff, (int, float)) or backoff < 1.0:
        raise TypeError(f"backoff must be >= 1.0, got {backoff!r}")
    if not isinstance(exceptions, tuple) or not exceptions:
        raise TypeError("exceptions must be a non-empty tuple of exception types")

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exc: BaseException | None = None
            for attempt in range(retries + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt < retries:
                        if current_delay > 0:
                            time.sleep(current_delay)
                        current_delay *= backoff
            raise last_exc  # type: ignore[misc]
        return wrapper
    return decorator


# ---------------------------------------------------------------------------
# fallback()
# ---------------------------------------------------------------------------

def fallback(
    fn: Callable,
    default: Any,
    exceptions: Tuple[Type[BaseException], ...] = (Exception,),
) -> Any:
    """Call *fn()* and return its result; return *default* on any caught exception.

    Parameters
    ----------
    fn : callable
        A zero-argument callable to attempt.
    default : any
        Value returned if *fn* raises.
    exceptions : tuple of exception types
        Only catch these exception types (default ``(Exception,)``).

    Returns
    -------
    any
        The return value of *fn()*, or *default* if it raised.

    Raises
    ------
    TypeError
        If *fn* is not callable, or *exceptions* is not a non-empty tuple of
        exception types.

    Examples
    --------
    >>> fallback(lambda: int("not-a-number"), default=0)
    0
    >>> fallback(lambda: 42, default=0)
    42
    """
    if not callable(fn):
        raise TypeError(f"fn must be callable, got {type(fn).__name__!r}")
    if not isinstance(exceptions, tuple) or not exceptions:
        raise TypeError("exceptions must be a non-empty tuple of exception types")

    try:
        return fn()
    except exceptions:
        return default


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import random

    print("=" * 60)
    print("@stubborn — flaky function that succeeds on 3rd attempt")
    print("=" * 60)

    call_count = 0

    @stubborn(retries=4, delay=0)
    def unreliable_service():
        global call_count
        call_count += 1
        print(f"  attempt #{call_count}...", end=" ")
        if call_count < 3:
            raise ConnectionError("service unavailable")
        print("success!")
        return {"status": "ok"}

    result = unreliable_service()
    print(f"  Result: {result}")

    print()
    print("=" * 60)
    print("@stubborn — exhausts all retries, re-raises last exception")
    print("=" * 60)

    @stubborn(retries=2, delay=0)
    def always_fails():
        raise RuntimeError("I will never work")

    try:
        always_fails()
    except RuntimeError as e:
        print(f"  Caught after retries: {e!r}")

    print()
    print("=" * 60)
    print("fallback() — graceful default on failure")
    print("=" * 60)

    result = fallback(lambda: int("not-a-number"), default=-1)
    print(f"  int('not-a-number') with fallback → {result}")

    result = fallback(lambda: 2 ** 10, default=-1)
    print(f"  2**10 with fallback             → {result}")

    print()
    print("=" * 60)
    print("@stubborn with exponential back-off (fast demo, tiny delay)")
    print("=" * 60)

    @stubborn(retries=3, delay=0.01, backoff=2.0)
    def eventually():
        if random.random() < 0.7:
            raise TimeoutError("slow response")
        return "got it"

    try:
        print(f"  Result: {eventually()}")
    except TimeoutError:
        print("  All retries exhausted (bad luck — run again!)")
