"""
tests/test_hype.py
~~~~~~~~~~~~~~~~~~
Unit tests for pocketknife.hype.
"""

import io
import unittest
from unittest.mock import patch

from pocketknife.hype import (
    _HYPE_BANKS,
    _VALID_LEVELS,
    _progress_prefix,
    hype_list,
    hype_man,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _stream():
    return io.StringIO()


def _exhaust(iterable):
    """Consume an iterable and return a list of its items."""
    return list(iterable)


# ---------------------------------------------------------------------------
# _progress_prefix
# ---------------------------------------------------------------------------

class TestProgressPrefix(unittest.TestCase):

    def test_with_known_total(self):
        result = _progress_prefix(10, 100)
        self.assertIn("10", result)
        self.assertIn("100", result)
        self.assertIn("10%", result)

    def test_without_total(self):
        result = _progress_prefix(10, None)
        self.assertIn("10", result)
        self.assertIn("?", result)

    def test_100_percent_at_end(self):
        result = _progress_prefix(50, 50)
        self.assertIn("100%", result)

    def test_zero_total_does_not_raise(self):
        result = _progress_prefix(0, 0)
        self.assertIsInstance(result, str)

    def test_format_contains_separator(self):
        result = _progress_prefix(5, 20)
        self.assertIn("/", result)


# ---------------------------------------------------------------------------
# hype_man — yields items correctly
# ---------------------------------------------------------------------------

class TestHypeManYields(unittest.TestCase):

    def test_yields_all_items_from_list(self):
        items = [1, 2, 3, 4, 5]
        result = _exhaust(hype_man(items, stream=_stream()))
        self.assertEqual(result, items)

    def test_yields_all_items_from_range(self):
        result = _exhaust(hype_man(range(20), stream=_stream()))
        self.assertEqual(result, list(range(20)))

    def test_yields_all_items_from_generator(self):
        gen = (x * 2 for x in range(5))
        result = _exhaust(hype_man(gen, stream=_stream()))
        self.assertEqual(result, [0, 2, 4, 6, 8])

    def test_yields_all_items_from_string_iterable(self):
        words = ["alpha", "beta", "gamma"]
        result = _exhaust(hype_man(words, stream=_stream()))
        self.assertEqual(result, words)

    def test_empty_iterable_yields_nothing(self):
        result = _exhaust(hype_man([], stream=_stream()))
        self.assertEqual(result, [])

    def test_items_are_not_mutated(self):
        items = [{"a": 1}, {"b": 2}]
        result = _exhaust(hype_man(items, stream=_stream()))
        self.assertEqual(result, items)

    def test_is_lazy_generator(self):
        """hype_man must return an iterator, not materialise the whole list."""
        import types
        result = hype_man(range(10), stream=_stream())
        self.assertIsInstance(result, types.GeneratorType)


# ---------------------------------------------------------------------------
# hype_man — message frequency
# ---------------------------------------------------------------------------

class TestHypeManFrequency(unittest.TestCase):

    def test_messages_printed_at_correct_interval(self):
        stream = _stream()
        _exhaust(hype_man(range(30), every=10, finale=False, stream=stream))
        # Expect messages at 10, 20, 30 → 3 lines
        lines = [l for l in stream.getvalue().splitlines() if l.strip()]
        self.assertEqual(len(lines), 3)

    def test_every_1_prints_each_iteration(self):
        stream = _stream()
        _exhaust(hype_man(range(5), every=1, finale=False, stream=stream))
        lines = [l for l in stream.getvalue().splitlines() if l.strip()]
        self.assertEqual(len(lines), 5)

    def test_every_larger_than_iterable_prints_no_mid_messages(self):
        stream = _stream()
        _exhaust(hype_man(range(5), every=100, finale=False, stream=stream))
        self.assertEqual(stream.getvalue().strip(), "")

    def test_finale_printed_once_at_end(self):
        stream = _stream()
        _exhaust(hype_man(range(7), every=100, finale=True, stream=stream))
        lines = [l for l in stream.getvalue().splitlines() if l.strip()]
        self.assertEqual(len(lines), 1)

    def test_no_finale_when_disabled(self):
        stream = _stream()
        _exhaust(hype_man(range(10), every=100, finale=False, stream=stream))
        self.assertEqual(stream.getvalue().strip(), "")

    def test_no_output_for_empty_iterable(self):
        stream = _stream()
        _exhaust(hype_man([], every=1, stream=stream))
        self.assertEqual(stream.getvalue(), "")

    def test_finale_not_duplicate_of_mid_message(self):
        """When every divides len exactly, the finale should still only appear once."""
        stream = _stream()
        _exhaust(hype_man(range(10), every=10, finale=True, stream=stream))
        # 1 mid message at index 10, 1 finale at index 10 — total 2 lines
        lines = [l for l in stream.getvalue().splitlines() if l.strip()]
        self.assertEqual(len(lines), 2)


# ---------------------------------------------------------------------------
# hype_man — progress prefix in output
# ---------------------------------------------------------------------------

class TestHypeManProgressOutput(unittest.TestCase):

    def test_index_appears_in_output(self):
        stream = _stream()
        _exhaust(hype_man(range(10), every=10, finale=False, stream=stream))
        self.assertIn("10", stream.getvalue())

    def test_total_appears_for_sized_iterable(self):
        stream = _stream()
        _exhaust(hype_man(list(range(20)), every=10, finale=False, stream=stream))
        self.assertIn("20", stream.getvalue())

    def test_unknown_total_for_generator(self):
        stream = _stream()
        gen = (x for x in range(10))
        _exhaust(hype_man(gen, every=10, finale=False, stream=stream))
        self.assertIn("?", stream.getvalue())

    def test_percentage_in_output_for_list(self):
        stream = _stream()
        _exhaust(hype_man(list(range(100)), every=50, finale=False, stream=stream))
        self.assertIn("50%", stream.getvalue())


# ---------------------------------------------------------------------------
# hype_man — hype levels
# ---------------------------------------------------------------------------

class TestHypeManLevels(unittest.TestCase):

    def test_all_valid_levels_accepted(self):
        for level in _VALID_LEVELS:
            stream = _stream()
            _exhaust(hype_man(range(10), every=5, hype_level=level, stream=stream))
            self.assertTrue(len(stream.getvalue()) > 0, f"No output for level {level!r}")

    def test_invalid_level_raises_value_error(self):
        with self.assertRaises(ValueError):
            _exhaust(hype_man(range(10), hype_level="MEGA_HYPE", stream=_stream()))

    def test_level_case_insensitive(self):
        stream = _stream()
        _exhaust(hype_man(range(10), every=5, hype_level="CALM", stream=stream))
        self.assertTrue(len(stream.getvalue()) > 0)

    def test_calm_phrases_are_used(self):
        """Calm phrases should appear in output — verify at least one matches."""
        from pocketknife.hype import _HYPE_CALM
        stream = _stream()
        # Run enough iterations to guarantee hype output
        random_seed = 42
        with patch("random.choice", side_effect=lambda lst: lst[0]):
            _exhaust(hype_man(range(10), every=5, hype_level="calm",
                              finale=False, stream=stream))
        output = stream.getvalue()
        self.assertTrue(any(phrase in output for phrase in _HYPE_CALM))

    def test_unhinged_phrases_are_used(self):
        from pocketknife.hype import _HYPE_UNHINGED
        stream = _stream()
        with patch("random.choice", side_effect=lambda lst: lst[0]):
            _exhaust(hype_man(range(10), every=5, hype_level="unhinged",
                              finale=False, stream=stream))
        output = stream.getvalue()
        self.assertTrue(any(phrase in output for phrase in _HYPE_UNHINGED))


# ---------------------------------------------------------------------------
# hype_man — custom phrases
# ---------------------------------------------------------------------------

class TestHypeManCustomPhrases(unittest.TestCase):

    def test_custom_phrases_used_instead_of_bank(self):
        stream = _stream()
        custom = ["Go team!", "Keep pushing!", "Almost there!"]
        with patch("random.choice", side_effect=lambda lst: lst[0]):
            _exhaust(hype_man(range(10), every=5, custom_phrases=custom,
                              finale=False, stream=stream))
        output = stream.getvalue()
        self.assertIn("Go team!", output)

    def test_custom_phrases_do_not_affect_finale(self):
        """The finale should still come from the built-in bank."""
        from pocketknife.hype import _FINALES_NORMAL
        stream = _stream()
        custom = ["Custom only!"]
        with patch("random.choice", side_effect=lambda lst: lst[0]):
            _exhaust(hype_man(range(5), every=100, custom_phrases=custom,
                              finale=True, stream=stream))
        output = stream.getvalue()
        self.assertIn(_FINALES_NORMAL[0], output)

    def test_single_custom_phrase_repeated(self):
        stream = _stream()
        _exhaust(hype_man(range(30), every=10, custom_phrases=["Only phrase"],
                          finale=False, stream=stream))
        self.assertEqual(stream.getvalue().count("Only phrase"), 3)


# ---------------------------------------------------------------------------
# hype_man — validation
# ---------------------------------------------------------------------------

class TestHypeManValidation(unittest.TestCase):

    def test_every_zero_raises(self):
        with self.assertRaises(ValueError):
            _exhaust(hype_man(range(10), every=0, stream=_stream()))

    def test_every_negative_raises(self):
        with self.assertRaises(ValueError):
            _exhaust(hype_man(range(10), every=-5, stream=_stream()))

    def test_invalid_hype_level_message_helpful(self):
        try:
            _exhaust(hype_man(range(5), hype_level="turbo", stream=_stream()))
        except ValueError as e:
            self.assertIn("turbo", str(e))
            self.assertIn("calm", str(e))

    def test_every_one_is_valid(self):
        stream = _stream()
        result = _exhaust(hype_man([42], every=1, stream=stream))
        self.assertEqual(result, [42])


# ---------------------------------------------------------------------------
# hype_list
# ---------------------------------------------------------------------------

class TestHypeList(unittest.TestCase):

    def test_returns_list(self):
        self.assertIsInstance(hype_list("calm"), list)

    def test_calm_list_non_empty(self):
        self.assertGreater(len(hype_list("calm")), 0)

    def test_unhinged_list_non_empty(self):
        self.assertGreater(len(hype_list("unhinged")), 0)

    def test_all_phrases_are_strings(self):
        for level in _VALID_LEVELS:
            for phrase in hype_list(level):
                self.assertIsInstance(phrase, str)

    def test_custom_phrases_returned_as_is(self):
        custom = ["A", "B", "C"]
        self.assertEqual(hype_list(custom_phrases=custom), custom)

    def test_invalid_level_raises(self):
        with self.assertRaises(ValueError):
            hype_list("legendary")

    def test_returns_copy_not_reference(self):
        """Mutating the returned list must not affect the internal bank."""
        result = hype_list("calm")
        original_len = len(_HYPE_BANKS["calm"][0])
        result.append("INJECTED")
        self.assertEqual(len(_HYPE_BANKS["calm"][0]), original_len)


if __name__ == "__main__":
    unittest.main()
