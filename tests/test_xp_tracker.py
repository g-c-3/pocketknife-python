"""Unit tests for pocketknife.xp_tracker"""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pocketknife.xp_tracker import (  # noqa: E402
    award_xp,
    get_stats,
    level_for_xp,
    reset_xp,
)


class TestLevelForXp(unittest.TestCase):
    def test_zero_xp_is_level_one(self):
        self.assertEqual(level_for_xp(0), 1)

    def test_just_below_threshold_stays_level_one(self):
        self.assertEqual(level_for_xp(99), 1)

    def test_exact_threshold_reaches_level_two(self):
        self.assertEqual(level_for_xp(100), 2)

    def test_second_threshold(self):
        # level 2->3 costs 150, so 100 + 150 = 250 total for level 3
        self.assertEqual(level_for_xp(249), 2)
        self.assertEqual(level_for_xp(250), 3)

    def test_large_xp_reaches_high_level(self):
        self.assertGreaterEqual(level_for_xp(10_000), 5)

    def test_negative_xp_raises(self):
        with self.assertRaises(ValueError):
            level_for_xp(-1)


class TestXpFileIsolation(unittest.TestCase):
    """Every test gets its own throwaway XP file so tests never interfere."""

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.xp_path = Path(self.tmpdir.name) / "xp.json"

    def tearDown(self):
        self.tmpdir.cleanup()


class TestGetStats(TestXpFileIsolation):
    def test_stats_on_fresh_file(self):
        stats = get_stats(self.xp_path)
        self.assertEqual(stats["xp"], 0)
        self.assertEqual(stats["level"], 1)
        self.assertEqual(stats["xp_into_level"], 0)
        self.assertEqual(stats["xp_for_next_level"], 100)

    def test_stats_does_not_create_file(self):
        get_stats(self.xp_path)
        self.assertFalse(self.xp_path.exists())

    def test_stats_reads_existing_file(self):
        @award_xp(150, path=self.xp_path)
        def dummy():
            return True

        dummy()
        stats = get_stats(self.xp_path)
        self.assertEqual(stats["xp"], 150)
        self.assertEqual(stats["level"], 2)


class TestResetXp(TestXpFileIsolation):
    def test_reset_zeroes_existing_xp(self):
        @award_xp(500, path=self.xp_path)
        def dummy():
            return True

        dummy()
        self.assertGreater(get_stats(self.xp_path)["xp"], 0)

        reset_xp(self.xp_path)
        self.assertEqual(get_stats(self.xp_path)["xp"], 0)

    def test_reset_on_nonexistent_file_creates_zero_state(self):
        reset_xp(self.xp_path)
        self.assertTrue(self.xp_path.exists())
        self.assertEqual(get_stats(self.xp_path)["xp"], 0)


class TestAwardXpDecorator(TestXpFileIsolation):
    def test_successful_call_awards_points(self):
        @award_xp(40, path=self.xp_path)
        def passing():
            return "ok"

        passing()
        self.assertEqual(get_stats(self.xp_path)["xp"], 40)

    def test_multiple_calls_accumulate(self):
        @award_xp(25, path=self.xp_path)
        def passing():
            return "ok"

        for _ in range(4):
            passing()
        self.assertEqual(get_stats(self.xp_path)["xp"], 100)

    def test_raising_function_awards_no_xp(self):
        @award_xp(100, path=self.xp_path)
        def failing():
            raise AssertionError("boom")

        with self.assertRaises(AssertionError):
            failing()
        self.assertEqual(get_stats(self.xp_path)["xp"], 0)

    def test_return_value_passes_through(self):
        @award_xp(10, path=self.xp_path)
        def adds(a, b):
            return a + b

        self.assertEqual(adds(2, 3), 5)

    def test_args_and_kwargs_forwarded(self):
        @award_xp(10, path=self.xp_path)
        def greet(name, greeting="hello"):
            return f"{greeting}, {name}"

        self.assertEqual(greet("duck", greeting="quack"), "quack, duck")

    def test_level_up_prints_message(self, ):
        @award_xp(100, path=self.xp_path)
        def passing():
            return True

        import io
        import contextlib

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            passing()
        output = buf.getvalue()
        self.assertIn("LEVEL UP", output)

    def test_no_level_up_message_when_level_unchanged(self):
        @award_xp(10, path=self.xp_path)
        def passing():
            return True

        import io
        import contextlib

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            passing()
        output = buf.getvalue()
        self.assertNotIn("LEVEL UP", output)

    def test_zero_points_raises(self):
        with self.assertRaises(ValueError):
            award_xp(0, path=self.xp_path)

    def test_negative_points_raises(self):
        with self.assertRaises(ValueError):
            award_xp(-5, path=self.xp_path)

    def test_wraps_preserves_function_metadata(self):
        @award_xp(10, path=self.xp_path)
        def documented():
            """A docstring."""
            return None

        self.assertEqual(documented.__name__, "documented")
        self.assertEqual(documented.__doc__, "A docstring.")

    def test_independent_paths_dont_interfere(self):
        other_path = Path(self.tmpdir.name) / "other.json"

        @award_xp(50, path=self.xp_path)
        def a():
            return True

        @award_xp(50, path=other_path)
        def b():
            return True

        a()
        self.assertEqual(get_stats(self.xp_path)["xp"], 50)
        self.assertEqual(get_stats(other_path)["xp"], 0)


class TestCorruptFileHandling(TestXpFileIsolation):
    def test_corrupt_json_falls_back_to_zero(self):
        self.xp_path.parent.mkdir(parents=True, exist_ok=True)
        self.xp_path.write_text("not valid json{{{", encoding="utf-8")

        stats = get_stats(self.xp_path)
        self.assertEqual(stats["xp"], 0)


if __name__ == "__main__":
    unittest.main()
