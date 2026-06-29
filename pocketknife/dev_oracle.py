"""
pocketknife.dev_oracle
======================
Consult the Oracle before making decisions you'll regret on Monday.

Functions
---------
should_i_deploy(dt=None)    — blesses or curses your deploy based on day/time
code_review_roulette()      — returns a random passive-aggressive PR comment
"""

import random
import datetime

# ---------------------------------------------------------------------------
# should_i_deploy — thresholds
# ---------------------------------------------------------------------------

# "Friday afternoon" starts at this hour (24h clock, local time)
_FRIDAY_DANGER_HOUR = 13  # 1 PM Friday onwards is cursed

# Days of the week (Monday=0, Sunday=6)
_FRIDAY = 4
_SATURDAY = 5
_SUNDAY = 6
_MONDAY = 0

# ---------------------------------------------------------------------------
# Deploy verdicts
# ---------------------------------------------------------------------------

_BLESSED_VERDICTS = [
    "✅ Green light. The stars are aligned. Deploy with confidence.",
    "✅ All omens point to YES. Ship it.",
    "✅ The Oracle sees clear skies. Proceed.",
    "✅ Tuesday morning energy detected. You may deploy.",
    "✅ No Friday vibes. The pipeline gods are with you.",
    "✅ Conditions nominal. Deploy and go touch some grass.",
    "✅ The diff is small, the hour is right. You have the Oracle's blessing.",
    "✅ Deploy. The on-call engineer is well-rested and caffeinated.",
]

_CURSED_VERDICTS = [
    "🚨 FRIDAY AFTERNOON DETECTED. Step away from the keyboard.",
    "🚨 The Oracle weeps. It is Friday. Go home.",
    "🚨 Deploying on Friday afternoon? Bold. Catastrophically bold.",
    "🚨 The last person who deployed on a Friday afternoon is still rotating their on-call schedule. Don't be them.",
    "🚨 No. Absolutely not. It's Friday PM. The Oracle refuses.",
    "🚨 Your rollback plan is 'hope'. Reconsider.",
    "🚨 The pipeline gods are laughing. It's Friday afternoon.",
    "🚨 ABORT. The Oracle has spoken. Touch no production systems until Monday.",
]

_WEEKEND_VERDICTS = [
    "😬 It's the weekend. Why are you here? Please go outside.",
    "😬 Weekend deploy detected. The Oracle is concerned about your work-life balance.",
    "😬 Who hurt you? It's the weekend. Close the laptop.",
    "😬 The Oracle refuses to answer on weekends. Talk to your therapist instead.",
    "😬 Deploying on a weekend? The on-call rotation has a long memory.",
]

_MONDAY_VERDICTS = [
    "⚠️  It's Monday. The team is still waking up. Maybe wait an hour?",
    "⚠️  Monday morning deploy. Brave. The standup gods are watching.",
    "⚠️  Early Monday is risky — the incident channel is barely staffed yet.",
    "⚠️  The Oracle says: fine, but have the rollback command ready to paste.",
]

# ---------------------------------------------------------------------------
# Code review comments — organized by passive-aggression flavour
# ---------------------------------------------------------------------------

_REVIEW_COMMENTS = [
    # Nit-picky
    "Nit: this variable name could be more descriptive. I'd suggest something",
    "that explains what it actually does, unlike its current name.",
    "Per our style guide (section 4, paragraph 2, subsection b), we prefer",
    "single quotes here. I've left a comment on this in two previous PRs.",
    "This is fine I guess, though I personally would have done it differently.",
    "Have you considered the implications of this approach at scale?",
    "I'm not saying this is wrong, but I'm not saying it's right either.",

    # Complexity concerns
    "This function is doing a lot. Could we break it into smaller, more",
    "focused functions that each do one thing? (See: Single Responsibility Principle.)",
    "The cyclomatic complexity of this method is concerning. Just flagging.",
    "I counted 7 levels of nesting here. Seven.",
    "We already have a utility for this in `helpers/`. Please use it.",
    "This looks like it was written quickly. No judgment. Just an observation.",

    # Testing
    "Where are the tests for the edge case where the input is None?",
    "I'd feel more comfortable merging this with a few more test cases.",
    "The test coverage for this path is 0%. I'll let that sink in.",
    "These tests are testing the happy path. Real data is not the happy path.",
    "LGTM, but have you actually run the tests?",

    # Architecture
    "This feels like a pattern we're going to regret in six months.",
    "I've seen this approach before. In a codebase we rewrote from scratch.",
    "Could we align this with the RFC we discussed in Q2? I can resend it.",
    "This introduces a new pattern. Were the team aware? Should there be an ADR?",
    "I'm approving this, but I want it noted that I had reservations.",

    # Passive praise
    "LGTM. (Assuming CI passes, which it historically has not on Fridays.)",
    "Looks good to me, though I'd want a second pair of eyes on lines 47–83.",
    "Approved. You'll want to monitor this closely after deploy.",
    "Fine. Ship it. (I accept no responsibility for what happens next.)",
    "This is clever. I'm not sure if that's a compliment.",

    # Documentation
    "No docstring. I'll just... sit with that.",
    "The comment says 'TODO: fix this'. How old is this TODO?",
    "Could you add a comment explaining *why*, not just *what*?",
    "I shouldn't need to read the implementation to understand the interface.",

    # General existential
    "Left some comments. Don't take them personally. (Take them professionally.)",
    "Reviewed. Questioned my career choices. Approved.",
    "This is readable, which puts it in the top quartile of PRs I've reviewed.",
    "I've added 11 comments. 10 are nits. 1 is blocking. Good luck finding it.",
    "The code works. Whether it *should* work this way is a different question.",
    "Rubber duck reviewed. The duck had concerns. I've documented them above.",
]


# ---------------------------------------------------------------------------
# should_i_deploy
# ---------------------------------------------------------------------------

def should_i_deploy(dt: datetime.datetime | None = None) -> str:
    """
    Consult the Oracle about whether now is a safe time to deploy.

    The Oracle's wisdom is simple:
    - **Friday afternoon (≥ 13:00 local)** → hard no, strongly worded.
    - **Weekend (Saturday / Sunday)** → concerned, why are you here?
    - **Monday morning** → cautious blessing with caveats.
    - **Any other time** → blessed, deploy away.

    Parameters
    ----------
    dt : datetime.datetime, optional
        The datetime to evaluate. Defaults to ``datetime.datetime.now()``
        (local time). Pass a specific datetime for testing or future planning.

    Returns
    -------
    str
        A verdict string from the Oracle. Always includes an emoji so you
        can tell the result at a glance from your terminal.

    Examples
    --------
    >>> print(should_i_deploy())
    ✅ Green light. The stars are aligned. Deploy with confidence.

    >>> import datetime
    >>> friday_pm = datetime.datetime(2024, 3, 15, 15, 30)  # Friday 3:30 PM
    >>> print(should_i_deploy(friday_pm))
    🚨 FRIDAY AFTERNOON DETECTED. Step away from the keyboard.
    """
    if dt is None:
        dt = datetime.datetime.now()

    weekday = dt.weekday()  # Monday=0, Sunday=6
    hour = dt.hour

    if weekday == _FRIDAY and hour >= _FRIDAY_DANGER_HOUR:
        return random.choice(_CURSED_VERDICTS)
    elif weekday in (_SATURDAY, _SUNDAY):
        return random.choice(_WEEKEND_VERDICTS)
    elif weekday == _MONDAY and hour < 9:
        return random.choice(_MONDAY_VERDICTS)
    else:
        return random.choice(_BLESSED_VERDICTS)


# ---------------------------------------------------------------------------
# code_review_roulette
# ---------------------------------------------------------------------------

def code_review_roulette(*, n: int = 1) -> str | list[str]:
    """
    Return a random passive-aggressive PR review comment, as left by a
    reviewer who has seen too many PRs and not enough sunlight.

    All comments are fictional and reflect no real code review methodology
    endorsed by any reasonable engineering organisation.

    Parameters
    ----------
    n : int, optional
        Number of comments to return. If ``1`` (default), returns a single
        string. If ``n > 1``, returns a list of ``n`` unique strings
        (or as many unique ones as the pool allows).

    Returns
    -------
    str or list[str]
        A single comment string, or a list of comment strings if ``n > 1``.

    Raises
    ------
    ValueError
        If ``n`` is less than 1.

    Examples
    --------
    >>> comment = code_review_roulette()
    >>> print(comment)
    Nit: this variable name could be more descriptive...

    >>> comments = code_review_roulette(n=3)
    >>> for c in comments:
    ...     print("-", c)
    """
    if n < 1:
        raise ValueError(f"n must be at least 1, got {n!r}")

    if n == 1:
        return random.choice(_REVIEW_COMMENTS)

    # Return n unique comments (sample without replacement up to pool size)
    k = min(n, len(_REVIEW_COMMENTS))
    return random.sample(_REVIEW_COMMENTS, k)


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import datetime

    print("=" * 60)
    print("  pocketknife.dev_oracle  —  demo")
    print("=" * 60)

    # --- should_i_deploy ---
    print("\n--- should_i_deploy ---\n")

    scenarios = [
        ("Tuesday 10 AM (blessed)",
         datetime.datetime(2024, 3, 12, 10, 0)),
        ("Friday 9 AM (still safe)",
         datetime.datetime(2024, 3, 15, 9, 0)),
        ("Friday 3 PM (CURSED)",
         datetime.datetime(2024, 3, 15, 15, 0)),
        ("Saturday noon (why?)",
         datetime.datetime(2024, 3, 16, 12, 0)),
        ("Monday 7 AM (risky)",
         datetime.datetime(2024, 3, 18, 7, 0)),
        ("Right now",
         None),
    ]

    for label, dt in scenarios:
        verdict = should_i_deploy(dt)
        print(f"  {label}:")
        print(f"    {verdict}\n")

    # --- code_review_roulette ---
    print("--- code_review_roulette ---\n")
    print("  Single comment:")
    print(f"    {code_review_roulette()}\n")

    print("  Three comments:")
    for comment in code_review_roulette(n=3):
        print(f"    • {comment}")
