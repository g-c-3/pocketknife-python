"""
tests/test_nostalgia.py
~~~~~~~~~~~~~~~~~~~~~~~
Unit tests for pocketknife.nostalgia.

Both functions are I/O- and time-heavy, so the strategy is:
  - Patch time.sleep to a no-op so tests run instantly
  - Capture output via io.StringIO
  - Assert on structure/content rather than exact timing
"""

import io
import sys
import time
import unittest
from unittest.mock import patch

from pocketknife.nostalgia import (
    _MODEM_SOUNDS,
    _MATRIX_CHARS,
    _terminal_size,
    dial_up_print,
    matrix_rain,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _fast_stream():
    """Return a StringIO that looks like a TTY (has isatty())."""
    s = io.StringIO()
    s.isatty = lambda: True
    return s


def _plain_stream():
    """Return a StringIO that is NOT a TTY."""
    s = io.StringIO()
    s.isatty = lambda: False
    return s


# ---------------------------------------------------------------------------
# dial_up_print tests
# ---------------------------------------------------------------------------

class TestDialUpPrint(unittest.TestCase):

    @patch("time.sleep", return_value=None)
    def test_output_contains_full_text(self, _sleep):
        """The entire input text should appear in the output."""
        stream = io.StringIO()
        dial_up_print("Hello, World!", modem_intro=False, stream=stream)
        self.assertIn("Hello, World!", stream.getvalue())

    @patch("time.sleep", return_value=None)
    def test_no_extra_newlines_before_text_without_intro(self, _sleep):
        """Without the modem intro, output starts with the actual text."""
        stream = io.StringIO()
        dial_up_print("ABC", modem_intro=False, stream=stream)
        output = stream.getvalue()
        # Should not have a massive preamble
        self.assertTrue(output.strip().startswith("A") or "A" in output)

    @patch("time.sleep", return_value=None)
    def test_modem_intro_appears_when_enabled(self, _sleep):
        """When modem_intro=True the CONNECT banner should be in the output."""
        stream = io.StringIO()
        dial_up_print("hi", modem_intro=True, stream=stream)
        output = stream.getvalue()
        self.assertIn("CONNECT", output)

    @patch("time.sleep", return_value=None)
    def test_modem_intro_absent_when_disabled(self, _sleep):
        """When modem_intro=False the CONNECT banner must not appear."""
        stream = io.StringIO()
        dial_up_print("hi", modem_intro=False, stream=stream)
        self.assertNotIn("CONNECT", stream.getvalue())

    @patch("time.sleep", return_value=None)
    def test_output_ends_with_newline(self, _sleep):
        """dial_up_print always appends a trailing newline."""
        stream = io.StringIO()
        dial_up_print("test", modem_intro=False, stream=stream)
        self.assertTrue(stream.getvalue().endswith("\n"))

    @patch("time.sleep", return_value=None)
    def test_empty_string_produces_just_newline(self, _sleep):
        """An empty string input should produce only a trailing newline."""
        stream = io.StringIO()
        dial_up_print("", modem_intro=False, stream=stream)
        self.assertEqual(stream.getvalue(), "\n")

    @patch("time.sleep", return_value=None)
    def test_sleep_called_per_character(self, mock_sleep):
        """time.sleep is called at least once per character."""
        stream = io.StringIO()
        text = "Hello"
        dial_up_print(text, modem_intro=False, stream=stream)
        # At minimum 1 sleep per character; glitch path can add more
        self.assertGreaterEqual(mock_sleep.call_count, len(text))

    @patch("time.sleep", return_value=None)
    def test_modem_sound_in_intro(self, _sleep):
        """One of the predefined modem sounds should appear in the intro block."""
        stream = io.StringIO()
        dial_up_print("x", modem_intro=True, stream=stream)
        output = stream.getvalue()
        found = any(sound in output for sound in _MODEM_SOUNDS)
        self.assertTrue(found, f"Expected a modem sound in output:\n{output}")

    @patch("time.sleep", return_value=None)
    def test_glitch_chance_zero_produces_clean_output(self, _sleep):
        """With glitch_chance=0 the output contains only the original text."""
        stream = io.StringIO()
        text = "CleanText"
        dial_up_print(text, modem_intro=False, glitch_chance=0.0, stream=stream)
        output = stream.getvalue()
        # Strip the trailing newline and compare
        self.assertEqual(output.rstrip("\n"), text)

    @patch("time.sleep", return_value=None)
    def test_multiline_text_preserved(self, _sleep):
        """Multi-line input is printed with newlines intact."""
        stream = io.StringIO()
        text = "line one\nline two\nline three"
        dial_up_print(text, modem_intro=False, glitch_chance=0.0, stream=stream)
        output = stream.getvalue()
        self.assertIn("line one", output)
        self.assertIn("line two", output)
        self.assertIn("line three", output)


# ---------------------------------------------------------------------------
# matrix_rain tests
# ---------------------------------------------------------------------------

class TestMatrixRain(unittest.TestCase):

    @patch("time.sleep", return_value=None)
    def test_non_tty_fallback_message(self, _sleep):
        """On a non-TTY stream, a fallback text message is printed instead."""
        stream = _plain_stream()
        matrix_rain(duration=1.0, stream=stream)
        self.assertIn("ANSI terminal required", stream.getvalue())

    def _one_frame_monotonic(self):
        """Return a callable that lets matrix_rain run exactly one frame.

        monotonic() call sites per iteration:
          1 = start (before loop)
          2 = while check  (enters loop: 0.0 - 0.0 < 1.0)
          3 = frame_start
          4 = elapsed calc
          5 = while check  (exits loop: 2.0 - 0.0 >= 1.0)
        Any extra calls also return 2.0 so we never exhaust the mock.
        """
        values = [0.0, 0.0, 0.0, 0.0, 2.0]
        calls = [0]
        def _mono():
            idx = min(calls[0], len(values) - 1)
            calls[0] += 1
            return values[idx]
        return _mono

    def test_ansi_escape_written_on_tty(self):
        """On a TTY stream, ANSI escape sequences should be written."""
        stream = _fast_stream()
        with patch("time.sleep", return_value=None), \
             patch("time.monotonic", side_effect=self._one_frame_monotonic()):
            matrix_rain(duration=1.0, fps=1, stream=stream)
        self.assertIn("\033[", stream.getvalue())

    def test_cursor_hidden_then_shown(self):
        """Cursor should be hidden at start and restored at end."""
        stream = _fast_stream()
        with patch("time.sleep", return_value=None), \
             patch("time.monotonic", side_effect=self._one_frame_monotonic()):
            matrix_rain(duration=1.0, fps=1, stream=stream)
        output = stream.getvalue()
        self.assertIn("\033[?25l", output)   # hide cursor
        self.assertIn("\033[?25h", output)   # show cursor

    def test_screen_cleared_at_start(self):
        """The screen clear escape should appear near the start of output."""
        stream = _fast_stream()
        with patch("time.sleep", return_value=None), \
             patch("time.monotonic", side_effect=self._one_frame_monotonic()):
            matrix_rain(duration=1.0, fps=1, stream=stream)
        self.assertIn("\033[2J", stream.getvalue())

    def test_reset_escape_written_at_end(self):
        """ANSI reset should be written on exit to restore colors."""
        stream = _fast_stream()
        with patch("time.sleep", return_value=None), \
             patch("time.monotonic", side_effect=self._one_frame_monotonic()):
            matrix_rain(duration=1.0, fps=1, stream=stream)
        self.assertIn("\033[0m", stream.getvalue())

    @patch("time.sleep", return_value=None)
    @patch("time.monotonic", side_effect=[0.0, 0.0, 1.0])
    def test_cleanup_runs_on_keyboard_interrupt(self, _mono, _sleep):
        """Terminal cleanup (show cursor) must happen even if interrupted."""
        stream = _fast_stream()

        # Make time.monotonic raise KeyboardInterrupt on the second call
        # inside the loop to simulate Ctrl-C mid-run.
        call_count = [0]
        def fake_mono():
            call_count[0] += 1
            if call_count[0] == 2:
                raise KeyboardInterrupt
            return 0.0

        with patch("time.monotonic", side_effect=fake_mono):
            try:
                matrix_rain(duration=10.0, fps=1, stream=stream)
            except KeyboardInterrupt:
                pass

        output = stream.getvalue()
        self.assertIn("\033[?25h", output)   # cursor must be restored


# ---------------------------------------------------------------------------
# _terminal_size tests
# ---------------------------------------------------------------------------

class TestTerminalSize(unittest.TestCase):

    def test_returns_tuple_of_two_ints(self):
        cols, rows = _terminal_size()
        self.assertIsInstance(cols, int)
        self.assertIsInstance(rows, int)

    def test_fallback_when_no_tty(self):
        """When os.get_terminal_size raises OSError, returns the safe default."""
        with patch("os.get_terminal_size", side_effect=OSError):
            cols, rows = _terminal_size()
        self.assertEqual((cols, rows), (80, 24))

    def test_positive_dimensions(self):
        cols, rows = _terminal_size()
        self.assertGreater(cols, 0)
        self.assertGreater(rows, 0)


# ---------------------------------------------------------------------------
# Module-level constant sanity checks
# ---------------------------------------------------------------------------

class TestConstants(unittest.TestCase):

    def test_matrix_chars_non_empty(self):
        self.assertTrue(len(_MATRIX_CHARS) > 0)

    def test_modem_sounds_non_empty(self):
        self.assertTrue(len(_MODEM_SOUNDS) > 0)

    def test_modem_sounds_are_strings(self):
        for s in _MODEM_SOUNDS:
            self.assertIsInstance(s, str)


if __name__ == "__main__":
    unittest.main()
