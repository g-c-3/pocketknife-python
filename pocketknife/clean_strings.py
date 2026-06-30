"""
pocketknife.clean_strings
==========================

User input is a disaster. Copy-pasted text from Word brings smart
quotes and zero-width spaces. Database fields arrive with inconsistent
whitespace. Names come in ALL CAPS or with random   gaps.
``normalize_text`` cleans all of it in one pass, ready for DB
insertion, comparison, or display.

Example
-------
>>> normalize_text("  Hello\\u200b   World\\u2019s  ")
"Hello World's"
>>> normalize_text("HELLO", case="lower")
'hello'
>>> slugify("Hello, World!")
'hello-world'
"""

from __future__ import annotations

import re
import unicodedata
from typing import Optional


# ---------------------------------------------------------------------------
# Unicode character categories we treat as "invisible junk"
# ---------------------------------------------------------------------------
_INVISIBLE_CATEGORIES = frozenset({
    "Cf",   # Format characters (zero-width spaces, soft hyphens, BOM, …)
    "Cc",   # Control characters
    "Cs",   # Surrogate characters
    "Co",   # Private-use characters
})

# Smart / curly quotes → straight ASCII equivalents
_SMART_QUOTES: dict[int, str] = {
    ord("\u2018"): "'",   # left single quotation mark
    ord("\u2019"): "'",   # right single quotation mark / apostrophe
    ord("\u201a"): "'",   # single low-9 quotation mark
    ord("\u201b"): "'",   # single high-reversed-9 quotation mark
    ord("\u201c"): '"',   # left double quotation mark
    ord("\u201d"): '"',   # right double quotation mark
    ord("\u201e"): '"',   # double low-9 quotation mark
    ord("\u201f"): '"',   # double high-reversed-9 quotation mark
    ord("\u2032"): "'",   # prime
    ord("\u2033"): '"',   # double prime
    ord("\u00ab"): '"',   # left-pointing double angle quotation mark
    ord("\u00bb"): '"',   # right-pointing double angle quotation mark
}

# En-dash / em-dash → regular hyphen
_DASHES: dict[int, str] = {
    ord("\u2013"): "-",   # en dash
    ord("\u2014"): "-",   # em dash
    ord("\u2015"): "-",   # horizontal bar
    ord("\u2212"): "-",   # minus sign
}

_REPLACEMENTS = {**_SMART_QUOTES, **_DASHES}


def normalize_text(
    text: str,
    *,
    case: Optional[str] = None,
    strip_accents: bool = False,
    ascii_only: bool = False,
) -> str:
    """Clean a string for DB storage or reliable text comparison.

    Steps applied in order:

    1. Strip invisible / control / format Unicode characters.
    2. Replace smart quotes and typographic dashes with ASCII equivalents.
    3. Collapse all interior whitespace runs to a single space and strip
       leading / trailing whitespace.
    4. Optionally fold case (``"lower"``, ``"upper"``, ``"title"``).
    5. Optionally decompose accented characters and drop the accent marks.
    6. Optionally strip everything that isn't printable ASCII.

    Args:
        text: The string to normalize.
        case: If given, one of ``"lower"``, ``"upper"``, or ``"title"``.
            Applied after cleaning.
        strip_accents: If True, decompose accented characters (e.g. ``é``
            → ``e``) using Unicode NFD normalization. Applied before
            ``ascii_only`` so that accented letters become their ASCII
            base form.
        ascii_only: If True, remove any character outside the printable
            ASCII range (0x20–0x7E) after all other steps.

    Returns:
        The cleaned string. Never raises; always returns a string.

    Raises:
        TypeError: If ``text`` is not a string.
        ValueError: If ``case`` is not one of the accepted values.

    Example:
        >>> normalize_text("  café\\u200b  ")
        'café'
        >>> normalize_text("  café  ", strip_accents=True)
        'cafe'
        >>> normalize_text("  café  ", ascii_only=True)
        'caf'
    """
    if not isinstance(text, str):
        raise TypeError(f"normalize_text expects str, got {type(text).__name__!r}")
    if case is not None and case not in ("lower", "upper", "title"):
        raise ValueError(f"case must be 'lower', 'upper', or 'title', got {case!r}")

    # 1. Strip invisible / control characters.
    # Whitespace (tabs, newlines, etc.) is also technically "Cc" but we
    # keep it so the whitespace-collapse step below can fold it to spaces.
    cleaned = "".join(
        ch for ch in text
        if ch.isspace() or unicodedata.category(ch) not in _INVISIBLE_CATEGORIES
    )

    # 2. Replace smart quotes and typographic dashes
    cleaned = cleaned.translate(_REPLACEMENTS)

    # 3. Collapse whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # 4. Case folding
    if case == "lower":
        cleaned = cleaned.lower()
    elif case == "upper":
        cleaned = cleaned.upper()
    elif case == "title":
        cleaned = cleaned.title()

    # 5. Strip accents (NFD decomposition → drop Mn "Mark, Nonspacing")
    if strip_accents:
        nfd = unicodedata.normalize("NFD", cleaned)
        cleaned = "".join(ch for ch in nfd if unicodedata.category(ch) != "Mn")

    # 6. ASCII-only filter
    if ascii_only:
        cleaned = "".join(ch for ch in cleaned if 0x20 <= ord(ch) <= 0x7E)

    return cleaned


def slugify(
    text: str,
    *,
    separator: str = "-",
    max_length: Optional[int] = None,
) -> str:
    """Convert a string into a URL / filename-safe slug.

    Normalizes the text, strips accents, folds to lower-case, replaces
    runs of non-alphanumeric characters with ``separator``, and trims
    leading / trailing separators.

    Args:
        text: The string to slugify.
        separator: Character(s) to use between words. Defaults to ``"-"``.
        max_length: If given, truncates the result to this many characters
            (truncation happens before stripping trailing separators, so
            the final slug may be slightly shorter).

    Returns:
        A lower-case slug string containing only alphanumeric characters
        and the separator.

    Example:
        >>> slugify("Hello, World!")
        'hello-world'
        >>> slugify("Ça va? Très bien.", separator="_")
        'ca-va-tres-bien'
        >>> slugify("Long title here", max_length=8)
        'long'
    """
    cleaned = normalize_text(text, strip_accents=True, ascii_only=True, case="lower")
    slug = re.sub(r"[^a-z0-9]+", separator, cleaned)
    if max_length is not None:
        slug = slug[:max_length]
    return slug.strip(separator)


if __name__ == "__main__":
    print("pocketknife.clean_strings demo\n")

    dirty = "  Hello\u200b\u200c   World\u2019s \u2014 it\u2019s \u201cgreat\u201d  "
    print(f"1. Basic normalization (invisible chars + smart quotes + whitespace):")
    print(f"   input : {dirty!r}")
    print(f"   output: {normalize_text(dirty)!r}")

    print(f"\n2. Case folding:")
    print(f"   lower : {normalize_text('HELLO WORLD', case='lower')!r}")
    print(f"   upper : {normalize_text('hello world', case='upper')!r}")
    print(f"   title : {normalize_text('hello world', case='title')!r}")

    print(f"\n3. Strip accents:")
    print(f"   normalize_text('café résumé naïve', strip_accents=True)")
    print(f"   -> {normalize_text('café résumé naïve', strip_accents=True)!r}")

    print(f"\n4. ASCII only:")
    print(f"   normalize_text('café', ascii_only=True) -> {normalize_text('café', ascii_only=True)!r}")

    print(f"\n5. slugify:")
    print(f"   slugify('Hello, World!')                 -> {slugify('Hello, World!')!r}")
    print(f"   slugify('Ça va? Très bien.')             -> {slugify('Ça va? Très bien.')!r}")
    print(f"   slugify('My  Blog  Post', separator='_') -> {slugify('My  Blog  Post', separator='_')!r}")
    print(f"   slugify('Long title here', max_length=8) -> {slugify('Long title here', max_length=8)!r}")

    print("\nDemo complete.")
