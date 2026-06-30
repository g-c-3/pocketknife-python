"""Unit tests for pocketknife.lazy_logger."""

import tempfile
import unittest
from pathlib import Path

from pocketknife.lazy_logger import log_to_file


class TestLogToFile(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.log_path = Path(self._tmp.name) / "test.log"

    def tearDown(self):
        self._tmp.cleanup()

    def test_function_still_returns_normally(self):
        @log_to_file(self.log_path)
        def add(a, b):
            return a + b

        self.assertEqual(add(2, 3), 5)

    def test_logs_call_with_positional_args(self):
        @log_to_file(self.log_path)
        def add(a, b):
            return a + b

        add(2, 3)
        content = self.log_path.read_text()
        self.assertIn("add(2, 3)", content)
        self.assertIn("-> 5", content)

    def test_logs_call_with_keyword_args(self):
        @log_to_file(self.log_path)
        def greet(name):
            return f"hi {name}"

        greet(name="sam")
        content = self.log_path.read_text()
        self.assertIn("name='sam'", content)
        self.assertIn("greet(", content)

    def test_creates_parent_directories(self):
        nested_path = Path(self._tmp.name) / "nested" / "dir" / "out.log"

        @log_to_file(nested_path)
        def noop():
            return None

        noop()
        self.assertTrue(nested_path.exists())

    def test_appends_multiple_calls(self):
        @log_to_file(self.log_path)
        def inc(x):
            return x + 1

        inc(1)
        inc(2)
        inc(3)
        lines = self.log_path.read_text().splitlines()
        self.assertEqual(len(lines), 3)

    def test_exception_is_logged_and_reraised(self):
        @log_to_file(self.log_path)
        def boom():
            raise ValueError("kaboom")

        with self.assertRaises(ValueError):
            boom()

        content = self.log_path.read_text()
        self.assertIn("raised ValueError", content)
        self.assertIn("kaboom", content)

    def test_include_result_false_omits_return_value(self):
        @log_to_file(self.log_path, include_result=False)
        def secret():
            return "super-sensitive-value"

        secret()
        content = self.log_path.read_text()
        self.assertNotIn("super-sensitive-value", content)
        self.assertIn("secret()", content)

    def test_include_duration_false_omits_timing(self):
        @log_to_file(self.log_path, include_duration=False)
        def add(a, b):
            return a + b

        add(1, 1)
        content = self.log_path.read_text()
        self.assertNotIn("ms]", content)

    def test_preserves_function_metadata(self):
        @log_to_file(self.log_path)
        def documented_fn(x):
            """A documented function."""
            return x

        self.assertEqual(documented_fn.__name__, "documented_fn")
        self.assertEqual(documented_fn.__doc__, "A documented function.")

    def test_accepts_string_path(self):
        str_path = str(self.log_path)

        @log_to_file(str_path)
        def add(a, b):
            return a + b

        add(1, 2)
        self.assertTrue(self.log_path.exists())

    def test_log_line_includes_timestamp(self):
        @log_to_file(self.log_path)
        def noop():
            return 1

        noop()
        content = self.log_path.read_text()
        # ISO timestamps contain a 'T' separator between date and time.
        self.assertIn("T", content.split(" | ")[0])


if __name__ == "__main__":
    unittest.main()
