"""
pocketknife.file_scout
=======================

Hunting through a directory tree for a file whose name you only half
remember shouldn't require a ``find`` one-liner you have to look up
every time. ``find_first`` and ``find_all`` let you search by regex
pattern from Python, with sensible defaults and optional depth limiting.

Example
-------
>>> import tempfile, pathlib
>>> with tempfile.TemporaryDirectory() as tmp:
...     _ = pathlib.Path(tmp, "report_2024.csv").touch()
...     _ = pathlib.Path(tmp, "notes.txt").touch()
...     found = find_first(r"report_.*\\.csv", root=tmp)
...     found.name
'report_2024.csv'
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterator, List, Optional, Union


def find_first(
    pattern: str,
    root: Union[str, Path] = ".",
    *,
    max_depth: Optional[int] = None,
    ignore_hidden: bool = True,
    flags: int = 0,
) -> Optional[Path]:
    """Return the first file whose name matches ``pattern``, or None.

    Walks the directory tree under ``root`` depth-first and returns the
    path to the first file whose *name* (not the full path) matches the
    given regular expression. Returns ``None`` if nothing is found.

    Args:
        pattern: A regular expression matched against the file's name
            (not its full path). The match is partial by default --
            anchor with ``^`` and ``$`` for an exact match.
        root: Directory to search from. Defaults to the current
            working directory.
        max_depth: If given, stops descending past this many directory
            levels below ``root`` (0 means only ``root`` itself, 1
            means ``root`` and its immediate children, etc.).
        ignore_hidden: If True (default), skips files and directories
            whose names start with ``.``.
        flags: Optional ``re`` flags to pass to ``re.search``, e.g.
            ``re.IGNORECASE``.

    Returns:
        A ``pathlib.Path`` pointing to the first match, or ``None``.

    Raises:
        NotADirectoryError: If ``root`` exists but is not a directory.
        FileNotFoundError: If ``root`` does not exist.

    Example:
        >>> find_first(r"\\.py$", root="/tmp")  # doctest: +SKIP
        PosixPath('/tmp/something.py')
    """
    for path in _walk(Path(root), pattern, max_depth, ignore_hidden, flags):
        return path
    return None


def find_all(
    pattern: str,
    root: Union[str, Path] = ".",
    *,
    max_depth: Optional[int] = None,
    ignore_hidden: bool = True,
    flags: int = 0,
) -> List[Path]:
    """Return all files whose names match ``pattern``, sorted by path.

    Like ``find_first`` but collects every match into a list. The list
    is sorted so results are deterministic across platforms.

    Args:
        pattern: A regular expression matched against each file's name.
        root: Directory to search from. Defaults to ``"."``.
        max_depth: Maximum number of directory levels to descend.
        ignore_hidden: If True (default), skips hidden files/dirs.
        flags: Optional ``re`` flags, e.g. ``re.IGNORECASE``.

    Returns:
        A sorted list of ``pathlib.Path`` objects for every matching
        file. Empty list if nothing matches.

    Example:
        >>> find_all(r"\\.log$", root="/var/log")  # doctest: +SKIP
        [PosixPath('/var/log/auth.log'), PosixPath('/var/log/syslog')]
    """
    return sorted(_walk(Path(root), pattern, max_depth, ignore_hidden, flags))


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _walk(
    root: Path,
    pattern: str,
    max_depth: Optional[int],
    ignore_hidden: bool,
    flags: int,
) -> Iterator[Path]:
    """Yield matching files, respecting depth and hidden-file settings."""
    if not root.exists():
        raise FileNotFoundError(f"root directory not found: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"root is not a directory: {root}")

    regex = re.compile(pattern, flags)
    yield from _recurse(root, regex, max_depth, ignore_hidden, current_depth=0)


def _recurse(
    directory: Path,
    regex: re.Pattern,  # type: ignore[type-arg]
    max_depth: Optional[int],
    ignore_hidden: bool,
    current_depth: int,
) -> Iterator[Path]:
    try:
        entries = sorted(directory.iterdir())
    except PermissionError:
        return

    for entry in entries:
        if ignore_hidden and entry.name.startswith("."):
            continue
        if entry.is_file():
            if regex.search(entry.name):
                yield entry
        elif entry.is_dir():
            if max_depth is None or current_depth < max_depth:
                yield from _recurse(
                    entry, regex, max_depth, ignore_hidden, current_depth + 1
                )


if __name__ == "__main__":
    import tempfile

    print("pocketknife.file_scout demo\n")

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        # Build a little tree
        (root / "reports").mkdir()
        (root / "reports" / "q1_2024.csv").touch()
        (root / "reports" / "q2_2024.csv").touch()
        (root / "reports" / "summary.txt").touch()
        (root / "logs").mkdir()
        (root / "logs" / "app.log").touch()
        (root / "logs" / "error.log").touch()
        (root / ".hidden_dir").mkdir()
        (root / ".hidden_dir" / "secret.txt").touch()
        (root / "README.md").touch()

        print("1. find_first: locate any CSV file:")
        hit = find_first(r"\.csv$", root=tmp)
        print(f"   {hit.name if hit else 'not found'}")

        print("\n2. find_all: all log files:")
        logs = find_all(r"\.log$", root=tmp)
        print(f"   {[p.name for p in logs]}")

        print("\n3. find_all: case-insensitive search for 'README':")
        import re as _re
        readmes = find_all(r"readme", root=tmp, flags=_re.IGNORECASE)
        print(f"   {[p.name for p in readmes]}")

        print("\n4. max_depth=0 only looks in root itself:")
        shallow = find_all(r".*", root=tmp, max_depth=0)
        print(f"   {[p.name for p in shallow]}")

        print("\n5. Hidden files/dirs are skipped by default:")
        with_hidden = find_all(r"\.txt$", root=tmp, ignore_hidden=False)
        without_hidden = find_all(r"\.txt$", root=tmp, ignore_hidden=True)
        print(f"   ignore_hidden=False -> {[p.name for p in with_hidden]}")
        print(f"   ignore_hidden=True  -> {[p.name for p in without_hidden]}")

        print("\n6. find_first returns None when nothing matches:")
        miss = find_first(r"\.parquet$", root=tmp)
        print(f"   {miss}")

    print("\nDemo complete.")
