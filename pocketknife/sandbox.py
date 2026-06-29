"""
pocketknife.sandbox
~~~~~~~~~~~~~~~~~~~

A context manager that creates a temporary directory, yields it as a
``pathlib.Path``, and cleans it up on exit — even if an exception is raised.

Functions
---------
temp_workspace(prefix="pocketknife-", suffix="", keep_on_error=False, seed=None)
    Context manager.  Yields a ``pathlib.Path`` pointing at a freshly-created
    temporary directory.  Deletes the directory (and all contents) on exit
    unless *keep_on_error* is ``True`` and the block raised an exception.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, Generator, Optional, Union


@contextmanager
def temp_workspace(
    prefix: str = "pocketknife-",
    suffix: str = "",
    keep_on_error: bool = False,
    seed: Optional[Dict[str, Union[str, bytes]]] = None,
) -> Generator[Path, None, None]:
    """Create a temporary directory, yield it as a ``Path``, then delete it.

    Parameters
    ----------
    prefix : str
        Prefix for the temporary directory name (default ``"pocketknife-"``).
    suffix : str
        Suffix for the temporary directory name (default ``""``).
    keep_on_error : bool
        If ``True``, the directory is *not* deleted when the ``with`` block
        raises an exception — useful for post-mortem inspection (default
        ``False``).
    seed : dict or None
        Optional mapping of ``{relative_path: content}`` to pre-populate the
        workspace before yielding.  Keys are relative path strings; values are
        either ``str`` (written as UTF-8 text) or ``bytes`` (written as-is).
        Intermediate directories are created automatically.

    Yields
    ------
    pathlib.Path
        Absolute path to the temporary directory.

    Raises
    ------
    TypeError
        If *seed* is not a dict (or ``None``), or if a seed value is neither
        ``str`` nor ``bytes``.

    Examples
    --------
    >>> import os
    >>> with temp_workspace() as ws:
    ...     (ws / "hello.txt").write_text("hi")
    ...     files = os.listdir(ws)
    >>> # directory is gone after the block
    >>> import os, pathlib
    >>> os.path.exists(ws)
    False

    Seed a workspace with starter files::

        with temp_workspace(seed={"config.json": '{"debug": true}'}) as ws:
            data = (ws / "config.json").read_text()
    """
    if seed is not None:
        if not isinstance(seed, dict):
            raise TypeError(f"seed must be a dict or None, got {type(seed).__name__!r}")
        for key, value in seed.items():
            if not isinstance(value, (str, bytes)):
                raise TypeError(
                    f"seed values must be str or bytes; "
                    f"got {type(value).__name__!r} for key {key!r}"
                )

    tmpdir = tempfile.mkdtemp(prefix=prefix, suffix=suffix)
    workspace = Path(tmpdir).resolve()

    # Pre-populate if requested
    if seed:
        for rel_path, content in seed.items():
            target = workspace / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, bytes):
                target.write_bytes(content)
            else:
                target.write_text(content, encoding="utf-8")

    error_occurred = False
    try:
        yield workspace
    except BaseException:
        error_occurred = True
        raise
    finally:
        should_delete = not (keep_on_error and error_occurred)
        if should_delete and workspace.exists():
            shutil.rmtree(workspace, ignore_errors=True)


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    print("=" * 60)
    print("Basic temp_workspace — write a file, read it back")
    print("=" * 60)

    with temp_workspace() as ws:
        print(f"  Workspace: {ws}")
        print(f"  Exists:    {ws.exists()}")

        # Create some files
        (ws / "notes.txt").write_text("temporary thoughts")
        subdir = ws / "data"
        subdir.mkdir()
        (subdir / "results.json").write_text(json.dumps({"score": 99}))

        files = list(ws.rglob("*"))
        print(f"  Files:     {[str(f.relative_to(ws)) for f in files]}")

    print(f"  After exit, exists: {ws.exists()}")

    print()
    print("=" * 60)
    print("Seeded workspace — pre-populated with starter files")
    print("=" * 60)

    seed_files = {
        "config.json": '{"debug": true, "version": 3}',
        "subdir/data.csv": "name,score\nalice,95\nbob,87\n",
        "binary/blob.bin": b"\x00\x01\x02\x03",
    }

    with temp_workspace(prefix="seeded-", seed=seed_files) as ws:
        print(f"  Workspace: {ws}")
        for path in sorted(ws.rglob("*")):
            if path.is_file():
                print(f"  {path.relative_to(ws)}")

    print(f"  After exit, exists: {ws.exists()}")

    print()
    print("=" * 60)
    print("keep_on_error=True — directory survives an exception")
    print("=" * 60)

    survivor = None
    try:
        with temp_workspace(keep_on_error=True) as ws:
            survivor = ws
            (ws / "evidence.txt").write_text("the crime scene")
            raise RuntimeError("something went wrong")
    except RuntimeError:
        pass

    print(f"  Workspace still exists: {survivor.exists()}")
    if survivor and survivor.exists():
        print(f"  Contents: {list(survivor.iterdir())}")
        shutil.rmtree(survivor)  # manual cleanup for demo
        print(f"  Cleaned up manually: {survivor.exists()}")
