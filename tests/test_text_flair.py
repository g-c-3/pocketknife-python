"""
Tests for pocketknife.text_flair
"""

import sys
import os

# Allow running from repo root or tests/ directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pocketknife.text_flair import spongecase, leetspeak, clapy


# ===========================================================================
# spongecase
# ===========================================================================

class TestSpongecase:

    def test_basic_alternation(self):
        result = spongecase("hello")
        assert result == "hElLo"

    def test_starts_lowercase(self):
        # First letter should always be lowercase
        assert spongecase("ABCDE")[0] == "a"

    def test_non_alpha_passthrough(self):
        # Digits and punctuation pass through unchanged
        result = spongecase("a1b2c3")
        assert result == "a1B2c3"

    def test_non_alpha_does_not_flip_case_slot(self):
        # Non-letters should NOT consume an alternation slot
        # "a" → lower (slot 0), "!" → passthrough, "b" → upper (slot 1)
        result = spongecase("a!b")
        assert result == "a!B"

    def test_empty_string(self):
        assert spongecase("") == ""

    def test_all_uppercase_input(self):
        result = spongecase("HELLO")
        assert result == "hElLo"

    def test_spaces_preserved(self):
        result = spongecase("hi ho")
        assert result == "hI hO"

    def test_preserves_length(self):
        text = "The quick brown fox"
        assert len(spongecase(text)) == len(text)

    def test_only_non_alpha(self):
        assert spongecase("123 !@#") == "123 !@#"


# ===========================================================================
# leetspeak
# ===========================================================================

class TestLeetspeak:

    def test_basic_substitution(self):
        assert leetspeak("leet") == "1337"

    def test_elite_hacker(self):
        # e→3, l→1 (mapped), i→1, t→7, e→3
        assert leetspeak("elite") == "31173"

    def test_non_mapped_chars_unchanged(self):
        # Letters not in the leet map stay as-is
        result = leetspeak("xyz")
        assert result == "xyz"

    def test_full_intensity_is_deterministic_for_unmapped(self):
        # At intensity=1.0, every mappable char should be swapped
        # a→4, e→3, i→1, o→0, s→5, t→7
        result = leetspeak("aeiost", intensity=1.0)
        assert result == "431057"

    def test_zero_intensity_no_change(self):
        # At intensity=0.0, nothing should be swapped
        result = leetspeak("aeiost", intensity=0.0)
        assert result == "aeiost"

    def test_empty_string(self):
        assert leetspeak("") == ""

    def test_invalid_intensity_too_high(self):
        with pytest.raises(ValueError):
            leetspeak("hello", intensity=1.5)

    def test_invalid_intensity_too_low(self):
        with pytest.raises(ValueError):
            leetspeak("hello", intensity=-0.1)

    def test_case_insensitive_mapping(self):
        # Both upper and lower case letters should be mapped
        assert leetspeak("A") == "4"
        assert leetspeak("a") == "4"
        assert leetspeak("E") == "3"
        assert leetspeak("e") == "3"

    def test_digits_and_punctuation_unchanged(self):
        result = leetspeak("1! 2@ 3#")
        assert result == "1! 2@ 3#"

    def test_intensity_boundary_values(self):
        # Should not raise at exact boundaries
        leetspeak("hello", intensity=0.0)
        leetspeak("hello", intensity=1.0)

    def test_partial_intensity_returns_string(self):
        # At 0.5 intensity, result should be a string of the same length
        result = leetspeak("abcdefghij", intensity=0.5)
        assert isinstance(result, str)
        assert len(result) == 10


# ===========================================================================
# clapy
# ===========================================================================

class TestClapy:

    def test_basic_clap(self):
        assert clapy("read the room") == "read 👏 the 👏 room"

    def test_single_word(self):
        assert clapy("hello") == "hello"

    def test_empty_string(self):
        assert clapy("") == ""

    def test_only_whitespace(self):
        assert clapy("   ") == ""

    def test_custom_emoji(self):
        assert clapy("ok boomer", emoji="💅") == "ok 💅 boomer"

    def test_strips_leading_trailing_whitespace(self):
        assert clapy("  hello world  ") == "hello 👏 world"

    def test_collapses_internal_whitespace(self):
        # Multiple spaces between words should be collapsed
        assert clapy("hello   world") == "hello 👏 world"

    def test_two_words(self):
        assert clapy("hello world") == "hello 👏 world"

    def test_custom_string_separator(self):
        result = clapy("one two three", emoji="AND")
        assert result == "one AND two AND three"

    def test_preserves_word_content(self):
        words = ["Python", "is", "great"]
        result = clapy(" ".join(words))
        for word in words:
            assert word in result

    def test_newline_treated_as_whitespace(self):
        result = clapy("line1\nline2")
        assert result == "line1 👏 line2"
