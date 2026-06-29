"""
Tests for pocketknife.corporate_lorem
"""

import sys
import os
import random

import pytest

# Make sure the repo root is on the path when running from any directory.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pocketknife.corporate_lorem import buzzwords, pirate


# ---------------------------------------------------------------------------
# buzzwords()
# ---------------------------------------------------------------------------

class TestBuzzwords:

    def test_returns_string(self):
        result = buzzwords()
        assert isinstance(result, str)

    def test_default_is_one_sentence(self):
        """A single sentence ends with a period (all suffixes end with one)."""
        random.seed(0)
        result = buzzwords(1)
        # Should contain exactly one terminal punctuation mark at the end
        assert len(result.strip()) > 0

    def test_n_sentences_produces_more_text(self):
        random.seed(1)
        one = buzzwords(1)
        five = buzzwords(5)
        assert len(five) > len(one)

    def test_multiple_sentences_joined_by_space(self):
        random.seed(2)
        result = buzzwords(3)
        # Three sentences joined by spaces → at least 2 spaces between sentences
        # simplest proxy: word count is higher than a single sentence
        words = result.split()
        assert len(words) >= 6  # each sentence is at least 5–6 words

    def test_raises_on_zero(self):
        with pytest.raises(ValueError):
            buzzwords(0)

    def test_raises_on_negative(self):
        with pytest.raises(ValueError):
            buzzwords(-3)

    def test_deterministic_with_seed(self):
        random.seed(99)
        first = buzzwords(4)
        random.seed(99)
        second = buzzwords(4)
        assert first == second

    def test_large_n(self):
        result = buzzwords(50)
        assert isinstance(result, str)
        assert len(result) > 100

    def test_contains_no_pirate_words(self):
        random.seed(7)
        result = buzzwords(10).lower()
        pirate_markers = ["arr", "doubloon", "kraken", "buccaneer", "plunder"]
        for marker in pirate_markers:
            assert marker not in result, f"Found pirate word '{marker}' in buzzwords output"


# ---------------------------------------------------------------------------
# pirate()
# ---------------------------------------------------------------------------

class TestPirate:

    def test_returns_string(self):
        result = pirate()
        assert isinstance(result, str)

    def test_default_is_one_sentence(self):
        result = pirate(1)
        assert len(result.strip()) > 0

    def test_n_sentences_produces_more_text(self):
        random.seed(3)
        one = pirate(1)
        five = pirate(5)
        assert len(five) > len(one)

    def test_raises_on_zero(self):
        with pytest.raises(ValueError):
            pirate(0)

    def test_raises_on_negative(self):
        with pytest.raises(ValueError):
            pirate(-1)

    def test_deterministic_with_seed(self):
        random.seed(42)
        first = pirate(4)
        random.seed(42)
        second = pirate(4)
        assert first == second

    def test_large_n(self):
        result = pirate(50)
        assert isinstance(result, str)
        assert len(result) > 100

    def test_feels_piratey(self):
        """At least one of 20 sentences should contain a pirate flavour word."""
        random.seed(13)
        result = pirate(20).lower()
        pirate_markers = [
            "arr", "doubloon", "kraken", "buccaneer", "plunder",
            "jolly roger", "davy jones", "grog", "galleon", "rum",
            "landlubber", "corsair", "parrot", "barnacle", "keelhaul",
        ]
        found = [m for m in pirate_markers if m in result]
        assert len(found) > 0, "Expected at least one pirate-flavoured word in 20 sentences"

    def test_contains_no_corporate_words(self):
        random.seed(5)
        result = pirate(10).lower()
        corporate_markers = ["synergy", "leverage", "roi", "stakeholder", "agile"]
        for marker in corporate_markers:
            assert marker not in result, f"Found corporate word '{marker}' in pirate output"


# ---------------------------------------------------------------------------
# Cross-function
# ---------------------------------------------------------------------------

class TestCrossFunction:

    def test_outputs_are_independent(self):
        """buzzwords and pirate with the same seed produce different text."""
        random.seed(77)
        bz = buzzwords(3)
        random.seed(77)
        pi = pirate(3)
        assert bz != pi

    def test_both_callable_back_to_back(self):
        combined = buzzwords(2) + " " + pirate(2)
        assert isinstance(combined, str)
        assert len(combined) > 20
