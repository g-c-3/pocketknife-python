"""
pocketknife.lazy_logger
========================

You don't always want full ``logging`` module ceremony just to see what
a function was called with and what it returned. ``@log_to_file`` is a
one-line decorator that appends a timestamped record of each call --
arguments, return value (or exception) and duration -- to a plain text
file. Good for quick "what actually happened" debugging.

Example
-------
>>> @log_to_file("calls.log")
... def add(a, b):
...     return a + b
>>> add(2, 3)
5
"""

from __future__ import annotations

import functools
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, TypeVar, Union

F = TypeVar("F", bound=Callable[..., Any])


def log_to_file(
    path: Union[str, "Path"],
    *,
    include_result: bool = True,
    include_duration: bool = True,
) -> Callable[[F], F]:
    """Decorator that logs a function's inputs/outputs to a file.

    Each call appends one line to ``path`` (the file and any parent
    directories are created if they don't exist) formatted as::

        2024-01-15T10:30:00.123456 | add(2, 3) -> 5 [0.4ms]

    If the function raises, the log line instead records the exception
    and the exception still propagates normally -- this decorator never
    swallows errors, it just observes.

    Args:
        path: File path to append log lines to. Parent directories are
            created automatically if missing.
        include_result: If True (default), include the return value (or
            raised exception) in the log line. Set to False to log only
            the call signature and timing, e.g. when results are huge
            or sensitive.
        include_duration: If True (default), include how long the call
            took, in milliseconds.

    Returns:
        A decorator that wraps the target function with logging.

    Example:
        >>> @log_to_file("debug.log")
        ... def divide(a, b):
        ...     return a / b
        >>> divide(10, 2)
        5.0
    """
    log_path = Path(path)

    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            log_path.parent.mkdir(parents=True, exist_ok=True)

            arg_parts = [repr(a) for a in args]
            arg_parts.extend(f"{k}={v!r}" for k, v in kwargs.items())
            call_repr = f"{func.__name__}({', '.join(arg_parts)})"

            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
            except Exception as exc:
                duration_ms = (time.perf_counter() - start) * 1000
                line = f"{call_repr} raised {exc.__class__.__name__}: {exc}"
                _write_line(log_path, line, duration_ms, include_duration)
                raise
            else:
                duration_ms = (time.perf_counter() - start) * 1000
                if include_result:
                    line = f"{call_repr} -> {result!r}"
                else:
                    line = call_repr
                _write_line(log_path, line, duration_ms, include_duration)
                return result

        return wrapper  # type: ignore[return-value]

    return decorator


def _write_line(
    log_path: Path, line: str, duration_ms: float, include_duration: bool
) -> None:
    """Append a single formatted log line to the log file."""
    timestamp = datetime.now().isoformat()
    if include_duration:
        line = f"{line} [{duration_ms:.1f}ms]"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"{timestamp} | {line}\n")


if __name__ == "__main__":
    import tempfile

    print("pocketknife.lazy_logger demo\n")

    with tempfile.TemporaryDirectory() as tmp:
        log_file = Path(tmp) / "calls.log"

        @log_to_file(log_file)
        def add(a, b):
            return a + b

        @log_to_file(log_file)
        def divide(a, b):
            return a / b

        print("1. Calling logged functions normally...")
        print(f"   add(2, 3) -> {add(2, 3)}")
        print(f"   add(a=5, b=7) -> {add(a=5, b=7)}")

        print("\n2. A raised exception is logged too, then re-raised:")
        try:
            divide(1, 0)
        except ZeroDivisionError as e:
            print(f"   Caught: {e}")

        print(f"\n3. Contents of {log_file.name}:")
        for line in log_file.read_text().splitlines():
            print(f"   {line}")

    print("\nDemo complete.")
