"""
pocketknife.rubber_duck
========================

An ELIZA-style debugging companion. When you're stuck on a bug, talk to
the duck. It won't solve your problem, but it will ask the right
Socratic questions to help *you* solve it -- which is, after all, the
entire point of rubber duck debugging.

Public API
----------
summon_duck(input_fn=input, print_fn=print, seed=None)
    Starts an interactive REPL loop with the duck. Type 'quit', 'exit',
    or 'bye' to end the session.

Duck
    The class powering the conversation. Exposed for programmatic /
    non-interactive use (e.g. testing, or piping in a transcript).
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Pattern, Tuple

__all__ = ["summon_duck", "Duck"]


# ---------------------------------------------------------------------------
# Reflection: swaps first/second person pronouns so echoed fragments make
# grammatical sense, e.g. "my function" -> "your function".
# ---------------------------------------------------------------------------
_REFLECTIONS = {
    "i": "you",
    "me": "you",
    "my": "your",
    "mine": "yours",
    "myself": "yourself",
    "i'm": "you're",
    "i've": "you've",
    "i'll": "you'll",
    "am": "are",
    "you": "I",
    "your": "my",
    "yours": "mine",
    "you're": "I'm",
    "you've": "I've",
    "yourself": "myself",
}


def _reflect(fragment: str) -> str:
    words = fragment.strip().split()
    return " ".join(_REFLECTIONS.get(w.lower(), w) for w in words)


# ---------------------------------------------------------------------------
# Pattern -> response templates. {0}, {1}... refer to reflected regex
# groups. Order matters: first matching pattern wins.
# ---------------------------------------------------------------------------
_PatternResponses = Tuple[Pattern, Tuple[str, ...]]


def _build_patterns() -> List[_PatternResponses]:
    raw: List[Tuple[str, Tuple[str, ...]]] = [
        (r"\bwhy (is|does|isn'?t|doesn'?t) (.+?)\??$",
         ("What have you already tried to find out why {1} {0}?",
          "What would you expect to happen instead, and why?")),

        (r"\b(.+) (is|are) (broken|failing|crashing)\b",
         ("What does {0} do right before it {2}?",
          "Have you reproduced {0} {2} with the smallest possible input?")),

        (r"\bi (think|believe|guess) (.+)",
         ("What evidence do you have that {1}?",
          "What would prove you wrong about {1}?")),

        (r"\bi('m| am) (stuck|lost|confused)\b",
         ("Where exactly did things stop making sense?",
          "What's the last thing you understood for certain?")),

        (r"\bi (can'?t|cannot) (.+)",
         ("What have you tried in order to {1}?",
          "What happens, exactly, when you try to {1}?")),

        (r"\berror\b.*\b(line|in)\s*(\d+|\w+)",
         ("What does the code look like right at {1} {2}?",
          "Did you check what the value of every variable was at {1} {2}?")),

        (r"\b(it|this|that) (doesn'?t|does not) work\b",
         ("What does '{1} work' look like when it succeeds?",
          "What's different between when {0} works and when it doesn't?")),

        (r"\bexpected (.+) but got (.+)",
         ("What would make {1} turn into {2} -- where in the flow could that happen?",
          "Have you printed the value right before it becomes {2}?")),

        (r"\bnull|none|undefined\b",
         ("Where was that value supposed to be set, and was that code path actually run?",
          "What's the very first place this value could have been set, and did you check it?")),

        (r"\bworks on my machine\b",
         ("What's different about the environment where it fails?",
          "Have you compared dependency versions between the two machines?")),

        (r"\b(.+)\?$",
         ("What makes you ask whether {0}?",
          "What have you already ruled out about {0}?")),
    ]
    return [(re.compile(p, re.IGNORECASE), r) for p, r in raw]


_PATTERNS = _build_patterns()

_GENERIC_PROMPTS = (
    "Go on -- walk me through it step by step.",
    "What's the smallest example that reproduces this?",
    "What did you expect to happen, and what actually happened?",
    "Have you checked the obvious thing yet? (You know the one.)",
    "What changed right before this started happening?",
    "If you had to explain this bug to a beginner, what would you say?",
    "What's one assumption you're making that might be wrong?",
    "What does the very first line of the traceback actually say?",
)

_GREETINGS = (
    "🦆 *quack* I'm listening. What's broken?",
    "🦆 The duck is ready. Describe the bug from the top.",
    "🦆 *blinks expectantly* Go ahead, explain it to me like I know nothing.",
)

_FAREWELLS = (
    "🦆 Good luck out there. *quack*",
    "🦆 Glad I could listen. Go fix it.",
    "🦆 *waddles off into the pond*",
)


@dataclass
class Duck:
    """The stateless-ish brain behind the duck. One instance per session."""

    rng: random.Random = field(default_factory=random.Random)
    _used_generic: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.rng, random.Random):
            self.rng = random.Random(self.rng)

    def greet(self) -> str:
        return self.rng.choice(_GREETINGS)

    def farewell(self) -> str:
        return self.rng.choice(_FAREWELLS)

    def respond(self, text: str) -> str:
        """Given one line of user input, return the duck's next question."""
        text = text.strip()
        if not text:
            return "🦆 ...silence. Try saying it out loud anyway."

        for pattern, templates in _PATTERNS:
            match = pattern.search(text)
            if match:
                groups = [_reflect(g) for g in match.groups() if g is not None]
                template = self.rng.choice(templates)
                try:
                    return "🦆 " + template.format(*groups)
                except (IndexError, KeyError):
                    continue  # template needed more groups than we got

        return "🦆 " + self._next_generic()

    def _next_generic(self) -> str:
        if len(self._used_generic) >= len(_GENERIC_PROMPTS):
            self._used_generic.clear()
        remaining = [p for p in _GENERIC_PROMPTS if p not in self._used_generic]
        choice = self.rng.choice(remaining)
        self._used_generic.append(choice)
        return choice


_QUIT_WORDS = {"quit", "exit", "bye", "goodbye", "q"}


def summon_duck(
    input_fn: Callable[[str], str] = input,
    print_fn: Callable[[str], None] = print,
    seed: Optional[int] = None,
) -> None:
    """
    Start an interactive rubber-duck debugging session.

    Parameters
    ----------
    input_fn:
        Function used to read a line of user input. Defaults to the
        builtin ``input``. Override for testing or non-stdin use.
    print_fn:
        Function used to print the duck's responses. Defaults to the
        builtin ``print``.
    seed:
        Optional seed for reproducible duck responses (mainly for tests).

    The session ends when the user types one of: quit, exit, bye,
    goodbye, q -- or sends EOF (Ctrl-D / Ctrl-Z).
    """
    duck = Duck(rng=random.Random(seed) if seed is not None else random.Random())
    print_fn(duck.greet())

    while True:
        try:
            user_text = input_fn("you> ")
        except EOFError:
            print_fn("\n" + duck.farewell())
            return

        if user_text.strip().lower() in _QUIT_WORDS:
            print_fn(duck.farewell())
            return

        print_fn(duck.respond(user_text))


if __name__ == "__main__":
    summon_duck()
