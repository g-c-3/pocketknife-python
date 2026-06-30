"""
tests/test_pet.py
~~~~~~~~~~~~~~~~~~
Unit tests for pocketknife.pet.

All tests use a temporary directory for state files so the real
~/.pocketknife_bird.json on the test-runner's machine is never touched.
"""

import io
import json
import time
import unittest
from pathlib import Path

from pocketknife.pet import (
    _SECONDS_PER_DAY,
    _days_since,
    _load_state,
    _mood_for_days,
    _save_state,
    bird_status,
    feed_the_bird,
)


def _stream():
    return io.StringIO()


class TempStateMixin:
    """Provides a fresh temp-dir state path per test."""

    def setUp(self):
        import tempfile
        self._tmpdir = tempfile.TemporaryDirectory()
        self.state_path = Path(self._tmpdir.name) / "bird.json"

    def tearDown(self):
        self._tmpdir.cleanup()


# ---------------------------------------------------------------------------
# _days_since
# ---------------------------------------------------------------------------

class TestDaysSince(unittest.TestCase):

    def test_none_timestamp_returns_none(self):
        self.assertIsNone(_days_since(None, time.time()))

    def test_same_timestamp_returns_zero(self):
        now = time.time()
        self.assertAlmostEqual(_days_since(now, now), 0.0, places=5)

    def test_one_day_elapsed(self):
        now = time.time()
        one_day_ago = now - _SECONDS_PER_DAY
        self.assertAlmostEqual(_days_since(one_day_ago, now), 1.0, places=5)

    def test_seven_days_elapsed(self):
        now = time.time()
        week_ago = now - (7 * _SECONDS_PER_DAY)
        self.assertAlmostEqual(_days_since(week_ago, now), 7.0, places=5)


# ---------------------------------------------------------------------------
# _mood_for_days
# ---------------------------------------------------------------------------

class TestMoodForDays(unittest.TestCase):

    def test_none_days_is_newborn(self):
        mood, _ = _mood_for_days(None)
        self.assertEqual(mood, "newborn")

    def test_zero_days_is_ecstatic(self):
        mood, _ = _mood_for_days(0)
        self.assertEqual(mood, "ecstatic")

    def test_half_day_is_ecstatic(self):
        mood, _ = _mood_for_days(0.5)
        self.assertEqual(mood, "ecstatic")

    def test_one_day_is_content(self):
        mood, _ = _mood_for_days(1)
        self.assertEqual(mood, "content")

    def test_three_days_is_lonely(self):
        mood, _ = _mood_for_days(3)
        self.assertEqual(mood, "lonely")

    def test_seven_days_is_sulking(self):
        mood, _ = _mood_for_days(7)
        self.assertEqual(mood, "sulking")

    def test_fourteen_days_is_forlorn(self):
        mood, _ = _mood_for_days(14)
        self.assertEqual(mood, "forlorn")

    def test_thirty_days_is_abandoned(self):
        mood, _ = _mood_for_days(30)
        self.assertEqual(mood, "abandoned")

    def test_very_long_neglect_still_abandoned(self):
        mood, _ = _mood_for_days(365)
        self.assertEqual(mood, "abandoned")

    def test_message_is_nonempty_string(self):
        _, message = _mood_for_days(2)
        self.assertIsInstance(message, str)
        self.assertTrue(len(message) > 0)


# ---------------------------------------------------------------------------
# _load_state / _save_state
# ---------------------------------------------------------------------------

class TestLoadSaveState(TempStateMixin, unittest.TestCase):

    def test_load_missing_file_returns_default(self):
        state = _load_state(self.state_path)
        self.assertIsNone(state["last_fed"])
        self.assertEqual(state["feed_count"], 0)

    def test_save_then_load_round_trip(self):
        original = {"last_fed": 12345.0, "feed_count": 3, "created": 100.0}
        ok = _save_state(self.state_path, original)
        self.assertTrue(ok)

        loaded = _load_state(self.state_path)
        self.assertEqual(loaded["last_fed"], 12345.0)
        self.assertEqual(loaded["feed_count"], 3)

    def test_corrupt_json_falls_back_to_default(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, "w") as f:
            f.write("{not valid json!!!")

        state = _load_state(self.state_path)
        self.assertIsNone(state["last_fed"])
        self.assertEqual(state["feed_count"], 0)

    def test_malformed_dict_missing_key_falls_back(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_path, "w") as f:
            json.dump({"totally": "unrelated"}, f)

        state = _load_state(self.state_path)
        self.assertIsNone(state["last_fed"])

    def test_save_creates_parent_directories(self):
        nested = self.state_path.parent / "nested" / "deeper" / "bird.json"
        ok = _save_state(nested, {"last_fed": None, "feed_count": 0})
        self.assertTrue(ok)
        self.assertTrue(nested.exists())


# ---------------------------------------------------------------------------
# feed_the_bird
# ---------------------------------------------------------------------------

class TestFeedTheBird(TempStateMixin, unittest.TestCase):

    def test_returns_dict_with_expected_keys(self):
        stream = _stream()
        result = feed_the_bird(state_path=self.state_path, stream=stream)
        for key in ("last_fed", "feed_count", "mood", "days_since_last_feeding"):
            self.assertIn(key, result)

    def test_first_feeding_is_newborn(self):
        stream = _stream()
        result = feed_the_bird(state_path=self.state_path, stream=stream)
        self.assertEqual(result["mood"], "newborn")
        self.assertIn("hatched", stream.getvalue())

    def test_feed_count_increments(self):
        feed_the_bird(state_path=self.state_path, stream=_stream())
        result = feed_the_bird(state_path=self.state_path, stream=_stream())
        self.assertEqual(result["feed_count"], 2)

    def test_state_persists_to_disk(self):
        feed_the_bird(state_path=self.state_path, stream=_stream())
        self.assertTrue(self.state_path.exists())
        with open(self.state_path) as f:
            data = json.load(f)
        self.assertEqual(data["feed_count"], 1)

    def test_immediate_refeed_is_ecstatic(self):
        feed_the_bird(state_path=self.state_path, stream=_stream())
        # Feed again at essentially the same timestamp
        now = time.time()
        result = feed_the_bird(state_path=self.state_path, stream=_stream(), _now=now)
        self.assertIn(result["mood"], ("ecstatic", "newborn"))

    def test_feeding_after_simulated_gap_shows_correct_mood(self):
        base_time = time.time()
        feed_the_bird(state_path=self.state_path, stream=_stream(), _now=base_time)

        five_days_later = base_time + (5 * _SECONDS_PER_DAY)
        stream = _stream()
        result = feed_the_bird(state_path=self.state_path, stream=stream, _now=five_days_later)
        self.assertEqual(result["mood"], "lonely")

    def test_feeding_resets_mood_to_ecstatic_next_check(self):
        base_time = time.time()
        feed_the_bird(state_path=self.state_path, stream=_stream(), _now=base_time)

        ten_days_later = base_time + (10 * _SECONDS_PER_DAY)
        feed_the_bird(state_path=self.state_path, stream=_stream(), _now=ten_days_later)

        # Immediately after feeding, status check should show ecstatic again
        status = bird_status(state_path=self.state_path, _now=ten_days_later)
        self.assertEqual(status["mood"], "ecstatic")

    def test_days_ago_message_shown_for_neglected_bird(self):
        base_time = time.time()
        feed_the_bird(state_path=self.state_path, stream=_stream(), _now=base_time)

        three_days_later = base_time + (3 * _SECONDS_PER_DAY)
        stream = _stream()
        feed_the_bird(state_path=self.state_path, stream=stream, _now=three_days_later)
        self.assertIn("3 days ago", stream.getvalue())

    def test_no_days_ago_message_on_same_day_feeding(self):
        base_time = time.time()
        feed_the_bird(state_path=self.state_path, stream=_stream(), _now=base_time)

        stream = _stream()
        feed_the_bird(state_path=self.state_path, stream=stream, _now=base_time + 10)
        self.assertNotIn("days ago", stream.getvalue())
        self.assertNotIn("day ago", stream.getvalue())

    def test_singular_day_grammar(self):
        base_time = time.time()
        feed_the_bird(state_path=self.state_path, stream=_stream(), _now=base_time)

        one_day_later = base_time + _SECONDS_PER_DAY + 5  # just over 1 day
        stream = _stream()
        feed_the_bird(state_path=self.state_path, stream=stream, _now=one_day_later)
        self.assertIn("1 day ago", stream.getvalue())
        self.assertNotIn("1 days ago", stream.getvalue())


# ---------------------------------------------------------------------------
# bird_status
# ---------------------------------------------------------------------------

class TestBirdStatus(TempStateMixin, unittest.TestCase):

    def test_status_on_never_fed_bird(self):
        status = bird_status(state_path=self.state_path)
        self.assertEqual(status["mood"], "newborn")
        self.assertEqual(status["feed_count"], 0)

    def test_status_does_not_modify_state_file(self):
        feed_the_bird(state_path=self.state_path, stream=_stream())
        with open(self.state_path) as f:
            before = f.read()

        bird_status(state_path=self.state_path)

        with open(self.state_path) as f:
            after = f.read()
        self.assertEqual(before, after)

    def test_status_reflects_feed_count(self):
        feed_the_bird(state_path=self.state_path, stream=_stream())
        feed_the_bird(state_path=self.state_path, stream=_stream())
        status = bird_status(state_path=self.state_path)
        self.assertEqual(status["feed_count"], 2)

    def test_status_reflects_elapsed_neglect(self):
        base_time = time.time()
        feed_the_bird(state_path=self.state_path, stream=_stream(), _now=base_time)

        two_weeks_later = base_time + (14 * _SECONDS_PER_DAY)
        status = bird_status(state_path=self.state_path, _now=two_weeks_later)
        self.assertEqual(status["mood"], "forlorn")


if __name__ == "__main__":
    unittest.main()
