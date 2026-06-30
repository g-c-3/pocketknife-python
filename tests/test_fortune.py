"""
tests/test_fortune.py
~~~~~~~~~~~~~~~~~~~~~
Unit tests for pocketknife.fortune.
"""

import io
import sys
import unittest
from unittest.mock import patch

from pocketknife.fortune import _PROVERBS, _random_proverb, fortune_once, zen_crash


# ---------------------------------------------------------------------------
# _random_proverb
# ---------------------------------------------------------------------------

class TestRandomProverb(unittest.TestCase):

    def test_returns_string(self):
        self.assertIsInstance(_random_proverb(), str)

    def test_returns_one_of_known_proverbs(self):
        proverb = _random_proverb()
        self.assertIn(proverb, _PROVERBS)

    def test_proverbs_list_non_empty(self):
        self.assertTrue(len(_PROVERBS) > 0)

    def test_varies_over_many_calls(self):
        """Across many calls, more than one distinct proverb should appear."""
        seen = {_random_proverb() for _ in range(100)}
        self.assertGreater(len(seen), 1)


# ---------------------------------------------------------------------------
# fortune_once
# ---------------------------------------------------------------------------

class TestFortuneOnce(unittest.TestCase):

    def test_returns_string(self):
        self.assertIsInstance(fortune_once(), str)

    def test_starts_with_lotus_emoji(self):
        self.assertTrue(fortune_once().startswith("🪷"))

    def test_contains_a_known_proverb(self):
        result = fortune_once()
        matches = any(p in result for p in _PROVERBS)
        self.assertTrue(matches)

    def test_wrapped_in_quotes(self):
        result = fortune_once()
        self.assertIn('"', result)

    def test_deterministic_with_patched_random(self):
        with patch("pocketknife.fortune._random_proverb", return_value="Test proverb."):
            self.assertEqual(fortune_once(), '🪷 "Test proverb."')


# ---------------------------------------------------------------------------
# zen_crash
# ---------------------------------------------------------------------------

class TestZenCrash(unittest.TestCase):

    def setUp(self):
        self._original_hook = sys.excepthook

    def tearDown(self):
        sys.excepthook = self._original_hook

    def test_registers_custom_excepthook(self):
        original = sys.excepthook
        zen_crash()
        self.assertIsNot(sys.excepthook, original)

    def test_hook_writes_proverb_line(self):
        stream = io.StringIO()
        zen_crash(stream=stream)

        try:
            raise ValueError("test crash")
        except ValueError:
            exc_type, exc_value, exc_tb = sys.exc_info()
            sys.excepthook(exc_type, exc_value, exc_tb)

        output = stream.getvalue()
        self.assertIn("🪷", output)

    def test_hook_writes_traceback_before_proverb(self):
        stream = io.StringIO()
        zen_crash(stream=stream)

        try:
            raise RuntimeError("kaboom")
        except RuntimeError:
            exc_type, exc_value, exc_tb = sys.exc_info()
            sys.excepthook(exc_type, exc_value, exc_tb)

        output = stream.getvalue()
        proverb_pos = output.find("🪷")
        traceback_pos = output.find("RuntimeError")
        self.assertGreater(proverb_pos, traceback_pos)

    def test_hook_proverb_is_from_known_list(self):
        stream = io.StringIO()
        zen_crash(stream=stream)

        try:
            raise KeyError("missing")
        except KeyError:
            exc_type, exc_value, exc_tb = sys.exc_info()
            sys.excepthook(exc_type, exc_value, exc_tb)

        output = stream.getvalue()
        matches = any(p in output for p in _PROVERBS)
        self.assertTrue(matches)

    def test_does_not_raise_for_exception_with_no_message(self):
        stream = io.StringIO()
        zen_crash(stream=stream)

        try:
            raise Exception()
        except Exception:
            exc_type, exc_value, exc_tb = sys.exc_info()
            # Should not raise
            sys.excepthook(exc_type, exc_value, exc_tb)

        self.assertIn("🪷", stream.getvalue())

    def test_default_stream_param_is_sys_stderr(self):
        """The 'stream' parameter should default to sys.stderr."""
        import inspect
        sig = inspect.signature(zen_crash)
        self.assertIs(sig.parameters["stream"].default, sys.stderr)


if __name__ == "__main__":
    unittest.main()
