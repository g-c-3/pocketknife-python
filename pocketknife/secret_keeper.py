"""
pocketknife.secret_keeper
==========================

Logging a dict that might contain passwords, tokens, or credit card
numbers is a bad day waiting to happen. ``mask_secrets`` recursively
walks any nested dict (or list of dicts) and replaces the values of
sensitive keys with a redaction placeholder before the data ever
reaches a log line, an API response, or a debug print.

Example
-------
>>> cfg = {"user": "alice", "password": "s3cr3t", "db": {"token": "abc123"}}
>>> mask_secrets(cfg, ["password", "token"])
{'user': 'alice', 'password': '***', 'db': {'token': '***'}}
"""

from __future__ import annotations

import copy
from typing import Any, Collection, Set, Union


_DEFAULT_MASK = "***"

# Commonly sensitive key names -- used when no explicit list is given.
_DEFAULT_SENSITIVE_KEYS: frozenset[str] = frozenset({
    "password", "passwd", "pwd",
    "secret", "secret_key",
    "token", "access_token", "refresh_token", "id_token", "auth_token",
    "api_key", "apikey", "api_secret",
    "private_key", "private_key_id",
    "client_secret",
    "authorization",
    "credit_card", "card_number", "cvv", "ssn",
    "passphrase",
})


def mask_secrets(
    data: Any,
    keys: Union[Collection[str], None] = None,
    *,
    mask: str = _DEFAULT_MASK,
    case_sensitive: bool = False,
    in_place: bool = False,
) -> Any:
    """Recursively redact sensitive values in a nested structure.

    Walks dicts, lists, and tuples. Any dict key whose name appears in
    ``keys`` (after optional case-folding) has its value replaced with
    ``mask``. Everything else is left unchanged.

    Args:
        data: The structure to redact. May be a dict, list, tuple, or
            any scalar. Non-dict / non-list / non-tuple values are
            returned as-is (scalars are trivially safe).
        keys: Collection of key names to redact. If ``None`` (default),
            a built-in list of common sensitive names is used (see
            ``DEFAULT_SENSITIVE_KEYS``).
        mask: The replacement string for redacted values.
            Defaults to ``"***"``.
        case_sensitive: If False (default), key matching ignores case
            so ``"Password"`` and ``"PASSWORD"`` both match ``"password"``.
        in_place: If False (default), the original structure is not
            mutated -- a deep copy is returned. Set to True only when
            you are sure you don't need the originals and want to avoid
            the copy overhead.

    Returns:
        A redacted copy of ``data`` (or ``data`` itself if
        ``in_place=True``).

    Example:
        >>> mask_secrets({"api_key": "sk-123", "name": "alice"})
        {'api_key': '***', 'name': 'alice'}

        >>> mask_secrets([{"password": "x"}, {"password": "y"}])
        [{'password': '***'}, {'password': '***'}]
    """
    sensitive: Set[str]
    if keys is None:
        sensitive = set(_DEFAULT_SENSITIVE_KEYS)
        if not case_sensitive:
            sensitive = {k.lower() for k in sensitive}
    else:
        if case_sensitive:
            sensitive = set(keys)
        else:
            sensitive = {k.lower() for k in keys}

    if not in_place:
        data = copy.deepcopy(data)

    return _redact(data, sensitive, mask, case_sensitive)


def _redact(obj: Any, sensitive: Set[str], mask: str, case_sensitive: bool) -> Any:
    """Recursively redact ``obj`` in-place (after deep-copy if requested)."""
    if isinstance(obj, dict):
        for key in list(obj):
            lookup = key if case_sensitive else (key.lower() if isinstance(key, str) else key)
            if lookup in sensitive:
                obj[key] = mask
            else:
                obj[key] = _redact(obj[key], sensitive, mask, case_sensitive)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            obj[i] = _redact(item, sensitive, mask, case_sensitive)
    elif isinstance(obj, tuple):
        # Tuples are immutable, so we rebuild
        return tuple(_redact(item, sensitive, mask, case_sensitive) for item in obj)
    return obj


#: The built-in set of sensitive key names used when ``keys=None``.
DEFAULT_SENSITIVE_KEYS = frozenset(_DEFAULT_SENSITIVE_KEYS)


if __name__ == "__main__":
    print("pocketknife.secret_keeper demo\n")

    config = {
        "app": "myservice",
        "database": {
            "host": "localhost",
            "port": 5432,
            "password": "super_secret_123",
        },
        "auth": {
            "api_key": "sk-prod-abc123xyz",
            "token": "eyJhbGciOiJIUzI1NiJ9...",
            "scopes": ["read", "write"],
        },
        "debug": True,
    }

    print("1. Mask with default sensitive key list:")
    safe = mask_secrets(config)
    print(f"   password  -> {safe['database']['password']!r}")
    print(f"   api_key   -> {safe['auth']['api_key']!r}")
    print(f"   token     -> {safe['auth']['token']!r}")
    print(f"   host      -> {safe['database']['host']!r}  (untouched)")

    print("\n2. Custom key list:")
    result = mask_secrets({"user": "alice", "ssn": "123-45-6789"}, keys=["ssn"])
    print(f"   {result}")

    print("\n3. Custom mask string:")
    result = mask_secrets({"password": "oops"}, mask="[REDACTED]")
    print(f"   {result}")

    print("\n4. Case-insensitive matching (default):")
    result = mask_secrets({"Password": "oops", "API_KEY": "oops"}, keys=["password", "api_key"])
    print(f"   {result}")

    print("\n5. List of dicts:")
    users = [
        {"name": "alice", "password": "abc"},
        {"name": "bob", "password": "xyz"},
    ]
    print(f"   {mask_secrets(users, keys=['password'])}")

    print("\n6. Original is NOT mutated (in_place=False default):")
    original = {"password": "hunter2"}
    _ = mask_secrets(original)
    print(f"   original still intact: {original}")

    print("\nDemo complete.")
