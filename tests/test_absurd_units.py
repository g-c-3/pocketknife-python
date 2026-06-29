"""
Tests for pocketknife.absurd_units
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pocketknife.absurd_units import (
    to_bananas,
    to_coffees,
    to_jiffies,
    to_double_deckers,
    to_football_fields,
    to_olympic_pools,
    to_library_of_congress,
    _BANANA_LENGTH_M,
    _COFFEE_JOULES,
    _JIFFY_SECONDS,
    _DOUBLE_DECKER_M,
    _FOOTBALL_FIELD_M,
    _OLYMPIC_POOL_L,
    _LOC_BYTES,
)


# ===========================================================================
# to_bananas
# ===========================================================================

class TestToBananas:

    def test_one_banana_length(self):
        assert math.isclose(to_bananas(_BANANA_LENGTH_M), 1.0, rel_tol=1e-9)

    def test_zero_meters(self):
        assert to_bananas(0) == 0.0

    def test_one_meter(self):
        result = to_bananas(1)
        assert math.isclose(result, 1 / _BANANA_LENGTH_M, rel_tol=1e-9)

    def test_known_value(self):
        # 0.1778 m * 2 = 2 bananas
        assert math.isclose(to_bananas(_BANANA_LENGTH_M * 2), 2.0, rel_tol=1e-9)

    def test_negative_meters(self):
        assert to_bananas(-1) < 0

    def test_large_value(self):
        # Mount Everest: 8849 m → lots of bananas
        result = to_bananas(8849)
        assert result > 40_000

    def test_returns_float_by_default(self):
        assert isinstance(to_bananas(1), float)

    def test_pretty_returns_string(self):
        result = to_bananas(1, pretty=True)
        assert isinstance(result, str)

    def test_pretty_contains_unit(self):
        result = to_bananas(1, pretty=True)
        assert "bananas" in result

    def test_pretty_contains_number(self):
        result = to_bananas(1, pretty=True)
        # Should contain a digit
        assert any(c.isdigit() for c in result)

    def test_pretty_and_raw_consistent(self):
        raw = to_bananas(5)
        pretty = to_bananas(5, pretty=True)
        # The pretty string should contain the rounded raw value
        assert str(round(raw, 4)).rstrip("0").rstrip(".").replace(",", "") in pretty.replace(",", "")


# ===========================================================================
# to_coffees
# ===========================================================================

class TestToCoffees:

    def test_one_coffee_worth_of_joules(self):
        assert math.isclose(to_coffees(_COFFEE_JOULES), 1.0, rel_tol=1e-9)

    def test_zero_joules(self):
        assert to_coffees(0) == 0.0

    def test_two_coffees(self):
        assert math.isclose(to_coffees(_COFFEE_JOULES * 2), 2.0, rel_tol=1e-9)

    def test_returns_float_by_default(self):
        assert isinstance(to_coffees(1000), float)

    def test_pretty_returns_string(self):
        result = to_coffees(1_000_000, pretty=True)
        assert isinstance(result, str)

    def test_pretty_contains_unit(self):
        result = to_coffees(1_000_000, pretty=True)
        assert "cups of coffee" in result

    def test_large_energy(self):
        # 1 megajoule should be more than 1 coffee
        assert to_coffees(1_000_000) > 1

    def test_negative_joules(self):
        assert to_coffees(-_COFFEE_JOULES) < 0

    def test_fractional_result(self):
        # Half a coffee's worth
        result = to_coffees(_COFFEE_JOULES / 2)
        assert math.isclose(result, 0.5, rel_tol=1e-9)


# ===========================================================================
# to_jiffies
# ===========================================================================

class TestToJiffies:

    def test_one_second(self):
        assert math.isclose(to_jiffies(1), 100.0, rel_tol=1e-9)

    def test_one_jiffy(self):
        assert math.isclose(to_jiffies(_JIFFY_SECONDS), 1.0, rel_tol=1e-9)

    def test_zero_seconds(self):
        assert to_jiffies(0) == 0.0

    def test_one_minute(self):
        assert math.isclose(to_jiffies(60), 6_000.0, rel_tol=1e-9)

    def test_one_hour(self):
        assert math.isclose(to_jiffies(3600), 360_000.0, rel_tol=1e-9)

    def test_returns_float_by_default(self):
        assert isinstance(to_jiffies(1), float)

    def test_pretty_returns_string(self):
        result = to_jiffies(1, pretty=True)
        assert isinstance(result, str)

    def test_pretty_contains_unit(self):
        result = to_jiffies(1, pretty=True)
        assert "jiffies" in result

    def test_sub_second(self):
        # 10 ms = 1 jiffy
        assert math.isclose(to_jiffies(0.01), 1.0, rel_tol=1e-9)

    def test_negative_seconds(self):
        assert to_jiffies(-1) < 0


# ===========================================================================
# to_double_deckers
# ===========================================================================

class TestToDoubleDeckers:

    def test_one_bus_length(self):
        assert math.isclose(to_double_deckers(_DOUBLE_DECKER_M), 1.0, rel_tol=1e-9)

    def test_zero(self):
        assert to_double_deckers(0) == 0.0

    def test_returns_float(self):
        assert isinstance(to_double_deckers(100), float)

    def test_pretty_contains_unit(self):
        assert "double-decker buses" in to_double_deckers(100, pretty=True)

    def test_scaling(self):
        assert math.isclose(
            to_double_deckers(_DOUBLE_DECKER_M * 10), 10.0, rel_tol=1e-9
        )


# ===========================================================================
# to_football_fields
# ===========================================================================

class TestToFootballFields:

    def test_one_field_length(self):
        assert math.isclose(to_football_fields(_FOOTBALL_FIELD_M), 1.0, rel_tol=1e-9)

    def test_zero(self):
        assert to_football_fields(0) == 0.0

    def test_returns_float(self):
        assert isinstance(to_football_fields(100), float)

    def test_pretty_contains_unit(self):
        assert "football fields" in to_football_fields(1000, pretty=True)

    def test_one_km(self):
        result = to_football_fields(1000)
        assert math.isclose(result, 1000 / _FOOTBALL_FIELD_M, rel_tol=1e-9)


# ===========================================================================
# to_olympic_pools
# ===========================================================================

class TestToOlympicPools:

    def test_one_pool(self):
        assert math.isclose(to_olympic_pools(_OLYMPIC_POOL_L), 1.0, rel_tol=1e-9)

    def test_zero(self):
        assert to_olympic_pools(0) == 0.0

    def test_returns_float(self):
        assert isinstance(to_olympic_pools(1_000_000), float)

    def test_pretty_contains_unit(self):
        assert "Olympic swimming pools" in to_olympic_pools(5_000_000, pretty=True)

    def test_half_pool(self):
        assert math.isclose(to_olympic_pools(_OLYMPIC_POOL_L / 2), 0.5, rel_tol=1e-9)


# ===========================================================================
# to_library_of_congress
# ===========================================================================

class TestToLibraryOfCongress:

    def test_one_loc(self):
        assert math.isclose(to_library_of_congress(_LOC_BYTES), 1.0, rel_tol=1e-9)

    def test_zero(self):
        assert to_library_of_congress(0) == 0.0

    def test_returns_float(self):
        assert isinstance(to_library_of_congress(1024 ** 4), float)

    def test_pretty_contains_unit(self):
        assert "Libraries of Congress" in to_library_of_congress(_LOC_BYTES, pretty=True)

    def test_ten_loc(self):
        assert math.isclose(
            to_library_of_congress(_LOC_BYTES * 10), 10.0, rel_tol=1e-9
        )


# ===========================================================================
# pretty formatting shared behaviour
# ===========================================================================

class TestPrettyFormatting:

    def test_no_trailing_zeros(self):
        # 1 jiffy should render as "1" not "1.0000"
        result = to_jiffies(_JIFFY_SECONDS, pretty=True)
        assert "1.0000" not in result
        assert result.startswith("1 ")

    def test_large_numbers_have_commas(self):
        # 1 hour = 360,000 jiffies — should be comma-formatted
        result = to_jiffies(3600, pretty=True)
        assert "," in result

    def test_pretty_false_is_default(self):
        # Calling without pretty= should return a numeric type
        assert isinstance(to_bananas(1), (int, float))
        assert isinstance(to_coffees(1), (int, float))
        assert isinstance(to_jiffies(1), (int, float))
