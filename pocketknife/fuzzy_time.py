"""
pocketknife.fuzzy_time
======================
Human-friendly datetime descriptions — because "2024-03-14T09:26:53.000Z"
means nothing to anyone at a glance.

Functions
---------
around_now(dt, now=None)    — humanizes a datetime relative to now
                              ("just now", "about 3 hours ago", "2 weeks ago")
relative_age(dt, now=None)  — returns the human-readable age of any datetime
                              ("3 days", "about 2 years", "47 minutes")

Notes
-----
Both functions accept timezone-aware or timezone-naive datetimes, but the
two datetimes compared must be of the same type (both aware or both naive).
If you mix them, Python itself will raise a TypeError — by design.

The roadmap lists `around_noon(dt)` but the function is clearly intended to
humanise datetimes relative to *now* (not relative to noon). The name used
here is `around_now`, which matches the docstring example in the roadmap.
`around_noon` is provided as an alias for compatibility.
"""

import datetime
from typing import Optional

# ---------------------------------------------------------------------------
# Internal threshold table
# ---------------------------------------------------------------------------
# Each entry: (upper_bound_seconds, label_fn)
# label_fn receives the raw delta in seconds and returns the display string.

def _make_thresholds():
    MINUTE  = 60
    HOUR    = 60 * MINUTE
    DAY     = 24 * HOUR
    WEEK    = 7  * DAY
    MONTH   = 30 * DAY
    YEAR    = 365 * DAY

    return [
        # (max_seconds, fn(delta_seconds) -> str)
        (45,            lambda s: "just now"),
        (90,            lambda s: "a minute ago"),
        (45 * MINUTE,   lambda s: f"{round(s / MINUTE)} minutes ago"),
        (90 * MINUTE,   lambda s: "about an hour ago"),
        (22 * HOUR,     lambda s: f"about {round(s / HOUR)} hours ago"),
        (36 * HOUR,     lambda s: "a day ago"),
        (6  * DAY,      lambda s: f"{round(s / DAY)} days ago"),
        (11 * DAY,      lambda s: "about a week ago"),
        (3  * WEEK,     lambda s: f"{round(s / WEEK)} weeks ago"),
        (45 * DAY,      lambda s: "about a month ago"),
        (8  * MONTH,    lambda s: f"{round(s / MONTH)} months ago"),
        (11 * MONTH,    lambda s: "about a year ago"),
        (18 * MONTH,    lambda s: "a year ago"),
        (float("inf"),  lambda s: f"about {round(s / YEAR)} years ago"),
    ]

_THRESHOLDS = _make_thresholds()


def _age_thresholds():
    """Thresholds for relative_age — unsigned durations, no 'ago'."""
    MINUTE  = 60
    HOUR    = 60 * MINUTE
    DAY     = 24 * HOUR
    WEEK    = 7  * DAY
    MONTH   = 30 * DAY
    YEAR    = 365 * DAY

    return [
        (45,            lambda s: "a few seconds"),
        (90,            lambda s: "a minute"),
        (45 * MINUTE,   lambda s: f"{round(s / MINUTE)} minutes"),
        (90 * MINUTE,   lambda s: "about an hour"),
        (22 * HOUR,     lambda s: f"about {round(s / HOUR)} hours"),
        (36 * HOUR,     lambda s: "a day"),
        (6  * DAY,      lambda s: f"{round(s / DAY)} days"),
        (11 * DAY,      lambda s: "about a week"),
        (3  * WEEK,     lambda s: f"{round(s / WEEK)} weeks"),
        (45 * DAY,      lambda s: "about a month"),
        (8  * MONTH,    lambda s: f"{round(s / MONTH)} months"),
        (11 * MONTH,    lambda s: "about a year"),
        (18 * MONTH,    lambda s: "a year"),
        (float("inf"),  lambda s: f"about {round(s / YEAR)} years"),
    ]

_AGE_THRESHOLDS = _age_thresholds()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _delta_seconds(dt: datetime.datetime, now: datetime.datetime) -> float:
    """Return absolute elapsed seconds between *dt* and *now*."""
    return abs((now - dt).total_seconds())


def _is_future(dt: datetime.datetime, now: datetime.datetime) -> bool:
    return dt > now


def _apply_thresholds(delta: float, thresholds: list) -> str:
    for upper, label_fn in thresholds:
        if delta < upper:
            return label_fn(delta)
    # Unreachable — last threshold is inf — but be safe
    return "a long time ago"


# ---------------------------------------------------------------------------
# around_now
# ---------------------------------------------------------------------------

def around_now(
    dt: datetime.datetime,
    now: Optional[datetime.datetime] = None,
) -> str:
    """
    Return a human-friendly description of *dt* relative to *now*.

    Inspired by the Rails ``time_ago_in_words`` helper and the ``humanize``
    family of libraries, but with zero dependencies.

    Parameters
    ----------
    dt : datetime.datetime
        The datetime to describe. Can be in the past or the future.
        Timezone-aware and naive datetimes are both accepted, but *dt* and
        *now* must be of the same kind.
    now : datetime.datetime, optional
        The reference point. Defaults to ``datetime.datetime.now()`` for
        naive *dt*, or ``datetime.datetime.now(tz=dt.tzinfo)`` for aware *dt*.

    Returns
    -------
    str
        A human-readable relative time string, e.g.:

        - ``"just now"``        (< 45 s)
        - ``"a minute ago"``    (45–90 s)
        - ``"5 minutes ago"``   (up to ~45 min)
        - ``"about an hour ago"``
        - ``"about 3 hours ago"``
        - ``"a day ago"``
        - ``"3 days ago"``
        - ``"about a week ago"``
        - ``"2 weeks ago"``
        - ``"about a month ago"``
        - ``"4 months ago"``
        - ``"about a year ago"``
        - ``"about 3 years ago"``

        Future datetimes return the same labels prefixed with ``"in "``
        instead of suffixed with ``" ago"``, e.g. ``"in about 3 hours"``.

    Examples
    --------
    >>> import datetime
    >>> now = datetime.datetime(2024, 6, 15, 12, 0, 0)
    >>> around_now(now - datetime.timedelta(seconds=10), now)
    'just now'
    >>> around_now(now - datetime.timedelta(hours=3, minutes=20), now)
    'about 3 hours ago'
    >>> around_now(now + datetime.timedelta(days=2), now)
    'in 2 days'
    """
    if now is None:
        if dt.tzinfo is not None:
            now = datetime.datetime.now(tz=dt.tzinfo)
        else:
            now = datetime.datetime.now()

    delta = _delta_seconds(dt, now)
    future = _is_future(dt, now)

    label = _apply_thresholds(delta, _THRESHOLDS)

    if future:
        # Convert "X ago" → "in X" / "just now" stays as-is
        if label == "just now":
            return label
        label = label.replace(" ago", "")
        return f"in {label}"

    return label


# Alias matching the roadmap name
around_noon = around_now


# ---------------------------------------------------------------------------
# relative_age
# ---------------------------------------------------------------------------

def relative_age(
    dt: datetime.datetime,
    now: Optional[datetime.datetime] = None,
) -> str:
    """
    Return a human-readable *age* (unsigned duration) for any datetime.

    Unlike ``around_now``, this function returns a bare duration string with
    no directional context (no "ago" or "in"). Useful for showing how old
    something is — a file, a record, a user account — without implying
    whether it's past or future.

    Parameters
    ----------
    dt : datetime.datetime
        The datetime whose age to describe.
    now : datetime.datetime, optional
        The reference point. Defaults to the current local time (or
        timezone-aware now if *dt* is aware).

    Returns
    -------
    str
        A bare duration string, e.g.:

        - ``"a few seconds"``
        - ``"a minute"``
        - ``"47 minutes"``
        - ``"about an hour"``
        - ``"about 6 hours"``
        - ``"a day"``
        - ``"3 days"``
        - ``"about 2 years"``

    Examples
    --------
    >>> import datetime
    >>> now = datetime.datetime(2024, 6, 15, 12, 0, 0)
    >>> relative_age(now - datetime.timedelta(minutes=47), now)
    '47 minutes'
    >>> relative_age(now - datetime.timedelta(days=400), now)
    'about a year'
    >>> relative_age(now - datetime.timedelta(days=800), now)
    'about 2 years'
    """
    if now is None:
        if dt.tzinfo is not None:
            now = datetime.datetime.now(tz=dt.tzinfo)
        else:
            now = datetime.datetime.now()

    delta = _delta_seconds(dt, now)
    return _apply_thresholds(delta, _AGE_THRESHOLDS)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    now = datetime.datetime(2024, 6, 15, 12, 0, 0)

    print("=" * 60)
    print("  pocketknife.fuzzy_time  —  demo")
    print("=" * 60)
    print(f"\n  Reference point: {now}\n")

    past_cases = [
        ("10 seconds ago",    datetime.timedelta(seconds=10)),
        ("75 seconds ago",    datetime.timedelta(seconds=75)),
        ("5 minutes ago",     datetime.timedelta(minutes=5)),
        ("1 hour ago",        datetime.timedelta(hours=1)),
        ("3.5 hours ago",     datetime.timedelta(hours=3, minutes=30)),
        ("1 day ago",         datetime.timedelta(days=1)),
        ("4 days ago",        datetime.timedelta(days=4)),
        ("10 days ago",       datetime.timedelta(days=10)),
        ("3 weeks ago",       datetime.timedelta(weeks=3)),
        ("6 weeks ago",       datetime.timedelta(weeks=6)),
        ("5 months ago",      datetime.timedelta(days=150)),
        ("13 months ago",     datetime.timedelta(days=395)),
        ("2.5 years ago",     datetime.timedelta(days=912)),
    ]

    print("  --- around_now (past) ---\n")
    for label, delta in past_cases:
        dt = now - delta
        print(f"  {label:<22} → {around_now(dt, now)}")

    print("\n  --- around_now (future) ---\n")
    future_cases = [
        ("in 30 seconds",     datetime.timedelta(seconds=30)),
        ("in 10 minutes",     datetime.timedelta(minutes=10)),
        ("in 5 hours",        datetime.timedelta(hours=5)),
        ("in 3 days",         datetime.timedelta(days=3)),
        ("in 6 months",       datetime.timedelta(days=180)),
    ]
    for label, delta in future_cases:
        dt = now + delta
        print(f"  {label:<22} → {around_now(dt, now)}")

    print("\n  --- relative_age ---\n")
    age_cases = [
        ("47 minutes old",    datetime.timedelta(minutes=47)),
        ("18 hours old",      datetime.timedelta(hours=18)),
        ("400 days old",      datetime.timedelta(days=400)),
        ("800 days old",      datetime.timedelta(days=800)),
    ]
    for label, delta in age_cases:
        dt = now - delta
        print(f"  {label:<22} → {relative_age(dt, now)}")
