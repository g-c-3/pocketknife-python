"""
pocketknife.snark
~~~~~~~~~~~~~~~~~~
type() but it judges you.

`judge_type(x)` tells you the type of *x*, same as the builtin, but adds
commentary tailored to what you actually handed it — empty containers,
None, suspiciously large numbers, deeply nested structures, and so on.
Pure passive-aggression, zero functional difference from `type()`.

Usage
-----
    from pocketknife.snark import judge_type

    judge_type([])
    # "list. An empty one. Bold choice, very minimalist."

    judge_type(None)
    # "NoneType. The absence of a value, and possibly of a plan."
"""

from typing import Any


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _comment_for(x: Any) -> str:
    """Return a passive-aggressive comment string for the given value."""

    # None
    if x is None:
        return "The absence of a value, and possibly of a plan."

    # Booleans (must check before int, since bool is an int subclass)
    if isinstance(x, bool):
        return "True or False. How refreshingly binary of you." if x else \
               "False. Pessimistic, but at least it's decisive."

    # Numbers
    if isinstance(x, int):
        if x == 0:
            return "Zero. Nothing. Nada. Impressive, in a way."
        if x < 0:
            return "Negative. Going backwards already, I see."
        if x > 1_000_000:
            return "That's a big number. Compensating for something?"
        return "A perfectly ordinary integer. No notes."

    if isinstance(x, float):
        if x != x:  # NaN check without importing math
            return "NaN. Not even a number knows what this is."
        if x == 0.0:
            return "Zero, but fancier. Did you need the decimal point?"
        return "A float. Precision you'll almost certainly lose somewhere."

    # Strings
    if isinstance(x, str):
        if x == "":
            return "An empty string. Truly the bare minimum effort."
        if x.isupper() and len(x) > 1:
            return "ALL CAPS. We can hear you just fine, you know."
        if x.strip() != x:
            return "A string with stray whitespace. Did you mean to do that?"
        return "A perfectly normal string. Nothing to see here."

    # Containers — empty checks first
    if isinstance(x, list):
        if len(x) == 0:
            return "An empty one. Bold choice, very minimalist."
        if len(x) > 1000:
            return f"A list with {len(x)} items. Ever heard of pagination?"
        if any(isinstance(i, list) for i in x):
            return "A list of lists. Very enterprise of you."
        return "A perfectly reasonable list."

    if isinstance(x, dict):
        if len(x) == 0:
            return "An empty dict. So much potential, so little follow-through."
        return "A dict. At least you're organized about your chaos."

    if isinstance(x, tuple):
        if len(x) == 0:
            return "An empty tuple. Immutable AND empty — peak commitment to nothing."
        return "A tuple. Choosing immutability is very 'looking out for future you' of you."

    if isinstance(x, set):
        if len(x) == 0:
            return "An empty set. Mathematically valid. Emotionally bleak."
        return "A set. No duplicates allowed — very strict household."

    # Functions and callables
    if callable(x):
        return "Something callable. I won't ask what it does. I'm scared to know."

    # Fallback for anything else
    return "An object of indeterminate purpose. We're all just guessing at this point."


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def judge_type(x: Any) -> str:
    """Return the type of *x*, with passive-aggressive commentary attached.

    Functionally a drop-in replacement for asking "what type is this," but
    emotionally a much more judgmental experience. Never raises — every
    Python value gets *some* comment, even if it's just a vague shrug.

    Parameters
    ----------
    x : Any
        The value to judge.

    Returns
    -------
    str
        A string in the form ``"<type_name>. <commentary>"``.

    Example
    -------
    >>> from pocketknife.snark import judge_type
    >>> judge_type([])
    'list. An empty one. Bold choice, very minimalist.'
    >>> judge_type(None)
    'NoneType. The absence of a value, and possibly of a plan.'
    """
    type_name = type(x).__name__
    comment = _comment_for(x)
    return f"{type_name}. {comment}"


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== pocketknife.snark demo ===\n")

    samples = [
        None,
        True,
        False,
        0,
        -5,
        2_000_000,
        42,
        0.0,
        float("nan"),
        3.14159,
        "",
        "HELLO",
        "  padded  ",
        "normal string",
        [],
        [1, 2, 3],
        [[1, 2], [3, 4]],
        list(range(2000)),
        {},
        {"key": "value"},
        (),
        (1, 2),
        set(),
        {1, 2, 3},
        print,
    ]

    for sample in samples:
        label = repr(sample) if not callable(sample) else "print"
        if isinstance(sample, list) and len(sample) > 10:
            label = f"<list of {len(sample)} items>"
        print(f"judge_type({label}):")
        print(f"   {judge_type(sample)}\n")

    print("Demo complete. Hope your self-esteem survived.")
