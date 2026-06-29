"""
Tests for pocketknife.dev_oracle
"""

import sys
import os
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pocketknife.dev_oracle import (
    should_i_deploy,
    code_review_roulette,
    _FRIDAY,
    _SATURDAY,
    _SUNDAY,
    _MONDAY,
    _FRIDAY_DANGER_HOUR,
)

# ---------------------------------------------------------------------------
# Helpers — fixed datetimes for deterministic tests
# ---------------------------------------------------------------------------

def _dt(weekday_offset, hour, minute=0):
    """
    Return a datetime on a specific weekday.
    weekday_offset: 0=Mon, 1=Tue, 2=Wed, 3=Thu, 4=Fri, 5=Sat, 6=Sun
    We anchor on 2024-03-11 (Monday) and offset from there.
    """
    anchor = datetime.datetime(2024, 3, 11)  # known Monday
    return anchor + datetime.timedelta(days=weekday_offset, hours=hour, minutes=minute)


TUESDAY_MORNING = _dt(1, 10)      # Tue 10:00 — blessed
WEDNESDAY_NOON  = _dt(2, 12)      # Wed 12:00 — blessed
THURSDAY_EOD    = _dt(3, 16)      # Thu 16:00 — blessed
FRIDAY_MORNING  = _dt(4, 9)       # Fri 09:00 — still blessed
FRIDAY_NOON     = _dt(4, 12, 59)  # Fri 12:59 — last safe minute
FRIDAY_DANGER   = _dt(4, 13)      # Fri 13:00 — cursed starts here
FRIDAY_LATE     = _dt(4, 17)      # Fri 17:00 — deep in the curse
SATURDAY_NOON   = _dt(5, 12)      # Sat 12:00 — weekend
SUNDAY_MORNING  = _dt(6, 8)       # Sun 08:00 — weekend
MONDAY_EARLY    = _dt(7, 7)       # Mon 07:00 — next Mon, cautious
MONDAY_READY    = _dt(7, 9)       # Mon 09:00 — fine


# ===========================================================================
# should_i_deploy
# ===========================================================================

class TestShouldIDeploy:

    # --- Return type ---

    def test_returns_string(self):
        assert isinstance(should_i_deploy(TUESDAY_MORNING), str)

    def test_returns_non_empty_string(self):
        assert len(should_i_deploy(TUESDAY_MORNING).strip()) > 0

    # --- Blessed times (weekday, not Friday PM) ---

    def test_tuesday_morning_blessed(self):
        result = should_i_deploy(TUESDAY_MORNING)
        assert result.startswith("✅")

    def test_wednesday_noon_blessed(self):
        result = should_i_deploy(WEDNESDAY_NOON)
        assert result.startswith("✅")

    def test_thursday_eod_blessed(self):
        result = should_i_deploy(THURSDAY_EOD)
        assert result.startswith("✅")

    def test_friday_morning_still_blessed(self):
        result = should_i_deploy(FRIDAY_MORNING)
        assert result.startswith("✅")

    def test_friday_just_before_danger_blessed(self):
        result = should_i_deploy(FRIDAY_NOON)
        assert result.startswith("✅")

    def test_monday_after_9am_blessed(self):
        result = should_i_deploy(MONDAY_READY)
        assert result.startswith("✅")

    # --- Cursed times (Friday PM) ---

    def test_friday_at_danger_hour_cursed(self):
        result = should_i_deploy(FRIDAY_DANGER)
        assert result.startswith("🚨")

    def test_friday_late_afternoon_cursed(self):
        result = should_i_deploy(FRIDAY_LATE)
        assert result.startswith("🚨")

    def test_friday_midnight_not_cursed(self):
        # Friday at midnight (00:00) is before the danger threshold
        friday_midnight = _dt(4, 0)
        result = should_i_deploy(friday_midnight)
        assert result.startswith("✅")

    # --- Weekend ---

    def test_saturday_weekend_warning(self):
        result = should_i_deploy(SATURDAY_NOON)
        assert result.startswith("😬")

    def test_sunday_weekend_warning(self):
        result = should_i_deploy(SUNDAY_MORNING)
        assert result.startswith("😬")

    # --- Monday caution ---

    def test_monday_early_caution(self):
        result = should_i_deploy(MONDAY_EARLY)
        assert result.startswith("⚠️")

    def test_monday_8am_still_caution(self):
        monday_8am = _dt(7, 8, 59)
        result = should_i_deploy(monday_8am)
        assert result.startswith("⚠️")

    # --- Default uses now ---

    def test_no_argument_returns_string(self):
        result = should_i_deploy()
        assert isinstance(result, str)
        assert len(result) > 0

    # --- Boundary: exactly at danger hour ---

    def test_exact_danger_boundary(self):
        exact = _dt(4, _FRIDAY_DANGER_HOUR, 0)
        result = should_i_deploy(exact)
        assert result.startswith("🚨")

    def test_one_minute_before_danger(self):
        before = _dt(4, _FRIDAY_DANGER_HOUR - 1, 59)
        result = should_i_deploy(before)
        assert result.startswith("✅")

    # --- Randomness: multiple calls may differ ---

    def test_blessed_pool_has_variety(self):
        results = {should_i_deploy(TUESDAY_MORNING) for _ in range(30)}
        assert len(results) > 1

    def test_cursed_pool_has_variety(self):
        results = {should_i_deploy(FRIDAY_LATE) for _ in range(30)}
        assert len(results) > 1


# ===========================================================================
# code_review_roulette
# ===========================================================================

class TestCodeReviewRoulette:

    # --- Return type ---

    def test_default_returns_string(self):
        result = code_review_roulette()
        assert isinstance(result, str)

    def test_default_non_empty(self):
        assert len(code_review_roulette().strip()) > 0

    def test_n1_returns_string(self):
        result = code_review_roulette(n=1)
        assert isinstance(result, str)

    def test_n_greater_than_1_returns_list(self):
        result = code_review_roulette(n=3)
        assert isinstance(result, list)

    def test_n_returns_correct_count(self):
        result = code_review_roulette(n=5)
        assert len(result) == 5

    def test_list_items_are_strings(self):
        result = code_review_roulette(n=3)
        assert all(isinstance(c, str) for c in result)

    def test_list_items_non_empty(self):
        result = code_review_roulette(n=3)
        assert all(len(c.strip()) > 0 for c in result)

    # --- Uniqueness ---

    def test_n_results_are_unique(self):
        result = code_review_roulette(n=5)
        assert len(result) == len(set(result))

    # --- Error handling ---

    def test_n_zero_raises(self):
        with pytest.raises(ValueError):
            code_review_roulette(n=0)

    def test_n_negative_raises(self):
        with pytest.raises(ValueError):
            code_review_roulette(n=-1)

    # --- Large n capped at pool size ---

    def test_n_larger_than_pool_capped(self):
        # Should not raise; just returns as many unique ones as possible
        result = code_review_roulette(n=9999)
        assert isinstance(result, list)
        assert len(result) > 0

    # --- Randomness ---

    def test_different_calls_differ(self):
        results = {code_review_roulette() for _ in range(20)}
        assert len(results) > 1

    def test_n2_list_varies_across_calls(self):
        pairs = [tuple(code_review_roulette(n=2)) for _ in range(20)]
        unique_pairs = set(pairs)
        assert len(unique_pairs) > 1

    # --- Content sanity ---

    def test_comment_contains_text(self):
        comment = code_review_roulette()
        # Should contain at least a few words
        assert len(comment.split()) >= 3
