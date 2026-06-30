"""
pocketknife.chunker
====================

Splitting an iterable into fixed-size chunks is one of those things
everyone reimplements slightly wrong at least once (off-by-one on the
last chunk, blows up on generators, materializes the whole list first
when it didn't need to...). ``paginate`` does it once, safely, and
works on lists, generators, strings, or anything iterable.

Example
-------
>>> list(paginate([1, 2, 3, 4, 5], 2))
[[1, 2], [3, 4], [5]]
"""

from __future__ import annotations

from itertools import islice
from typing import Any, Iterable, Iterator, List, TypeVar

T = TypeVar("T")


def paginate(iterable: Iterable[T], size: int) -> Iterator[List[T]]:
    """Split any iterable into chunks of at most ``size`` items.

    Works lazily: chunks are produced on demand, so this is safe to use
    on large or infinite generators -- it never materializes more than
    one chunk in memory at a time (aside from whatever you do with the
    input iterable yourself).

    Args:
        iterable: Any iterable -- a list, tuple, generator, file object,
            string, etc.
        size: The maximum number of items per chunk. Must be a positive
            integer. The final chunk may contain fewer than ``size``
            items if the iterable doesn't divide evenly.

    Yields:
        Lists of up to ``size`` items each, in original order, until the
        iterable is exhausted.

    Raises:
        ValueError: If ``size`` is not a positive integer.

    Example:
        >>> list(paginate(range(7), 3))
        [[0, 1, 2], [3, 4, 5], [6]]

        >>> list(paginate("abcdef", 4))
        [['a', 'b', 'c', 'd'], ['e', 'f']]

        >>> list(paginate([], 5))
        []
    """
    if not isinstance(size, int) or size <= 0:
        raise ValueError(f"size must be a positive integer, got {size!r}")

    iterator = iter(iterable)
    while True:
        chunk = list(islice(iterator, size))
        if not chunk:
            return
        yield chunk


if __name__ == "__main__":
    print("pocketknife.chunker demo\n")

    print("1. Basic chunking of a list:")
    numbers = list(range(1, 11))
    for i, chunk in enumerate(paginate(numbers, 3), start=1):
        print(f"   page {i}: {chunk}")

    print("\n2. Works lazily on a generator (no full materialization):")

    def count_up_to(n: int):
        for i in range(n):
            yield i

    for chunk in paginate(count_up_to(5), 2):
        print(f"   chunk: {chunk}")

    print("\n3. Final chunk can be smaller than `size`:")
    print(f"   paginate([1,2,3,4,5], 2) -> {list(paginate([1, 2, 3, 4, 5], 2))}")

    print("\n4. Empty input yields no chunks:")
    print(f"   list(paginate([], 4)) -> {list(paginate([], 4))}")

    print("\n5. Invalid size raises ValueError:")
    try:
        list(paginate([1, 2, 3], 0))
    except ValueError as e:
        print(f"   Raised ValueError: {e}")

    print("\nDemo complete.")
