"""Unit tests for pocketknife.clean_strings."""

import unittest

from pocketknife.clean_strings import normalize_text, slugify


class TestNormalizeText(unittest.TestCase):

    # --- whitespace ---

    def test_strips_leading_trailing_whitespace(self):
        self.assertEqual(normalize_text("  hello  "), "hello")

    def test_collapses_internal_whitespace(self):
        self.assertEqual(normalize_text("hello   world"), "hello world")

    def test_handles_tabs_and_newlines(self):
        self.assertEqual(normalize_text("hello\t\nworld"), "hello world")

    # --- invisible / control characters ---

    def test_strips_zero_width_space(self):
        self.assertEqual(normalize_text("hel\u200blo"), "hello")

    def test_strips_zero_width_non_joiner(self):
        self.assertEqual(normalize_text("hel\u200clo"), "hello")

    def test_strips_bom(self):
        self.assertEqual(normalize_text("\ufeffhello"), "hello")

    # --- smart quote / dash replacement ---

    def test_replaces_right_single_quote(self):
        self.assertEqual(normalize_text("it\u2019s"), "it's")

    def test_replaces_left_double_quote(self):
        self.assertEqual(normalize_text("\u201chello\u201d"), '"hello"')

    def test_replaces_em_dash(self):
        self.assertEqual(normalize_text("one\u2014two"), "one-two")

    def test_replaces_en_dash(self):
        self.assertEqual(normalize_text("one\u2013two"), "one-two")

    # --- case ---

    def test_case_lower(self):
        self.assertEqual(normalize_text("HELLO", case="lower"), "hello")

    def test_case_upper(self):
        self.assertEqual(normalize_text("hello", case="upper"), "HELLO")

    def test_case_title(self):
        self.assertEqual(normalize_text("hello world", case="title"), "Hello World")

    def test_invalid_case_raises_value_error(self):
        with self.assertRaises(ValueError):
            normalize_text("hi", case="sentence")

    # --- strip_accents ---

    def test_strip_accents_removes_diacritics(self):
        self.assertEqual(normalize_text("café", strip_accents=True), "cafe")

    def test_strip_accents_false_preserves_accents(self):
        self.assertEqual(normalize_text("café", strip_accents=False), "café")

    def test_strip_accents_multiple(self):
        self.assertEqual(
            normalize_text("résumé naïve", strip_accents=True), "resume naive"
        )

    # --- ascii_only ---

    def test_ascii_only_removes_non_ascii(self):
        self.assertEqual(normalize_text("café", ascii_only=True), "caf")

    def test_ascii_only_preserves_printable_ascii(self):
        self.assertEqual(normalize_text("hello!", ascii_only=True), "hello!")

    def test_strip_accents_then_ascii_only(self):
        # strip_accents first turns é → e, then ascii_only keeps it
        self.assertEqual(
            normalize_text("café", strip_accents=True, ascii_only=True), "cafe"
        )

    # --- type safety ---

    def test_non_string_raises_type_error(self):
        with self.assertRaises(TypeError):
            normalize_text(42)  # type: ignore[arg-type]

    def test_empty_string_returns_empty(self):
        self.assertEqual(normalize_text(""), "")

    def test_whitespace_only_returns_empty(self):
        self.assertEqual(normalize_text("   "), "")


class TestSlugify(unittest.TestCase):

    def test_basic_slug(self):
        self.assertEqual(slugify("Hello, World!"), "hello-world")

    def test_strips_punctuation(self):
        self.assertEqual(slugify("one, two, three."), "one-two-three")

    def test_custom_separator(self):
        self.assertEqual(slugify("hello world", separator="_"), "hello_world")

    def test_collapses_multiple_non_alnum(self):
        self.assertEqual(slugify("hello---world"), "hello-world")

    def test_strips_leading_trailing_separator(self):
        self.assertEqual(slugify("  hello  "), "hello")

    def test_accent_stripping(self):
        self.assertEqual(slugify("Ça va?"), "ca-va")

    def test_max_length_truncates(self):
        result = slugify("hello world", max_length=5)
        self.assertLessEqual(len(result), 5)

    def test_empty_string_returns_empty(self):
        self.assertEqual(slugify(""), "")

    def test_all_special_chars_returns_empty(self):
        self.assertEqual(slugify("!@#$%"), "")

    def test_numbers_preserved(self):
        self.assertEqual(slugify("version 2.0"), "version-2-0")


if __name__ == "__main__":
    unittest.main()
