"""
pocketknife.conspiracy
~~~~~~~~~~~~~~~~~~~~~~
Your variable names know more than they're letting on.

`generate_theory(vars)` takes a list of variable names (or any strings,
really — your code doesn't judge) and weaves them into an unhinged,
Mad-Libs-style conspiracy theory connecting them to the Illuminati. No
network calls, no LLM, just pure procedurally-assembled nonsense from the
standard library.

Usage
-----
    from pocketknife.conspiracy import generate_theory

    print(generate_theory(["user_id", "session_token", "is_admin"]))
    # "Have you ever noticed that 'user_id' and 'is_admin' both appear
    #  in the codebase? That's not a coincidence — that's the Illuminati..."
"""

import random
from typing import List, Sequence


# ---------------------------------------------------------------------------
# Template fragments
# ---------------------------------------------------------------------------

_OPENERS = [
    "Wake up. Have you ever noticed that {a} and {b} both appear in the same codebase?",
    "They don't want you to ask why {a} was named right after {b}.",
    "Connect the dots: {a}... {b}... it's all there if you look closely.",
    "I've been tracing the commit history, and {a} keeps showing up near {b}.",
    "Nobody talks about this, but {a} and {b} share a suspicious number of characters.",
    "Do your own research: search '{a}' and '{b}' together. See what comes up.",
]

_MIDDLES = [
    "That's not a coincidence — that's the Illuminati, hiding in plain sight.",
    "The Illuminati has been encoding messages into variable names since the dawn of Unix.",
    "Big Refactoring doesn't want you to know this, but naming conventions are a control mechanism.",
    "This goes all the way to the top — straight to the original committer, whoever THEY were.",
    "Wake up, sheeple. Snake_case is just camelCase wearing a disguise.",
    "The pattern repeats every {n} lines. That's not random. That's by design.",
]

_CLOSERS = [
    "Stay vigilant. Refactor responsibly.",
    "I'm not saying it's the Illuminati. But I'm also not NOT saying that.",
    "Do your own `git blame`. The truth is in the commit log.",
    "They'll call this 'just a naming convention.' Don't believe them.",
    "Trust no one. Especially not your linter.",
    "The variables remember, even when the documentation doesn't.",
]

_THIRD_VAR_LINES = [
    "And don't even get me started on '{c}'. That one ties it all together.",
    "Oh, and '{c}'? That's the smoking gun right there.",
    "'{c}' is the missing piece. Once you see it, you can't unsee it.",
]


def _pick_two_distinct(vars_list: List[str]) -> tuple:
    """Pick two distinct entries from vars_list (allowing repeats if len==1)."""
    if len(vars_list) == 1:
        return vars_list[0], vars_list[0]
    a, b = random.sample(vars_list, 2)
    return a, b


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_theory(vars: Sequence[str]) -> str:
    """Generate a goofy conspiracy theory linking your variable names together.

    Procedurally assembles an opener, a middle "revelation", and a closer
    from internal template pools, substituting in names from *vars*. Purely
    for fun — no network calls, no AI, no actual implications about your
    codebase's secret loyalties.

    Parameters
    ----------
    vars : Sequence[str]
        A list (or any sequence) of variable names or strings to weave into
        the theory. Must contain at least one element.

    Returns
    -------
    str
        A multi-sentence conspiracy theory as a single string.

    Raises
    ------
    ValueError
        If *vars* is empty.

    Example
    -------
    >>> from pocketknife.conspiracy import generate_theory
    >>> theory = generate_theory(["user_id", "session_token"])
    >>> isinstance(theory, str)
    True
    """
    vars_list = [str(v) for v in vars]
    if not vars_list:
        raise ValueError("generate_theory() requires at least one variable name")

    a, b = _pick_two_distinct(vars_list)

    opener = random.choice(_OPENERS).format(a=a, b=b)
    middle = random.choice(_MIDDLES).format(n=random.choice([3, 7, 13, 23, 42]))
    closer = random.choice(_CLOSERS)

    parts = [opener, middle]

    # If there's a third distinct variable available, work it in for extra
    # unhinged credibility.
    remaining = [v for v in vars_list if v not in (a, b)]
    if remaining:
        c = random.choice(remaining)
        parts.append(random.choice(_THIRD_VAR_LINES).format(c=c))

    parts.append(closer)

    return " ".join(parts)


def generate_theories(vars: Sequence[str], n: int = 3) -> List[str]:
    """Generate *n* independent conspiracy theories from the same variable pool.

    Parameters
    ----------
    vars : Sequence[str]
        A list of variable names or strings to draw from.
    n : int
        Number of theories to generate. Must be a positive integer.

    Returns
    -------
    list of str
        *n* independently generated theories.

    Raises
    ------
    ValueError
        If *vars* is empty or *n* is not a positive integer.

    Example
    -------
    >>> from pocketknife.conspiracy import generate_theories
    >>> theories = generate_theories(["foo", "bar", "baz"], n=2)
    >>> len(theories)
    2
    """
    if not isinstance(n, int) or n <= 0:
        raise ValueError(f"n must be a positive integer, got {n!r}")
    return [generate_theory(vars) for _ in range(n)]


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== pocketknife.conspiracy demo ===\n")

    sample_vars = ["user_id", "session_token", "is_admin", "retry_count", "cache_key"]

    print("1. A single theory from 5 variables:\n")
    print("  ", generate_theory(sample_vars), "\n")

    print("2. A theory from just one variable (edge case):\n")
    print("  ", generate_theory(["temp_buffer"]), "\n")

    print("3. Three independent theories:\n")
    for i, theory in enumerate(generate_theories(sample_vars, n=3), start=1):
        print(f"   Theory {i}: {theory}\n")

    print("Demo complete. The truth is out there, encoded in PascalCase.")
