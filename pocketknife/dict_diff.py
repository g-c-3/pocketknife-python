"""
pocketknife.dict_diff
======================

When two configs, API responses, or JSON blobs diverge and you want to
know *exactly* what changed -- not just that they're not equal -- 
``compare`` gives you a tidy breakdown of added, removed, and modified
keys between two dicts, with before/after values for everything that
moved.

Example
-------
>>> a = {"x": 1, "y": 2, "z": 3}
>>> b = {"x": 1, "y": 99, "w": 4}
>>> compare(a, b)
{'added': {'w': 4}, 'removed': {'z': 3}, 'modified': {'y': {'before': 2, 'after': 99}}}
"""

from __future__ import annotations

from typing import Any, Dict, Set


def compare(
    a: Dict[Any, Any],
    b: Dict[Any, Any],
    *,
    recursive: bool = False,
) -> Dict[str, Any]:
    """Return the diff between two dicts as added, removed, and modified keys.

    Args:
        a: The "before" dict.
        b: The "after" dict.
        recursive: If True, values that are themselves dicts are diffed
            recursively rather than compared as opaque blobs. The
            ``modified`` entry for such a key will be a nested diff dict
            instead of a ``{"before": ..., "after": ...}`` pair. Keys
            that change *type* (e.g. dict → str) are still treated as a
            plain modification.

    Returns:
        A dict with up to three keys -- only non-empty buckets are
        included:

        - ``"added"``   — keys in ``b`` but not in ``a``, with their new values.
        - ``"removed"`` — keys in ``a`` but not in ``b``, with their old values.
        - ``"modified"`` — keys in both but with different values. Each entry
          is ``{"before": old_value, "after": new_value}`` unless
          ``recursive=True`` and both values are dicts, in which case the
          entry is itself a nested diff dict.

    Example:
        >>> compare({"a": 1, "b": 2}, {"b": 3, "c": 4})
        {'added': {'c': 4}, 'removed': {'a': 1}, 'modified': {'b': {'before': 2, 'after': 3}}}

        >>> compare({}, {})
        {}

        >>> compare({"x": 1}, {"x": 1})
        {}
    """
    keys_a: Set[Any] = set(a)
    keys_b: Set[Any] = set(b)

    added = {k: b[k] for k in keys_b - keys_a}
    removed = {k: a[k] for k in keys_a - keys_b}

    modified: Dict[Any, Any] = {}
    for k in keys_a & keys_b:
        val_a, val_b = a[k], b[k]
        if val_a == val_b:
            continue
        if recursive and isinstance(val_a, dict) and isinstance(val_b, dict):
            nested = compare(val_a, val_b, recursive=True)
            if nested:
                modified[k] = nested
        else:
            modified[k] = {"before": val_a, "after": val_b}

    result: Dict[str, Any] = {}
    if added:
        result["added"] = added
    if removed:
        result["removed"] = removed
    if modified:
        result["modified"] = modified
    return result


if __name__ == "__main__":
    print("pocketknife.dict_diff demo\n")

    config_v1 = {
        "host": "localhost",
        "port": 5432,
        "debug": True,
        "timeout": 30,
    }
    config_v2 = {
        "host": "prod.db.example.com",
        "port": 5432,
        "debug": False,
        "max_connections": 100,
    }

    print("1. Basic diff between two configs:")
    diff = compare(config_v1, config_v2)
    print(f"   added:    {diff.get('added')}")
    print(f"   removed:  {diff.get('removed')}")
    print(f"   modified: {diff.get('modified')}")

    print("\n2. Identical dicts return an empty dict (no noise):")
    print(f"   compare(config_v1, config_v1) -> {compare(config_v1, config_v1)}")

    print("\n3. Recursive diff on nested configs:")
    nested_a = {
        "db": {"host": "localhost", "port": 5432},
        "app": {"name": "myapp", "version": "1.0"},
    }
    nested_b = {
        "db": {"host": "prod.example.com", "port": 5432},
        "app": {"name": "myapp", "version": "2.0"},
    }
    diff_nested = compare(nested_a, nested_b, recursive=True)
    print(f"   {diff_nested}")

    print("\nDemo complete.")
