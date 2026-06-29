"""
pocketknife.inspector
~~~~~~~~~~~~~~~~~~~~~

Lightweight introspection tools for debugging and profiling — no third-party
dependencies, no Rich, no nothing.

Functions
---------
snoop(var, label=None, stream=None)
    Pretty-prints type, value preview, length (if applicable), and memory
    footprint of any Python object.

stopwatch(label="elapsed", stream=None, precision=4)
    Context manager that measures wall-clock time and prints the result on
    exit.
"""

from __future__ import annotations

import sys
import time
from contextlib import contextmanager
from typing import Any, Generator, Optional, TextIO


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _human_bytes(n: int) -> str:
    """Convert a byte count to a human-readable string (e.g. 1.23 KB)."""
    units = ("B", "KB", "MB", "GB", "TB")
    value = float(n)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(value)} B"
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{value:.2f} TB"  # pragma: no cover


def _safe_len(obj: Any) -> Optional[int]:
    """Return len(obj) if the object supports it, else None."""
    try:
        return len(obj)
    except TypeError:
        return None


def _value_preview(obj: Any, max_len: int = 80) -> str:
    """Return a short string preview of *obj*'s value."""
    raw = repr(obj)
    if len(raw) <= max_len:
        return raw
    return raw[:max_len - 3] + "..."


# ---------------------------------------------------------------------------
# snoop()
# ---------------------------------------------------------------------------

def snoop(
    var: Any,
    label: Optional[str] = None,
    stream: Optional[TextIO] = None,
) -> Any:
    """Print a concise diagnostic summary of *var* and return it unchanged.

    Prints (to *stream*, default ``sys.stdout``):

    - Optional label (if supplied)
    - Full qualified type name
    - Memory size (``sys.getsizeof`` — shallow, not recursive)
    - Length (if the object supports ``len()``)
    - Value preview (truncated at 80 chars)

    Parameters
    ----------
    var : any
        The variable to inspect.
    label : str or None
        Optional display name shown as a header (default ``None``).
    stream : file-like or None
        Where to write output (default ``sys.stdout``).

    Returns
    -------
    any
        *var* is returned unchanged, so ``snoop`` can be used inline::

            result = snoop(some_dict)["key"]

    Examples
    --------
    >>> snoop(42, label="answer")           # doctest: +SKIP
    ── answer ──────────────────────────────
    type   : int
    size   : 28 B
    value  : 42
    """
    out = stream or sys.stdout

    type_name = f"{type(var).__module__}.{type(var).__qualname__}"
    if type_name.startswith("builtins."):
        type_name = type(var).__qualname__

    size = sys.getsizeof(var)
    length = _safe_len(var)
    preview = _value_preview(var)

    # Header
    if label:
        header = f"── {label} "
        header += "─" * max(0, 40 - len(header))
    else:
        header = "─" * 40

    lines = [header]
    lines.append(f"type   : {type_name}")
    lines.append(f"size   : {_human_bytes(size)}")
    if length is not None:
        lines.append(f"len    : {length}")
    lines.append(f"value  : {preview}")

    print("\n".join(lines), file=out)
    return var


# ---------------------------------------------------------------------------
# stopwatch()
# ---------------------------------------------------------------------------

@contextmanager
def stopwatch(
    label: str = "elapsed",
    stream: Optional[TextIO] = None,
    precision: int = 4,
) -> Generator[None, None, None]:
    """Context manager — measure wall-clock execution time and print it.

    Prints a single line on exit::

        [label] 0.0123 s

    Parameters
    ----------
    label : str
        Prefix shown in the output line (default ``"elapsed"``).
    stream : file-like or None
        Where to write output (default ``sys.stdout``).
    precision : int
        Decimal places shown for the elapsed time (default 4).

    Yields
    ------
    None

    Raises
    ------
    TypeError
        If *precision* is not a non-negative integer.

    Examples
    --------
    >>> with stopwatch("sort"):   # doctest: +SKIP
    ...     sorted(range(10_000))
    [sort] 0.0007 s
    """
    if not isinstance(precision, int) or precision < 0:
        raise TypeError(f"precision must be a non-negative integer, got {precision!r}")

    out = stream or sys.stdout
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print(f"[{label}] {elapsed:.{precision}f} s", file=out)


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import io

    print("=" * 60)
    print("snoop() — various types")
    print("=" * 60)

    snoop(42, label="an integer")
    print()
    snoop([1, 2, 3, 4, 5], label="a list")
    print()
    snoop({"key": "value", "nested": {"a": 1}}, label="a dict")
    print()
    snoop("Hello, pocketknife! " * 10, label="a long string")
    print()
    snoop(3.14159, label="a float")
    print()
    snoop(None, label="None")
    print()

    # Inline usage
    result = snoop(list(range(100)), label="inline usage")
    assert isinstance(result, list)
    print(f"\n(returned value is the original object: {type(result).__name__})")

    print()
    print("=" * 60)
    print("stopwatch() — timing a tight loop")
    print("=" * 60)

    with stopwatch("sum 1..1M"):
        total = sum(range(1_000_000))
    print(f"  (answer: {total})")

    print()
    with stopwatch("string join", precision=6):
        _ = "-".join(str(i) for i in range(50_000))

    print()
    print("=" * 60)
    print("stopwatch() — exception still prints timing")
    print("=" * 60)

    try:
        with stopwatch("will raise"):
            _ = [i ** 2 for i in range(10_000)]
            raise ValueError("deliberate error")
    except ValueError as e:
        print(f"  Caught: {e!r}")
