"""
pocketknife.flatpack
~~~~~~~~~~~~~~~~~~~~

Collapse nested dicts into flat dot-notation keys, and rebuild them again.
Handy for diffing configs, writing to flat stores (env vars, Redis), or just
making deeply-nested structures easier to reason about.

Functions
---------
flatten(d, sep=".")
    Recursively collapses a nested dict into a single-level dict whose keys
    are joined by *sep*.

unflatten(d, sep=".")
    Rebuilds a nested dict from a flat dict whose keys contain *sep*.
"""

from __future__ import annotations

from typing import Any


def flatten(d: dict, sep: str = ".") -> dict:
    """Collapse a nested dict into a single-level dict with compound keys.

    Only ``dict`` values are descended into; lists, tuples, sets, and other
    types are treated as leaf values even if they contain dicts.

    Parameters
    ----------
    d : dict
        The (possibly nested) dict to flatten.
    sep : str
        Separator used to join key segments (default ``"."``).

    Returns
    -------
    dict
        A new flat dict.  The original *d* is never mutated.

    Raises
    ------
    TypeError
        If *d* is not a dict, or if *sep* is not a non-empty string.

    Examples
    --------
    >>> flatten({"a": {"b": {"c": 1}}, "x": 2})
    {'a.b.c': 1, 'x': 2}

    >>> flatten({"a": {"b": 1}, "a.b": 2})  # key collision — last write wins
    {'a.b': 2}

    >>> flatten({"scores": [10, 20]})
    {'scores': [10, 20]}
    """
    if not isinstance(d, dict):
        raise TypeError(f"flatten() expects a dict, got {type(d).__name__!r}")
    if not isinstance(sep, str) or not sep:
        raise TypeError("sep must be a non-empty string")

    result: dict = {}

    def _recurse(current: Any, prefix: str) -> None:
        if isinstance(current, dict):
            if not current:
                # Preserve empty dicts as a leaf value, but only when nested
                # (a top-level empty dict just produces an empty flat dict).
                if prefix:
                    result[prefix] = current
            else:
                for key, value in current.items():
                    new_key = f"{prefix}{sep}{key}" if prefix else str(key)
                    _recurse(value, new_key)
        else:
            result[prefix] = current

    _recurse(d, "")
    return result


def unflatten(d: dict, sep: str = ".") -> dict:
    """Rebuild a nested dict from a flat dict with compound keys.

    This is the inverse of :func:`flatten`.  Keys that do not contain *sep*
    are placed at the top level unchanged.

    Parameters
    ----------
    d : dict
        A flat dict whose keys may contain *sep* as a level delimiter.
    sep : str
        Separator used to split key segments (default ``"."``).

    Returns
    -------
    dict
        A new nested dict.  The original *d* is never mutated.

    Raises
    ------
    TypeError
        If *d* is not a dict, or if *sep* is not a non-empty string.
    ValueError
        If a key segment conflict is detected (e.g. one key treats a value as
        a dict while another treats the same path as a leaf).

    Examples
    --------
    >>> unflatten({"a.b.c": 1, "x": 2})
    {'a': {'b': {'c': 1}}, 'x': 2}

    >>> unflatten({"scores": [10, 20]})
    {'scores': [10, 20]}
    """
    if not isinstance(d, dict):
        raise TypeError(f"unflatten() expects a dict, got {type(d).__name__!r}")
    if not isinstance(sep, str) or not sep:
        raise TypeError("sep must be a non-empty string")

    result: dict = {}

    for compound_key, value in d.items():
        parts = str(compound_key).split(sep)
        node = result
        for i, part in enumerate(parts[:-1]):
            if part not in node:
                node[part] = {}
            elif not isinstance(node[part], dict):
                raise ValueError(
                    f"Key conflict at segment {part!r}: "
                    f"cannot treat existing leaf as a dict "
                    f"(full key: {compound_key!r})"
                )
            node = node[part]
        leaf = parts[-1]
        node[leaf] = value

    return result


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    original = {
        "database": {
            "host": "localhost",
            "port": 5432,
            "credentials": {
                "user": "admin",
                "password": "s3cr3t",
            },
        },
        "feature_flags": {
            "dark_mode": True,
            "beta": False,
        },
        "version": "1.0.0",
    }

    print("Original:")
    print(json.dumps(original, indent=2))

    flat = flatten(original)
    print("\nFlattened:")
    for k, v in flat.items():
        print(f"  {k!r}: {v!r}")

    rebuilt = unflatten(flat)
    print("\nRebuilt:")
    print(json.dumps(rebuilt, indent=2))

    print("\nRound-trip match:", original == rebuilt)

    # Custom separator
    flat_slash = flatten(original, sep="/")
    print("\nFlattened with sep='/':")
    for k, v in flat_slash.items():
        print(f"  {k!r}: {v!r}")
