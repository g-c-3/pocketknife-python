"""
pocketknife.diet_pandas
========================

Sometimes you just need to group a list of dicts by a field and you
don't want to ``pip install pandas`` (and wait for numpy to build) just
to avoid writing a five-line loop. ``groupby_key`` is that five-line
loop, packaged up.

Example
-------
>>> records = [
...     {"team": "red", "score": 10},
...     {"team": "blue", "score": 7},
...     {"team": "red", "score": 3},
... ]
>>> groupby_key(records, "team")
{'red': [{'team': 'red', 'score': 10}, {'team': 'red', 'score': 3}], 'blue': [{'team': 'blue', 'score': 7}]}
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, List, Union


def groupby_key(
    records: Iterable[Dict[Any, Any]],
    key: Union[str, Callable[[Dict[Any, Any]], Any]],
    *,
    default: Any = None,
    strict: bool = False,
) -> Dict[Any, List[Dict[Any, Any]]]:
    """Group a list of dicts by a field, without needing Pandas.

    This is the everyday ``df.groupby(key)`` you reach for, minus the
    DataFrame ceremony -- you give it plain dicts, you get plain dicts
    back, grouped by the value at ``key``, in first-seen order.

    Args:
        records: An iterable of dicts (or dict-like records) to group.
        key: Either the field name to group by, or a callable that takes
            a record and returns the group value. Use a callable for
            derived groupings, e.g. ``lambda r: r["score"] // 10``.
        default: The value to use for records missing the field, when
            ``strict`` is False. Defaults to ``None`` (so all "missing
            field" records land in one ``None`` group).
        strict: If True, raise a ``KeyError`` when a record is missing
            the grouping field, instead of falling back to ``default``.
            Has no effect when ``key`` is a callable.

    Returns:
        A dict mapping each distinct group value to the list of records
        in that group, preserving the original record order within each
        group and the order groups were first encountered.

    Raises:
        KeyError: If ``strict`` is True, ``key`` is a string, and a
            record does not contain that field.

    Example:
        >>> records = [{"type": "a", "n": 1}, {"type": "b", "n": 2}, {"type": "a", "n": 3}]
        >>> groupby_key(records, "type")
        {'a': [{'type': 'a', 'n': 1}, {'type': 'a', 'n': 3}], 'b': [{'type': 'b', 'n': 2}]}

        >>> groupby_key(records, lambda r: r["n"] % 2)
        {1: [{'type': 'a', 'n': 1}, {'type': 'a', 'n': 3}], 0: [{'type': 'b', 'n': 2}]}
    """
    groups: Dict[Any, List[Dict[Any, Any]]] = {}

    get_value: Callable[[Dict[Any, Any]], Any]
    if callable(key):
        get_value = key
    else:
        field = key

        def get_value(record: Dict[Any, Any], _field: Any = field) -> Any:
            if strict and _field not in record:
                raise KeyError(
                    f"Record missing grouping field {_field!r}: {record!r}"
                )
            return record.get(_field, default)

    for record in records:
        group_value = get_value(record)
        groups.setdefault(group_value, []).append(record)

    return groups


if __name__ == "__main__":
    print("pocketknife.diet_pandas demo\n")

    orders = [
        {"customer": "alice", "item": "widget", "amount": 25},
        {"customer": "bob", "item": "gadget", "amount": 40},
        {"customer": "alice", "item": "gizmo", "amount": 15},
        {"customer": "carol", "item": "widget", "amount": 25},
        {"customer": "bob", "item": "widget", "amount": 25},
    ]

    print("1. Group orders by customer:")
    by_customer = groupby_key(orders, "customer")
    for customer, customer_orders in by_customer.items():
        total = sum(o["amount"] for o in customer_orders)
        print(f"   {customer}: {len(customer_orders)} order(s), ${total} total")

    print("\n2. Group by a derived key using a callable (spend tier):")

    def spend_tier(record):
        return "big spender" if record["amount"] >= 30 else "regular"

    by_tier = groupby_key(orders, spend_tier)
    for tier, tier_orders in by_tier.items():
        print(f"   {tier}: {[o['customer'] for o in tier_orders]}")

    print("\n3. Records missing the field fall back to `default`:")
    messy = [{"a": 1}, {"b": 2}, {"a": 3}]
    print(f"   groupby_key(messy, 'a') -> {groupby_key(messy, 'a')}")
    print(f"   groupby_key(messy, 'a', default='MISSING') -> "
          f"{groupby_key(messy, 'a', default='MISSING')}")

    print("\n4. strict=True raises on missing fields:")
    try:
        groupby_key(messy, "a", strict=True)
    except KeyError as e:
        print(f"   Raised KeyError: {e}")

    print("\nDemo complete.")
