"""
pocketknife.gossip
===================

``dir()`` tells you what an object has. ``help()`` drowns you in it.
``tell_me_about`` is the middle ground: a quick, scannable summary of
an object's type, public attributes, and methods -- with their one-line
docstrings -- formatted as a readable table you can actually glance at
in a terminal or notebook.

Example
-------
>>> tell_me_about([])        # doctest: +SKIP
## list
| Name       | Kind      | Summary                                      |
|------------|-----------|----------------------------------------------|
| append     | method    | Append object to the end of the list.        |
| clear      | method    | Remove all items from list.                  |
| ...        | ...       | ...                                          |
"""

from __future__ import annotations

import inspect
import io
import types
from typing import Any, List, Optional, Tuple


def tell_me_about(
    obj: Any,
    *,
    include_private: bool = False,
    include_dunder: bool = False,
    max_doc_length: int = 72,
    output: Optional[io.TextIOBase] = None,
) -> str:
    """Print (and return) a human-readable summary of any Python object.

    Produces a Markdown-style table of the object's public members --
    attributes and methods -- with their kinds and one-line docstrings.
    Useful as a faster alternative to ``help()`` when you just want to
    know what an unfamiliar object can do.

    Args:
        obj: Any Python object to inspect.
        include_private: If True, include names that start with a single
            underscore (but not double underscore). Defaults to False.
        include_dunder: If True, include dunder (``__name__``) members.
            Defaults to False.
        max_doc_length: Maximum characters for the docstring summary
            column before truncation. Defaults to 72.
        output: File-like object to print to. Defaults to ``sys.stdout``.
            Pass ``io.StringIO()`` to capture output silently.

    Returns:
        The formatted table as a string (also printed to ``output``).

    Example:
        >>> tell_me_about(42)      # doctest: +SKIP
        ## int  (value: 42) ...
    """
    import sys
    writer = output or sys.stdout

    rows = _collect_rows(obj, include_private, include_dunder)
    table = _render(obj, rows, max_doc_length)

    print(table, file=writer)
    return table


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _collect_rows(
    obj: Any,
    include_private: bool,
    include_dunder: bool,
) -> List[Tuple[str, str, str]]:
    """Return (name, kind, docstring_summary) triples for every member."""
    rows: List[Tuple[str, str, str]] = []

    for name in sorted(dir(obj)):
        # Filter by name
        if name.startswith("__"):
            if not include_dunder:
                continue
        elif name.startswith("_"):
            if not include_private:
                continue

        try:
            member = getattr(obj, name)
        except AttributeError:
            continue

        kind = _kind_of(member)
        doc = _first_line(member, name, obj)

        rows.append((name, kind, doc))

    return rows


def _kind_of(member: Any) -> str:
    """Classify a member into a short human-readable category."""
    if inspect.isbuiltin(member) or inspect.isfunction(member):
        return "method"
    if inspect.ismethod(member):
        return "method"
    if isinstance(member, (types.MethodType, types.BuiltinMethodType)):
        return "method"
    if isinstance(member, classmethod):
        return "classmethod"
    if isinstance(member, staticmethod):
        return "staticmethod"
    if isinstance(member, property):
        return "property"
    if inspect.isclass(member):
        return "class"
    if callable(member):
        return "callable"
    return "attribute"


def _first_line(member: Any, name: str, obj: Any) -> str:
    """Extract the first non-empty line of a member's docstring."""
    # Try the member's own __doc__ first
    doc = getattr(member, "__doc__", None)

    # For descriptors on the class side, try the class's version
    if not doc:
        cls = type(obj)
        class_member = getattr(cls, name, None)
        if class_member is not None:
            doc = getattr(class_member, "__doc__", None)

    if not doc:
        return ""

    for line in doc.splitlines():
        line = line.strip()
        if line:
            return line

    return ""


def _render(
    obj: Any,
    rows: List[Tuple[str, str, str]],
    max_doc_length: int,
) -> str:
    """Format the header and table as a Markdown-ish string."""
    lines: List[str] = []

    # Header
    type_name = type(obj).__name__
    module = getattr(type(obj), "__module__", None)
    qualified = f"{module}.{type_name}" if module and module != "builtins" else type_name

    # Show a short value representation for scalars / short objects
    try:
        val_repr = repr(obj)
        value_hint = f"  (value: {val_repr})" if len(val_repr) <= 60 else ""
    except Exception:
        value_hint = ""

    lines.append(f"## {qualified}{value_hint}")
    lines.append("")

    if not rows:
        lines.append("*(no public members)*")
        return "\n".join(lines)

    # Column widths
    col_name = max(len(r[0]) for r in rows)
    col_kind = max(len(r[1]) for r in rows)
    col_doc = min(max((len(r[2]) for r in rows), default=0), max_doc_length)

    col_name = max(col_name, 4)   # "Name"
    col_kind = max(col_kind, 4)   # "Kind"
    col_doc = max(col_doc, 7)     # "Summary"

    def row_line(name: str, kind: str, doc: str) -> str:
        doc_cell = doc if len(doc) <= col_doc else doc[: col_doc - 1] + "…"
        return (
            f"| {name:<{col_name}} "
            f"| {kind:<{col_kind}} "
            f"| {doc_cell:<{col_doc}} |"
        )

    sep_line = (
        f"|-{'-' * col_name}-"
        f"|-{'-' * col_kind}-"
        f"|-{'-' * col_doc}-|"
    )

    lines.append(row_line("Name", "Kind", "Summary"))
    lines.append(sep_line)

    for name, kind, doc in rows:
        lines.append(row_line(name, kind, doc))

    lines.append("")
    lines.append(f"*{len(rows)} member(s) shown*")

    return "\n".join(lines)


if __name__ == "__main__":
    import io

    print("pocketknife.gossip demo\n")

    print("=== tell_me_about([]) ===")
    tell_me_about([])

    print("\n=== tell_me_about(42) ===")
    tell_me_about(42)

    print("\n=== tell_me_about('hello') — first 5 members only for brevity ===")
    buf = io.StringIO()
    tell_me_about("hello", output=buf)
    lines = buf.getvalue().splitlines()
    print("\n".join(lines[:8] + ["... (truncated)"]))

    print("\nDemo complete.")
