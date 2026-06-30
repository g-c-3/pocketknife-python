"""
pocketknife.env_police
=======================

Stop your app from crashing 40 minutes into a run because someone forgot
to set ``DATABASE_URL``. ``require_env`` checks for missing environment
variables up front and raises a single, clear error listing everything
that's missing -- instead of a vague ``KeyError`` deep in your code.

Example
-------
>>> import os
>>> os.environ["API_KEY"] = "secret"
>>> require_env("API_KEY")
{'API_KEY': 'secret'}

>>> require_env("API_KEY", "MISSING_VAR")
Traceback (most recent call last):
    ...
pocketknife.env_police.MissingEnvError: Missing required environment variable(s): MISSING_VAR
"""

from __future__ import annotations

import os
from typing import Dict, Optional, Sequence


class MissingEnvError(EnvironmentError):
    """Raised when one or more required environment variables are not set.

    Attributes:
        missing: The list of environment variable names that were missing.
    """

    def __init__(self, missing: Sequence[str]) -> None:
        self.missing = list(missing)
        joined = ", ".join(self.missing)
        super().__init__(f"Missing required environment variable(s): {joined}")


def require_env(
    *keys: str,
    allow_empty: bool = False,
    env: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """Ensure the given environment variables exist (and aren't blank).

    Call this at the very start of your script/app -- right after your
    imports -- so missing configuration fails loudly and immediately,
    rather than three function calls deep when you actually try to use it.

    Args:
        *keys: One or more environment variable names that must be set.
        allow_empty: If False (default), a variable that is set but equal
            to the empty string ``""`` is treated as missing. Set to True
            if blank values should be considered valid.
        env: The environment mapping to check. Defaults to ``os.environ``.
            Mainly useful for testing.

    Returns:
        A dict mapping each requested key to its value, for convenience.

    Raises:
        MissingEnvError: If any of the requested keys are absent (or blank,
            when ``allow_empty`` is False). The error message lists every
            missing key at once, not just the first one found.
        ValueError: If no keys are provided at all.

    Example:
        >>> import os
        >>> os.environ["PORT"] = "8000"
        >>> require_env("PORT")
        {'PORT': '8000'}
    """
    if not keys:
        raise ValueError("require_env() needs at least one key to check")

    source = os.environ if env is None else env

    missing = []
    found = {}
    for key in keys:
        value = source.get(key)
        if value is None or (value == "" and not allow_empty):
            missing.append(key)
        else:
            found[key] = value

    if missing:
        raise MissingEnvError(missing)

    return found


if __name__ == "__main__":
    import sys

    print("pocketknife.env_police demo\n")

    # Set up a fake environment for the demo so it's reproducible.
    os.environ["DEMO_API_KEY"] = "sk-demo-12345"
    os.environ["DEMO_EMPTY_VAR"] = ""

    print("1. All required vars present:")
    result = require_env("DEMO_API_KEY")
    print(f"   require_env('DEMO_API_KEY') -> {result}\n")

    print("2. A blank var is treated as missing by default:")
    try:
        require_env("DEMO_EMPTY_VAR")
    except MissingEnvError as e:
        print(f"   Raised MissingEnvError: {e}\n")

    print("   ...unless allow_empty=True:")
    result = require_env("DEMO_EMPTY_VAR", allow_empty=True)
    print(f"   require_env('DEMO_EMPTY_VAR', allow_empty=True) -> {result!r}\n")

    print("3. Missing vars are all reported together, not one at a time:")
    try:
        require_env("DEMO_API_KEY", "DEMO_DB_URL", "DEMO_SECRET")
    except MissingEnvError as e:
        print(f"   Raised MissingEnvError: {e}")
        print(f"   e.missing -> {e.missing}\n")

    print("Demo complete. Exiting 0.")
    sys.exit(0)
