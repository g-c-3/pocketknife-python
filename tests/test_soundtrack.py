"""
tests/test_soundtrack.py
~~~~~~~~~~~~~~~~~~~~~~~~
Unit tests for pocketknife.soundtrack.
"""

import io
import unittest
from unittest.mock import patch

from pocketknife.soundtrack import (
    _duration_commentary,
    _format_elapsed,
    run_with_music,
)


def _stream():
    return io.StringIO()


# ---------------------------------------------------------------------------
# _duration_commentary
# ---------------------------------------------------------------------------

class TestDurationCommentary(unittest.TestCase):

    def test_returns_string(self):
        self.assertIsInstance(_duration_commentary(5), str)

    def test_very_short_duration(self):
        self.assertIn("track title", _duration_commentary(0.1))

    def test_short_duration(self):
        self.assertIn("intro", _duration_commentary(2))

    def test_first_verse_duration(self):
        self.assertIn("first verse", _duration_commentary(10))

    def test_medium_duration(self):
        self.assertIn("chorus", _duration_commentary(20))

    def test_long_duration(self):
        self.assertIn("whole song", _duration_commentary(120))

    def test_very_long_duration(self):
        self.assertIn("album", _duration_commentary(700))

    def test_boundary_values_do_not_error(self):
        for val in [0, 1, 5, 15, 30, 60, 180, 600, 10000]:
            result = _duration_commentary(val)
            self.assertIsInstance(result, str)
            self.assertTrue(len(result) > 0)


# ---------------------------------------------------------------------------
# _format_elapsed
# ---------------------------------------------------------------------------

class TestFormatElapsed(unittest.TestCase):

    def test_seconds_format(self):
        self.assertEqual(_format_elapsed(3.456), "3.46s")

    def test_sub_second_format(self):
        self.assertEqual(_format_elapsed(0.001), "0.00s")

    def test_minutes_format(self):
        result = _format_elapsed(125.5)
        self.assertIn("m", result)
        self.assertIn("2", result)  # 2 minutes

    def test_exactly_sixty_seconds_uses_minute_format(self):
        result = _format_elapsed(60.0)
        self.assertIn("1m", result)

    def test_just_under_sixty_uses_second_format(self):
        result = _format_elapsed(59.99)
        self.assertTrue(result.endswith("s"))
        self.assertNotIn("m", result)


# ---------------------------------------------------------------------------
# run_with_music — success path
# ---------------------------------------------------------------------------

class TestRunWithMusicSuccess(unittest.TestCase):

    def test_return_value_passed_through(self):
        stream = _stream()
        result = run_with_music(lambda a, b: a + b, "http://music.example", 2, 3, stream=stream)
        self.assertEqual(result, 5)

    def test_url_appears_in_output(self):
        stream = _stream()
        run_with_music(lambda: 1, "http://music.example/track123", stream=stream)
        self.assertIn("http://music.example/track123", stream.getvalue())

    def test_function_name_appears_in_output(self):
        def my_special_function():
            return "ok"

        stream = _stream()
        run_with_music(my_special_function, "http://music.example", stream=stream)
        self.assertIn("my_special_function", stream.getvalue())

    def test_success_emoji_present(self):
        stream = _stream()
        run_with_music(lambda: None, "http://music.example", stream=stream)
        self.assertIn("✅", stream.getvalue())

    def test_now_playing_emoji_present(self):
        stream = _stream()
        run_with_music(lambda: None, "http://music.example", stream=stream)
        self.assertIn("🎵", stream.getvalue())

    def test_kwargs_forwarded(self):
        stream = _stream()

        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        result = run_with_music(greet, "http://music.example", "World", greeting="Hi", stream=stream)
        self.assertEqual(result, "Hi, World!")

    def test_lambda_uses_repr_for_name(self):
        """Lambdas have __name__ == '<lambda>', which should still work fine."""
        stream = _stream()
        run_with_music(lambda: 42, "http://music.example", stream=stream)
        self.assertIn("<lambda>", stream.getvalue())

    def test_elapsed_time_reported(self):
        stream = _stream()
        run_with_music(lambda: None, "http://music.example", stream=stream)
        output = stream.getvalue()
        self.assertIn("Done in", output)


# ---------------------------------------------------------------------------
# run_with_music — failure path
# ---------------------------------------------------------------------------

class TestRunWithMusicFailure(unittest.TestCase):

    def test_exception_propagates(self):
        stream = _stream()

        def boom():
            raise ValueError("kaboom")

        with self.assertRaises(ValueError):
            run_with_music(boom, "http://music.example", stream=stream)

    def test_failure_message_printed_before_reraise(self):
        stream = _stream()

        def boom():
            raise RuntimeError("nope")

        try:
            run_with_music(boom, "http://music.example", stream=stream)
        except RuntimeError:
            pass

        output = stream.getvalue()
        self.assertIn("💥", output)
        self.assertIn("Failed after", output)

    def test_url_still_printed_on_failure(self):
        stream = _stream()

        def boom():
            raise RuntimeError("nope")

        try:
            run_with_music(boom, "http://music.example/track999", stream=stream)
        except RuntimeError:
            pass

        self.assertIn("http://music.example/track999", stream.getvalue())

    def test_original_exception_type_preserved(self):
        stream = _stream()

        def type_error_fn():
            raise TypeError("wrong type")

        with self.assertRaises(TypeError):
            run_with_music(type_error_fn, "http://music.example", stream=stream)


# ---------------------------------------------------------------------------
# Default stream behavior
# ---------------------------------------------------------------------------

class TestRunWithMusicDefaultStream(unittest.TestCase):

    def test_uses_sys_stdout_when_stream_not_given(self):
        """Without an explicit stream, output should go to sys.stdout."""
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            result = run_with_music(lambda: "ok", "http://music.example")
        self.assertEqual(result, "ok")
        self.assertIn("🎵", mock_stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
