"""
pocketknife.absurd_units
========================
Unit conversion for people who find SI units too sensible.

All conversions use real, sourced constants — only the units are ridiculous.

Functions
---------
to_bananas(meters)      — converts metres to banana lengths
to_coffees(joules)      — converts energy to cups of coffee
to_jiffies(seconds)     — converts seconds to jiffies (1/100th of a second)

Bonus converters
----------------
to_double_deckers(meters)   — London bus lengths (11.23 m)
to_football_fields(meters)  — American football fields (91.44 m)
to_olympic_pools(liters)    — Olympic swimming pool volumes (2_500_000 L)
to_library_of_congress(bytes) — data in Library of Congress equivalents (~10 TB)
"""

# ---------------------------------------------------------------------------
# Constants (all sourced from real measurements)
# ---------------------------------------------------------------------------

# Average Cavendish banana length: ~18 cm (0.1778 m is often cited)
_BANANA_LENGTH_M = 0.1778

# Energy in one 250 mL cup of brewed coffee:
# ~95 kcal typical → 95 * 4184 J = 397,480 J
# We use the more commonly cited 95 kcal figure.
_COFFEE_JOULES = 95 * 4184  # ≈ 397,480 J

# A jiffy: 1/100th of a second in computing contexts (also used in chemistry
# as the time for light to travel 1 cm, but the computing definition is more
# fun and widely understood).
_JIFFY_SECONDS = 1 / 100  # 0.01 s

# London double-decker bus (Routemaster / New Routemaster): 11.23 m
_DOUBLE_DECKER_M = 11.23

# American football field (end zone to end zone): 100 yards = 91.44 m
_FOOTBALL_FIELD_M = 91.44

# Olympic swimming pool volume: 50m × 25m × 2m = 2,500,000 litres
_OLYMPIC_POOL_L = 2_500_000

# Library of Congress (print collections, digital estimate): ~10 terabytes
_LOC_BYTES = 10 * 1024 ** 4  # 10 TiB


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fmt(value: float, unit: str, precision: int = 4) -> str:
    """Return a tidy human-readable string like '3.1416 bananas'."""
    rounded = round(value, precision)
    # Strip trailing zeros after the decimal point for clean output
    formatted = f"{rounded:,.{precision}f}".rstrip("0").rstrip(".")
    return f"{formatted} {unit}"


# ---------------------------------------------------------------------------
# Core converters
# ---------------------------------------------------------------------------

def to_bananas(meters: float, *, pretty: bool = False) -> float | str:
    """
    Convert a distance in metres to banana lengths.

    Uses the average length of a Cavendish banana: **17.78 cm** (0.1778 m),
    which is the world's most-eaten banana variety and the de-facto standard
    for informal length measurement on the internet.

    Parameters
    ----------
    meters : float
        Distance in metres. Negative values are accepted (negative bananas
        are a philosophical problem, not a technical one).
    pretty : bool, optional
        If ``True``, return a formatted string like ``"5.618 bananas"``
        instead of a raw float. Default ``False``.

    Returns
    -------
    float or str
        Number of bananas, or a formatted string if *pretty* is ``True``.

    Examples
    --------
    >>> to_bananas(1)
    5.6243...
    >>> to_bananas(1, pretty=True)
    '5.6243 bananas'
    >>> to_bananas(8849)         # Mount Everest in bananas
    49769...
    """
    result = meters / _BANANA_LENGTH_M
    return _fmt(result, "bananas") if pretty else result


def to_coffees(joules: float, *, pretty: bool = False) -> float | str:
    """
    Convert energy in joules to cups of brewed coffee.

    One 250 mL cup of brewed coffee contains approximately **95 kcal**
    (397,480 J). This is the metabolisable energy, not the heat energy —
    so yes, you'd need a lot of cups to fuel a rocket.

    Parameters
    ----------
    joules : float
        Energy in joules.
    pretty : bool, optional
        If ``True``, return a formatted string like ``"2.513 cups of coffee"``.
        Default ``False``.

    Returns
    -------
    float or str
        Number of cups of coffee equivalent, or a formatted string.

    Examples
    --------
    >>> to_coffees(397480)       # approximately 1 cup
    1.0...
    >>> to_coffees(4.184e6, pretty=True)   # 1 megajoule
    '10.5294 cups of coffee'
    >>> to_coffees(8.988e16)     # E = mc² for 1 gram of matter
    226,193,180,... cups of coffee
    """
    result = joules / _COFFEE_JOULES
    return _fmt(result, "cups of coffee") if pretty else result


def to_jiffies(seconds: float, *, pretty: bool = False) -> float | str:
    """
    Convert a duration in seconds to jiffies.

    In computing, a **jiffy** is 1/100th of a second (10 ms) — the
    traditional tick interval of the Linux kernel scheduler. Not to be
    confused with the chemistry jiffy (time for light to travel 1 cm,
    ≈ 33.4 ps), which is far less satisfying to say out loud.

    Parameters
    ----------
    seconds : float
        Duration in seconds.
    pretty : bool, optional
        If ``True``, return a formatted string like ``"42 jiffies"``.
        Default ``False``.

    Returns
    -------
    float or str
        Number of jiffies, or a formatted string.

    Examples
    --------
    >>> to_jiffies(1)
    100.0
    >>> to_jiffies(0.01, pretty=True)
    '1 jiffies'
    >>> to_jiffies(3600, pretty=True)   # one hour
    '360,000 jiffies'
    """
    result = seconds / _JIFFY_SECONDS
    return _fmt(result, "jiffies") if pretty else result


# ---------------------------------------------------------------------------
# Bonus converters
# ---------------------------------------------------------------------------

def to_double_deckers(meters: float, *, pretty: bool = False) -> float | str:
    """
    Convert metres to London double-decker bus lengths (11.23 m each).

    Parameters
    ----------
    meters : float
        Distance in metres.
    pretty : bool, optional
        Return a formatted string if ``True``. Default ``False``.

    Returns
    -------
    float or str

    Examples
    --------
    >>> to_double_deckers(1000, pretty=True)
    '89.0472 double-decker buses'
    """
    result = meters / _DOUBLE_DECKER_M
    return _fmt(result, "double-decker buses") if pretty else result


def to_football_fields(meters: float, *, pretty: bool = False) -> float | str:
    """
    Convert metres to American football field lengths (91.44 m each).

    Parameters
    ----------
    meters : float
        Distance in metres.
    pretty : bool, optional
        Return a formatted string if ``True``. Default ``False``.

    Returns
    -------
    float or str

    Examples
    --------
    >>> to_football_fields(1000, pretty=True)
    '10.9361 football fields'
    """
    result = meters / _FOOTBALL_FIELD_M
    return _fmt(result, "football fields") if pretty else result


def to_olympic_pools(liters: float, *, pretty: bool = False) -> float | str:
    """
    Convert a volume in litres to Olympic swimming pools (2,500,000 L each).

    Parameters
    ----------
    liters : float
        Volume in litres.
    pretty : bool, optional
        Return a formatted string if ``True``. Default ``False``.

    Returns
    -------
    float or str

    Examples
    --------
    >>> to_olympic_pools(5_000_000, pretty=True)
    '2 Olympic swimming pools'
    """
    result = liters / _OLYMPIC_POOL_L
    return _fmt(result, "Olympic swimming pools") if pretty else result


def to_library_of_congress(bytes_: float, *, pretty: bool = False) -> float | str:
    """
    Convert a data size in bytes to Library of Congress equivalents (~10 TiB).

    The Library of Congress digital estimate is commonly cited as ~10 terabytes
    of text data. This is a rough figure, but the LoC itself has used it.

    Parameters
    ----------
    bytes_ : float
        Data size in bytes.
    pretty : bool, optional
        Return a formatted string if ``True``. Default ``False``.

    Returns
    -------
    float or str

    Examples
    --------
    >>> to_library_of_congress(10 * 1024**4, pretty=True)
    '1 Libraries of Congress'
    """
    result = bytes_ / _LOC_BYTES
    return _fmt(result, "Libraries of Congress") if pretty else result


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("  pocketknife.absurd_units  —  demo")
    print("=" * 60)

    examples = [
        ("Mount Everest (8,849 m)", "bananas",
         to_bananas(8849, pretty=True)),
        ("Marathon (42,195 m)", "double-deckers",
         to_double_deckers(42195, pretty=True)),
        ("Moon distance (384,400,000 m)", "football fields",
         to_football_fields(384_400_000, pretty=True)),
        ("1 megajoule", "cups of coffee",
         to_coffees(1_000_000, pretty=True)),
        ("Human lifespan (2.5 billion s)", "jiffies",
         to_jiffies(2_500_000_000, pretty=True)),
        ("Atlantic Ocean (3.1×10²⁰ L)", "Olympic pools",
         to_olympic_pools(3.1e20, pretty=True)),
        ("1 terabyte of data", "Libraries of Congress",
         to_library_of_congress(1024**4, pretty=True)),
    ]

    print()
    for label, _, result in examples:
        print(f"  {label}")
        print(f"    → {result}")
        print()
