"""
Tests for pocketknife.fuzzy_time
"""

import sys
import os
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pocketknife.fuzzy_time import around_now, around_noon, relative_age

# ---------------------------------------------------------------------------
# Fixed reference point for all deterministic tests
# ---------------------------------------------------------------------------

NOW = datetime.datetime(2024, 6, 15, 12, 0, 0)

def past(seconds=0, minutes=0, hours=0, days=0, weeks=0):
    delta = datetime.timedelta(
        seconds=seconds, minutes=minutes, hours=hours, days=days, weeks=weeks
    )
    return NOW - delta

def future(seconds=0, minutes=0, hours=0, days=0, weeks=0):
    delta = datetime.timedelta(
        seconds=seconds, minutes=minutes, hours=hours, days=days, weeks=weeks
    )
    return NOW + delta


# ===========================================================================
# around_now — past
# ===========================================================================

class TestAroundNowPast:

    # --- just now (< 45 s) ---

    def test_0_seconds(self):
        assert around_now(NOW, NOW) == "just now"

    def test_10_seconds(self):
        assert around_now(past(seconds=10), NOW) == "just now"

    def test_44_seconds(self):
        assert around_now(past(seconds=44), NOW) == "just now"

    def test_45_seconds_is_a_minute(self):
        assert around_now(past(seconds=45), NOW) == "a minute ago"

    def test_89_seconds(self):
        assert around_now(past(seconds=89), NOW) == "a minute ago"

    # --- minutes ago (90 s – 45 min) ---

    def test_90_seconds(self):
        assert around_now(past(seconds=90), NOW) == "2 minutes ago"

    def test_5_minutes(self):
        assert around_now(past(minutes=5), NOW) == "5 minutes ago"

    def test_44_minutes(self):
        assert around_now(past(minutes=44), NOW) == "44 minutes ago"

    # --- about an hour ago (45–90 min) ---

    def test_45_minutes(self):
        assert around_now(past(minutes=45), NOW) == "about an hour ago"

    def test_90_minutes(self):
        # 90 min = 5400 s > 45-min threshold → falls into "about N hours ago"
        assert around_now(past(minutes=90), NOW) == "about 2 hours ago"

    # --- about N hours ago (90 min – 22 h) ---

    def test_2_hours(self):
        assert around_now(past(hours=2), NOW) == "about 2 hours ago"

    def test_3_hours_30_minutes(self):
        assert around_now(past(hours=3, minutes=30), NOW) == "about 4 hours ago"

    def test_21_hours(self):
        assert around_now(past(hours=21), NOW) == "about 21 hours ago"

    # --- a day ago (22–36 h) ---

    def test_22_hours(self):
        assert around_now(past(hours=22), NOW) == "a day ago"

    def test_35_hours(self):
        assert around_now(past(hours=35), NOW) == "a day ago"

    # --- N days ago (36 h – 6 days) ---

    def test_2_days(self):
        assert around_now(past(days=2), NOW) == "2 days ago"

    def test_5_days(self):
        assert around_now(past(days=5), NOW) == "5 days ago"

    # --- about a week ago (6–11 days) ---

    def test_7_days(self):
        assert around_now(past(days=7), NOW) == "about a week ago"

    def test_10_days(self):
        assert around_now(past(days=10), NOW) == "about a week ago"

    # --- N weeks ago (11 days – 3 weeks) ---

    def test_2_weeks(self):
        assert around_now(past(weeks=2), NOW) == "2 weeks ago"

    def test_3_weeks(self):
        # 3 weeks = exactly the 3*WEEK boundary (not <), falls into "about a month ago"
        assert around_now(past(weeks=3), NOW) == "about a month ago"

    def test_20_days(self):
        # 20 days is safely inside the "N weeks ago" band
        assert around_now(past(days=20), NOW) == "3 weeks ago"

    # --- about a month ago (3–45 days roughly) ---

    def test_31_days(self):
        assert around_now(past(days=31), NOW) == "about a month ago"

    def test_44_days(self):
        assert around_now(past(days=44), NOW) == "about a month ago"

    # --- N months ago (45 days – 8 months) ---

    def test_2_months(self):
        assert around_now(past(days=60), NOW) == "2 months ago"

    def test_5_months(self):
        assert around_now(past(days=150), NOW) == "5 months ago"

    # --- about a year ago (8–11 months) ---

    def test_9_months(self):
        assert around_now(past(days=270), NOW) == "about a year ago"

    # --- a year ago (11–18 months) ---

    def test_13_months(self):
        assert around_now(past(days=395), NOW) == "a year ago"

    # --- about N years ago (> 18 months) ---

    def test_2_years(self):
        assert around_now(past(days=730), NOW) == "about 2 years ago"

    def test_5_years(self):
        assert around_now(past(days=1825), NOW) == "about 5 years ago"


# ===========================================================================
# around_now — future
# ===========================================================================

class TestAroundNowFuture:

    def test_future_just_now(self):
        assert around_now(future(seconds=10), NOW) == "just now"

    def test_future_a_minute(self):
        assert around_now(future(seconds=60), NOW) == "in a minute"

    def test_future_minutes(self):
        assert around_now(future(minutes=10), NOW) == "in 10 minutes"

    def test_future_about_an_hour(self):
        assert around_now(future(minutes=60), NOW) == "in about an hour"

    def test_future_hours(self):
        assert around_now(future(hours=5), NOW) == "in about 5 hours"

    def test_future_a_day(self):
        assert around_now(future(hours=24), NOW) == "in a day"

    def test_future_days(self):
        assert around_now(future(days=3), NOW) == "in 3 days"

    def test_future_months(self):
        assert around_now(future(days=180), NOW) == "in 6 months"

    def test_future_years(self):
        assert around_now(future(days=800), NOW) == "in about 2 years"

    def test_future_no_ago_in_result(self):
        result = around_now(future(days=5), NOW)
        assert "ago" not in result

    def test_past_no_in_in_result(self):
        result = around_now(past(days=5), NOW)
        assert not result.startswith("in ")


# ===========================================================================
# around_now — general contract
# ===========================================================================

class TestAroundNowContract:

    def test_returns_string(self):
        assert isinstance(around_now(past(hours=1), NOW), str)

    def test_non_empty(self):
        assert len(around_now(past(hours=1), NOW).strip()) > 0

    def test_default_now_does_not_raise(self):
        result = around_now(datetime.datetime.now() - datetime.timedelta(seconds=5))
        assert isinstance(result, str)

    def test_timezone_aware(self):
        tz = datetime.timezone.utc
        now_aware = datetime.datetime(2024, 6, 15, 12, 0, 0, tzinfo=tz)
        dt_aware = now_aware - datetime.timedelta(hours=1)
        result = around_now(dt_aware, now_aware)
        assert "hour" in result

    def test_around_noon_alias(self):
        # around_noon should be identical to around_now
        dt = past(hours=2)
        assert around_noon(dt, NOW) == around_now(dt, NOW)


# ===========================================================================
# relative_age
# ===========================================================================

class TestRelativeAge:

    def test_a_few_seconds(self):
        assert relative_age(past(seconds=5), NOW) == "a few seconds"

    def test_a_minute(self):
        assert relative_age(past(seconds=60), NOW) == "a minute"

    def test_minutes(self):
        # 47 min > 45-min threshold → "about an hour"
        assert relative_age(past(minutes=47), NOW) == "about an hour"

    def test_minutes_under_threshold(self):
        # 30 min is safely within the "N minutes" band
        assert relative_age(past(minutes=30), NOW) == "30 minutes"

    def test_about_an_hour(self):
        assert relative_age(past(minutes=75), NOW) == "about an hour"

    def test_about_hours(self):
        assert relative_age(past(hours=6), NOW) == "about 6 hours"

    def test_a_day(self):
        assert relative_age(past(hours=24), NOW) == "a day"

    def test_days(self):
        assert relative_age(past(days=4), NOW) == "4 days"

    def test_about_a_week(self):
        assert relative_age(past(days=8), NOW) == "about a week"

    def test_weeks(self):
        assert relative_age(past(weeks=2), NOW) == "2 weeks"

    def test_about_a_month(self):
        assert relative_age(past(days=35), NOW) == "about a month"

    def test_months(self):
        assert relative_age(past(days=120), NOW) == "4 months"

    def test_about_a_year(self):
        assert relative_age(past(days=300), NOW) == "about a year"

    def test_a_year(self):
        assert relative_age(past(days=400), NOW) == "a year"

    def test_about_years(self):
        assert relative_age(past(days=800), NOW) == "about 2 years"

    def test_no_ago_in_result(self):
        assert "ago" not in relative_age(past(hours=5), NOW)

    def test_no_in_prefix(self):
        assert not relative_age(past(hours=5), NOW).startswith("in ")

    def test_future_still_works(self):
        # relative_age is unsigned — future datetimes get the same label
        result_past   = relative_age(past(days=3),   NOW)
        result_future = relative_age(future(days=3), NOW)
        assert result_past == result_future

    def test_returns_string(self):
        assert isinstance(relative_age(past(minutes=10), NOW), str)

    def test_default_now_does_not_raise(self):
        result = relative_age(datetime.datetime.now() - datetime.timedelta(minutes=5))
        assert isinstance(result, str)

    def test_timezone_aware(self):
        tz = datetime.timezone.utc
        now_aware = datetime.datetime(2024, 6, 15, 12, 0, 0, tzinfo=tz)
        dt_aware = now_aware - datetime.timedelta(days=5)
        result = relative_age(dt_aware, now_aware)
        assert "day" in result
