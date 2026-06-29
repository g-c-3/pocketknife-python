"""
pocketknife.drama
=================
For when your code needs to be more emotionally present.

Functions
---------
dramatic_progress(iterable, ...)  — stressed loading bar with anxiety messages
excuse_generator()                — generates fake but plausible crash log excuses
"""

import sys
import time
import random
import datetime

# ---------------------------------------------------------------------------
# Internal data pools
# ---------------------------------------------------------------------------

_ANXIETY_MESSAGES = [
    "sweating profusely...",
    "questioning all my life choices...",
    "definitely not panicking...",
    "this is fine. everything is fine.",
    "have you tried turning it off and on again?",
    "consulting the ancient scrolls...",
    "silently judging your architecture...",
    "praying to the garbage collector...",
    "hoping nobody looks at the logs...",
    "recalibrating the flux capacitor...",
    "bribing the scheduler...",
    "pretending to know what I'm doing...",
    "asking a rubber duck for help...",
    "ignoring all compiler warnings...",
    "sending thoughts and prayers to the heap...",
    "blaming cosmic rays...",
    "the cloud is just someone else's computer...",
    "technically this is working as intended...",
    "what is a segfault, really?",
    "buffering... existentially...",
]

_EXCUSE_TEMPLATES = [
    "RuntimeError: Quantum state collapsed during {op} — observed too early (Heisenberg, line {line})",
    "MemoryError: All {n}MB of RAM consumed by {culprit}. System has achieved peak bloat.",
    "RecursionError: Stack overflow in {module}.{fn}() — the function called itself to feel something.",
    "OSError: File '{file}' not found. It existed yesterday. We don't talk about yesterday.",
    "TimeoutError: Operation '{op}' exceeded {ms}ms deadline. The server is on island time.",
    "ValueError: Expected {expected!r}, got {actual!r}. One of these is your fault.",
    "KeyError: '{key}' missing from response payload. The API is gaslighting us.",
    "ConnectionResetError: Remote host closed connection during {op}. Ghosted by a server.",
    "PermissionError: Access denied to {file}. Have you tried sudo? (Don't.)",
    "AttributeError: '{obj}' has no attribute '{attr}'. It did in staging. Classic staging.",
    "IndexError: List index {idx} out of range. Off-by-one errors: the gift that keeps giving.",
    "TypeError: unsupported operand type(s) for +: '{t1}' and '{t2}'. JavaScript would have allowed this.",
    "ImportError: Cannot import '{module}'. Did you activate the virtualenv? You didn't, did you.",
    "ZeroDivisionError: Division by zero in {module}.{fn}(). Math has opinions.",
    "AssertionError: {op} returned {actual!r} but we assumed {expected!r}. Assumptions are technical debt.",
]

_EXCUSE_FILLERS = {
    "op": [
        "token refresh", "cache invalidation", "dependency resolution",
        "schema migration", "health check", "feature flag evaluation",
        "telemetry flush", "session hydration", "auth handshake",
    ],
    "culprit": [
        "a single React component", "an unopened PDF", "the favicon",
        "three nested list comprehensions", "one rogue async task",
        "the logging framework", "an empty try/except block",
    ],
    "module": [
        "core.utils", "helpers.base", "services.client",
        "middleware.auth", "db.connection", "tasks.async_runner",
    ],
    "fn": [
        "process", "handle", "resolve", "execute", "dispatch",
        "transform", "validate", "flush", "sync",
    ],
    "file": [
        "config/settings.yaml", ".env.production", "secrets/api_keys.json",
        "cache/session_store.db", "tmp/upload_buffer.bin",
    ],
    "key": [
        "access_token", "user_id", "request_id", "correlation_id",
        "tenant_slug", "feature_flags", "next_cursor",
    ],
    "obj": [
        "NoneType", "response", "payload", "result", "client",
        "session", "context", "manager",
    ],
    "attr": [
        "data", "status_code", "json", "text", "headers",
        "id", "user", "token", "result",
    ],
}


def _fill_excuse(template: str) -> str:
    """Fills a template string with random plausible values."""
    import re

    def replacer(match):
        key = match.group(1).split("!")[0].split(":")[0]  # strip format specs
        pool_key = key if key in _EXCUSE_FILLERS else None
        if pool_key:
            return random.choice(_EXCUSE_FILLERS[pool_key])
        # numeric fillers
        if key == "n":
            return str(random.choice([128, 256, 512, 1024, 2048, 4096]))
        if key == "line":
            return str(random.randint(42, 999))
        if key == "ms":
            return str(random.choice([30000, 60000, 120000, 300000]))
        if key == "idx":
            return str(random.randint(-1, 5))
        if key in ("expected", "actual"):
            samples = ["True", "False", "None", "'ok'", "200", "[]", "{}"]
            return random.choice(samples)
        if key in ("t1", "t2"):
            return random.choice(["int", "str", "NoneType", "list", "dict", "bool"])
        return match.group(0)  # leave unknown placeholders as-is

    # Replace {key} and {key!r} and {key:fmt} patterns
    return re.sub(r"\{(\w+(?:[!:][^}]*)?)}", replacer, template)


# ---------------------------------------------------------------------------
# dramatic_progress
# ---------------------------------------------------------------------------

def dramatic_progress(
    iterable,
    *,
    desc: str = "Processing",
    width: int = 30,
    delay: float = 0.0,
    anxiety_frequency: float = 0.3,
    stream=None,
) -> object:
    """
    Iterate over *iterable* while displaying a stressed, anxiety-ridden
    progress bar in the terminal.

    Unlike calm progress bars, this one mutters existential dread between
    updates and occasionally questions all of its decisions.

    Parameters
    ----------
    iterable : iterable
        The thing to iterate over. Must support ``len()`` or be a ``Sized``
        object. For generators, wrap in a list first or pass ``total=``.
    desc : str, optional
        Label shown to the left of the bar. Default ``"Processing"``.
    width : int, optional
        Character width of the filled bar section. Default ``30``.
    delay : float, optional
        Seconds to sleep between items — useful for demos. Default ``0.0``.
    anxiety_frequency : float, optional
        Probability (0–1) of printing an anxiety message after each item.
        Default ``0.3`` (30% chance per step).
    stream : file-like, optional
        Output stream. Defaults to ``sys.stderr`` so the bar doesn't
        pollute stdout pipelines.

    Yields
    ------
    item
        Each item from *iterable*, unchanged.

    Examples
    --------
    >>> import time
    >>> for item in dramatic_progress(range(5), delay=0.1):
    ...     pass  # do your work here
    """
    if stream is None:
        stream = sys.stderr

    items = list(iterable)
    total = len(items)

    if total == 0:
        stream.write(f"\\r{desc}: nothing to do. Was it something I said?\\n")
        stream.flush()
        return

    for i, item in enumerate(items):
        filled = int(width * (i + 1) / total)
        bar = "█" * filled + "░" * (width - filled)
        pct = int(100 * (i + 1) / total)

        # Stress level: calm early on, peak anxiety in the middle, relief near end
        if pct < 20:
            mood = "🟢"
        elif pct < 50:
            mood = "🟡"
        elif pct < 80:
            mood = "🔴"
        else:
            mood = "✅"

        line = f"\\r{mood} {desc} [{bar}] {pct:3d}%  ({i + 1}/{total})"
        stream.write(line)
        stream.flush()

        if delay:
            time.sleep(delay)

        yield item

        # Random anxiety message on a new line
        if random.random() < anxiety_frequency and i < total - 1:
            msg = random.choice(_ANXIETY_MESSAGES)
            stream.write(f"\\n     💭 {msg}")
            stream.flush()

    stream.write(f"\\n{desc}: done. We survived. Barely.\\n")
    stream.flush()


# ---------------------------------------------------------------------------
# excuse_generator
# ---------------------------------------------------------------------------

def excuse_generator(*, include_timestamp: bool = True, include_traceback: bool = True) -> str:
    """
    Generate a fake but plausible-sounding crash log excuse.

    Perfect for those moments when "it just broke" isn't a satisfying
    explanation for your team, your manager, or yourself.

    Parameters
    ----------
    include_timestamp : bool, optional
        Prepend a realistic-looking ISO timestamp. Default ``True``.
    include_traceback : bool, optional
        Append a fake traceback stack to the excuse. Default ``True``.

    Returns
    -------
    str
        A multi-line string that looks like a real error log entry.

    Examples
    --------
    >>> print(excuse_generator())
    [2024-03-14 09:26:53] CRITICAL — core.utils.process()
    Traceback (most recent call last):
      ...
    RuntimeError: Quantum state collapsed during token refresh ...
    """
    template = random.choice(_EXCUSE_TEMPLATES)
    error_text = _fill_excuse(template)

    # Extract the error type (everything before the first colon)
    error_type = error_text.split(":")[0]

    lines = []

    if include_timestamp:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        module = random.choice(_EXCUSE_FILLERS["module"])
        fn = random.choice(_EXCUSE_FILLERS["fn"])
        lines.append(f"[{ts}] CRITICAL — {module}.{fn}()")

    if include_traceback:
        depth = random.randint(2, 4)
        lines.append("Traceback (most recent call last):")
        fake_files = [
            ("/usr/local/lib/python3.12/site-packages/framework/core.py", random.randint(100, 500)),
            ("/usr/local/lib/python3.12/site-packages/framework/dispatch.py", random.randint(50, 300)),
            ("./src/app/handlers.py", random.randint(20, 150)),
            ("./src/app/utils.py", random.randint(10, 80)),
        ]
        for file_path, lineno in random.sample(fake_files, k=min(depth, len(fake_files))):
            fn_name = random.choice(_EXCUSE_FILLERS["fn"])
            lines.append(f'  File "{file_path}", line {lineno}, in {fn_name}')
            lines.append(f"    raise {error_type}(message)")

    lines.append(error_text)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  pocketknife.drama  —  demo")
    print("=" * 60)

    print("\\n--- dramatic_progress demo ---")
    data = list(range(10))
    results = []
    for x in dramatic_progress(data, desc="Crunching numbers", delay=0.15, anxiety_frequency=0.5):
        results.append(x * 2)

    print(f"Computed: {results[:5]}...")

    print("\\n--- excuse_generator demo (3 excuses) ---")
    for i in range(3):
        print(f"\\n[Excuse #{i + 1}]")
        print(excuse_generator())
        print()
