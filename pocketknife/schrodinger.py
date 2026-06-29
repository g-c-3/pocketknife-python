"""
pocketknife.schrodinger
~~~~~~~~~~~~~~~~~~~~~~~
The cat is neither alive nor dead. Neither is your boolean.

Until you observe it.

Functions & Classes
-------------------
quantum_bool()
    Returns True exactly 50% of the time. Guaranteed. (Statistically.)

QuantumBool
    A boolean that exists in superposition until evaluated. Supports all
    standard boolean operations. Collapses on first observation and stays
    collapsed — the universe is consistent, even if your code isn't.

entangle(a, b)
    Entangle two QuantumBools so that observing one instantly determines
    the other to be the opposite. Spooky action at a distance.

observe_many(n)
    Observe *n* independent quantum bools and return the list of results.
    Useful for verifying the 50/50 distribution over many trials.
"""

import random
import threading
from typing import List, Optional, Tuple


# ---------------------------------------------------------------------------
# quantum_bool — the simple, honest coin flip
# ---------------------------------------------------------------------------

def quantum_bool() -> bool:
    """Return ``True`` or ``False`` with exactly 50% probability each.

    Unlike ``random.random() > 0.5`` (which has floating-point bias),
    this uses ``random.getrandbits(1)`` — the most balanced coin in the
    standard library.

    Returns
    -------
    bool

    Example
    -------
    >>> from pocketknife.schrodinger import quantum_bool
    >>> result = quantum_bool()
    >>> isinstance(result, bool)
    True
    """
    return bool(random.getrandbits(1))


# ---------------------------------------------------------------------------
# QuantumBool — superposition until observed
# ---------------------------------------------------------------------------

_UNOBSERVED = object()  # sentinel


class QuantumBool:
    """A boolean value that exists in superposition until first observed.

    Before observation, the value is neither True nor False — it is *both*.
    The moment you examine it (via ``bool()``, ``if``, ``==``, or
    ``.observe()``), the waveform collapses to a definite value and stays
    there for all future observations.

    Parameters
    ----------
    bias : float
        Probability of collapsing to ``True`` (default 0.5 for true 50/50).
        Must be in [0.0, 1.0].
    label : str, optional
        A human-readable name for this quantum bit, used in ``repr()``.

    Example
    -------
    >>> from pocketknife.schrodinger import QuantumBool
    >>> q = QuantumBool()
    >>> q.observed
    False
    >>> val = bool(q)   # collapses here
    >>> q.observed
    True
    >>> bool(q) == val  # stays collapsed
    True
    """

    def __init__(self, bias: float = 0.5, label: str = "q"):
        if not (0.0 <= bias <= 1.0):
            raise ValueError(f"bias must be in [0.0, 1.0], got {bias!r}")
        self._bias = bias
        self._label = label
        self._value = _UNOBSERVED
        self._lock = threading.Lock()
        self._entangled_partner: Optional["QuantumBool"] = None

    # ------------------------------------------------------------------
    # Core collapse logic
    # ------------------------------------------------------------------

    def _collapse(self) -> bool:
        """Collapse the waveform. Thread-safe; idempotent after first call."""
        with self._lock:
            if self._value is _UNOBSERVED:
                self._value = random.random() < self._bias
                # Spooky action: tell the partner to collapse to the opposite
                if self._entangled_partner is not None:
                    partner = self._entangled_partner
                    with partner._lock:
                        if partner._value is _UNOBSERVED:
                            partner._value = not self._value
        return self._value  # type: ignore[return-value]

    def observe(self) -> bool:
        """Explicitly observe (collapse) this QuantumBool.

        Returns
        -------
        bool
            The collapsed value.
        """
        return self._collapse()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def observed(self) -> bool:
        """``True`` if this QuantumBool has already been observed."""
        return self._value is not _UNOBSERVED

    @property
    def value(self) -> Optional[bool]:
        """The collapsed value, or ``None`` if not yet observed."""
        return None if self._value is _UNOBSERVED else self._value

    @property
    def bias(self) -> float:
        """The probability of collapsing to ``True``."""
        return self._bias

    # ------------------------------------------------------------------
    # Python data model — everything that "looks at" the value
    # ------------------------------------------------------------------

    def __bool__(self) -> bool:
        return self._collapse()

    def __int__(self) -> int:
        return int(self._collapse())

    def __eq__(self, other: object) -> bool:
        if isinstance(other, QuantumBool):
            return self._collapse() == other._collapse()
        if isinstance(other, bool):
            return self._collapse() == other
        return NotImplemented

    def __ne__(self, other: object) -> bool:
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    def __and__(self, other: object) -> bool:
        if isinstance(other, QuantumBool):
            return self._collapse() and other._collapse()
        if isinstance(other, bool):
            return self._collapse() and other
        return NotImplemented

    def __or__(self, other: object) -> bool:
        if isinstance(other, QuantumBool):
            return self._collapse() or other._collapse()
        if isinstance(other, bool):
            return self._collapse() or other
        return NotImplemented

    def __xor__(self, other: object) -> bool:
        if isinstance(other, QuantumBool):
            return self._collapse() ^ other._collapse()
        if isinstance(other, bool):
            return self._collapse() ^ other
        return NotImplemented

    def __invert__(self) -> bool:
        return not self._collapse()

    def __repr__(self) -> str:
        if self._value is _UNOBSERVED:
            return f"QuantumBool({self._label!r}, state=|0⟩+|1⟩)"
        return f"QuantumBool({self._label!r}, collapsed={self._value!r})"

    def __hash__(self):
        # Must be hashable; collapse on hash (as Python would for bool)
        return hash(self._collapse())


# ---------------------------------------------------------------------------
# entangle — spooky action at a distance
# ---------------------------------------------------------------------------

def entangle(a: QuantumBool, b: QuantumBool) -> Tuple[QuantumBool, QuantumBool]:
    """Entangle two ``QuantumBool`` instances so they always collapse to opposites.

    Once entangled, observing *a* instantly forces *b* to the opposite value
    (and vice versa), regardless of which one is observed first — exactly like
    the EPR paradox, but considerably less useful for physics.

    Parameters
    ----------
    a, b : QuantumBool
        Two *unobserved* QuantumBools to entangle.

    Returns
    -------
    (QuantumBool, QuantumBool)
        The same two objects, now entangled, for convenience.

    Raises
    ------
    ValueError
        If either QuantumBool has already been observed (the waveform has
        already collapsed — you can't entangle a dead cat).

    Example
    -------
    >>> from pocketknife.schrodinger import QuantumBool, entangle
    >>> a, b = entangle(QuantumBool(), QuantumBool())
    >>> bool(a)     # collapses a; b is instantly forced to the opposite
    True            # (or False — 50/50)
    >>> bool(b) == (not bool(a))
    True
    """
    if a.observed:
        raise ValueError(
            "Cannot entangle an already-observed QuantumBool — "
            "the waveform has collapsed."
        )
    if b.observed:
        raise ValueError(
            "Cannot entangle an already-observed QuantumBool — "
            "the waveform has collapsed."
        )
    if a is b:
        raise ValueError("Cannot entangle a QuantumBool with itself.")

    a._entangled_partner = b
    b._entangled_partner = a
    return a, b


# ---------------------------------------------------------------------------
# observe_many — batch observation / distribution check
# ---------------------------------------------------------------------------

def observe_many(n: int) -> List[bool]:
    """Observe *n* independent quantum bools and return the results.

    Parameters
    ----------
    n : int
        Number of observations. Must be >= 1.

    Returns
    -------
    list of bool
        A list of *n* boolean values, each independently 50/50.

    Example
    -------
    >>> from pocketknife.schrodinger import observe_many
    >>> results = observe_many(1000)
    >>> 400 <= sum(results) <= 600   # roughly 50/50 over 1000 trials
    True
    """
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n!r}")
    return [quantum_bool() for _ in range(n)]


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=== pocketknife.schrodinger demo ===\n")

    # 1. Simple quantum_bool
    print("1. quantum_bool() — 20 independent observations:")
    results = [quantum_bool() for _ in range(20)]
    print("   ", results)
    trues = sum(results)
    print(f"    True: {trues}/20  |  False: {20 - trues}/20\n")

    # 2. QuantumBool superposition
    print("2. QuantumBool in superposition:")
    q = QuantumBool(label="cat")
    print(f"   Before observation: {q!r}")
    print(f"   observed? {q.observed}")
    val = bool(q)
    print(f"   After  observation: {q!r}")
    print(f"   observed? {q.observed}  |  value: {val}\n")

    # 3. Stable after collapse
    print("3. QuantumBool is stable after collapse:")
    q2 = QuantumBool(label="stable")
    readings = [bool(q2) for _ in range(5)]
    print(f"   5 readings: {readings}  (all identical)\n")

    # 4. Entanglement
    print("4. Entangled pair (always opposite):")
    for trial in range(5):
        a, b = entangle(QuantumBool(label="A"), QuantumBool(label="B"))
        va, vb = bool(a), bool(b)
        print(f"   Trial {trial + 1}: A={va}, B={vb}  —  opposite? {va != vb}")

    # 5. observe_many distribution
    print("\n5. observe_many(10_000) distribution:")
    many = observe_many(10_000)
    t = sum(many)
    print(f"   True: {t} ({t/100:.1f}%)  |  False: {10000 - t} ({(10000 - t)/100:.1f}%)")

    # 6. Biased QuantumBool
    print("\n6. Biased QuantumBool(bias=0.8) over 100 trials:")
    biased_trues = sum(bool(QuantumBool(bias=0.8)) for _ in range(100))
    print(f"   True: {biased_trues}/100  (expect ~80)")
