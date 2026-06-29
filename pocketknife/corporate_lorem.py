"""
pocketknife.corporate_lorem
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Filler text generators for when you need placeholder copy that at least
*sounds* like something.

Functions
---------
buzzwords(n=1)
    Generate n sentences of corporate-speak buzzword soup.

pirate(n=1)
    Generate n sentences of pirate-flavoured filler text.
"""

import random

# ---------------------------------------------------------------------------
# Internal word banks
# ---------------------------------------------------------------------------

_BZ_SUBJECTS = [
    "Our core competencies",
    "The synergy initiative",
    "Cross-functional alignment",
    "Agile transformation",
    "Our digital-first strategy",
    "Stakeholder engagement",
    "The paradigm shift",
    "Value-chain optimisation",
    "Next-generation solutions",
    "Holistic ecosystem thinking",
    "Proactive disruption",
    "Our bandwidth",
    "The scalable framework",
    "Mission-critical deliverables",
    "Key performance indicators",
]

_BZ_VERBS = [
    "enables",
    "leverages",
    "accelerates",
    "disrupts",
    "synergises",
    "future-proofs",
    "de-risks",
    "incentivises",
    "unlocks",
    "operationalises",
    "streamlines",
    "ideates around",
    "pivots toward",
    "circles back on",
    "takes offline",
]

_BZ_OBJECTS = [
    "best-in-class ROI",
    "low-hanging fruit",
    "robust thought leadership",
    "end-to-end visibility",
    "actionable insights",
    "seamless omnichannel experiences",
    "bleeding-edge innovation",
    "blue-sky thinking",
    "a culture of continuous improvement",
    "the north star metric",
    "sustainable growth loops",
    "deep-dive retrospectives",
    "360-degree stakeholder alignment",
    "a minimum viable product",
    "strategic runway",
]

_BZ_SUFFIXES = [
    "going forward.",
    "at scale.",
    "across all verticals.",
    "in the current landscape.",
    "within the agile sprint cycle.",
    "from a 30,000-foot view.",
    "with full buy-in from leadership.",
    "by EOD.",
    "in a VUCA environment.",
    "to move the needle.",
    "with minimal lift.",
    "at the end of the day.",
    "in our collective wheelhouse.",
    "per the latest deck.",
    "across the board.",
]

# ---------------------------------------------------------------------------

_PI_SUBJECTS = [
    "The scallywag crew",
    "Cap'n Blacktooth",
    "A motley band of buccaneers",
    "The first mate",
    "Davy Jones",
    "The sea itself",
    "Salty Pete the navigator",
    "A fearsome kraken",
    "The Jolly Roger",
    "Three landlubbers",
    "A one-eyed quartermaster",
    "The ship's parrot",
    "Barnacle Bill",
    "A ghost galleon",
    "The powder monkey",
]

_PI_VERBS = [
    "plundered",
    "set sail for",
    "swabbed the deck toward",
    "keelhauled the notion of",
    "weighed anchor near",
    "fired a broadside at",
    "buried treasure beside",
    "hoisted the flag over",
    "navigated treacherous waters toward",
    "pillaged and pilfered",
    "charted a course for",
    "bellowed 'Arr!' about",
    "traded rum for",
    "shanghaied a sailor near",
    "walked the plank above",
]

_PI_OBJECTS = [
    "a chest of doubloons",
    "the seven seas",
    "a sunken galleon",
    "twelve barrels of grog",
    "the Fountain of Youth",
    "a poorly drawn treasure map",
    "the ghost of a rival pirate",
    "three bags of salt cod",
    "Port Royal at midnight",
    "an island of misfit corsairs",
    "a mermaid's lagoon",
    "the cursed idol of Tortuga",
    "a sea monster's lair",
    "a merchantman's gold",
    "the edge of the known world",
]

_PI_SUFFIXES = [
    "Arr!",
    "or me name ain't what it is!",
    "by Davy Jones' locker.",
    "shiver me timbers!",
    "and the sea wept salt tears.",
    "before the tide turned.",
    "whilst the kraken slept.",
    "under a blood-red moon.",
    "with a song in their hearts and rum in their bellies.",
    "aye, and not a doubloon to show for it.",
    "as the parrot screamed warnings.",
    "and nobody saw it comin'.",
    "afore the navy arrived.",
    "on pain of walking the plank.",
    "for the glory of the Jolly Roger.",
]


def _make_sentence(subjects, verbs, objects, suffixes):
    """Pick one item at random from each list and assemble a sentence."""
    return (
        f"{random.choice(subjects)} {random.choice(verbs)} "
        f"{random.choice(objects)} {random.choice(suffixes)}"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def buzzwords(n: int = 1) -> str:
    """Return *n* sentences of corporate-speak buzzword lorem ipsum.

    Parameters
    ----------
    n : int
        Number of sentences to generate (default 1).

    Returns
    -------
    str
        One string containing *n* sentences separated by spaces.

    Examples
    --------
    >>> import random; random.seed(0)
    >>> print(buzzwords(2))
    Our bandwidth takes offline low-hanging fruit across all verticals.
    Holistic ecosystem thinking operationalises actionable insights going forward.
    """
    if n < 1:
        raise ValueError(f"n must be a positive integer, got {n!r}")
    sentences = [
        _make_sentence(_BZ_SUBJECTS, _BZ_VERBS, _BZ_OBJECTS, _BZ_SUFFIXES)
        for _ in range(n)
    ]
    return " ".join(sentences)


def pirate(n: int = 1) -> str:
    """Return *n* sentences of pirate-themed filler text.

    Parameters
    ----------
    n : int
        Number of sentences to generate (default 1).

    Returns
    -------
    str
        One string containing *n* pirate sentences separated by spaces.

    Examples
    --------
    >>> import random; random.seed(42)
    >>> print(pirate(2))
    The ship's parrot plundered a chest of doubloons aye, and not a doubloon to show for it.
    Barnacle Bill weighed anchor near the cursed idol of Tortuga shiver me timbers!
    """
    if n < 1:
        raise ValueError(f"n must be a positive integer, got {n!r}")
    sentences = [
        _make_sentence(_PI_SUBJECTS, _PI_VERBS, _PI_OBJECTS, _PI_SUFFIXES)
        for _ in range(n)
    ]
    return " ".join(sentences)


# ---------------------------------------------------------------------------
# Quick demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import textwrap

    print("=" * 60)
    print("CORPORATE BUZZWORDS (5 sentences)")
    print("=" * 60)
    print(textwrap.fill(buzzwords(5), width=60))

    print()
    print("=" * 60)
    print("PIRATE LOREM IPSUM (5 sentences)")
    print("=" * 60)
    print(textwrap.fill(pirate(5), width=60))
