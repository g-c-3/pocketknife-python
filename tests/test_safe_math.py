"""Unit tests for pocketknife.safe_math."""

import math
import unittest

from pocketknife.safe_math import clamp, divide, percent, safe_round


class TestDivide(unittest.TestCase):
    def test_normal_division(self):
        self.assertEqual(divide(10, 2), 5.0)

    def test_returns_float(self):
        self.assertIsInstance(divide(9, 3), float)

    def test_zero_denominator_returns_none_by_default(self):
        self.assertIsNone(divide(10, 0))

    def test_zero_denominator_returns_custom_default(self):
        self.assertEqual(divide(10, 0, default=-1), -1)

    def test_non_numeric_numerator_returns_default(self):
        self.assertIsNone(divide("x", 2))

    def test_non_numeric_denominator_returns_default(self):
        self.assertIsNone(divide(10, "y"))

    def test_none_input_returns_default(self):
        self.assertIsNone(divide(None, 5))

    def test_infinity_returns_default(self):
        self.assertIsNone(divide(float("inf"), 1))

    def test_nan_returns_default(self):
        self.assertIsNone(divide(float("nan"), 1))

    def test_fractional_result(self):
        result = divide(1, 3)
        self.assertAlmostEqual(result, 0.3333, places=4)

    def test_zero_numerator_is_valid(self):
        self.assertEqual(divide(0, 5), 0.0)


class TestPercent(unittest.TestCase):
    def test_basic_percent(self):
        self.assertEqual(percent(1, 4), 25.0)

    def test_zero_whole_returns_none(self):
        self.assertIsNone(percent(0, 0))

    def test_custom_default_on_error(self):
        self.assertEqual(percent(1, 0, default=0.0), 0.0)

    def test_ndigits_rounds_result(self):
        self.assertEqual(percent(1, 3, ndigits=2), 33.33)

    def test_100_percent(self):
        self.assertEqual(percent(5, 5), 100.0)

    def test_over_100_percent(self):
        self.assertEqual(percent(10, 5), 200.0)


class TestClamp(unittest.TestCase):
    def test_value_above_hi_returns_hi(self):
        self.assertEqual(clamp(150, lo=0, hi=100), 100)

    def test_value_below_lo_returns_lo(self):
        self.assertEqual(clamp(-5, lo=0, hi=100), 0)

    def test_value_in_range_unchanged(self):
        self.assertEqual(clamp(42, lo=0, hi=100), 42)

    def test_lo_only(self):
        self.assertEqual(clamp(-5, lo=0), 0)
        self.assertEqual(clamp(99, lo=0), 99)

    def test_hi_only(self):
        self.assertEqual(clamp(999, hi=100), 100)
        self.assertEqual(clamp(50, hi=100), 50)

    def test_no_bounds_returns_value_unchanged(self):
        self.assertEqual(clamp(42), 42)

    def test_value_equal_to_lo(self):
        self.assertEqual(clamp(0, lo=0, hi=10), 0)

    def test_value_equal_to_hi(self):
        self.assertEqual(clamp(10, lo=0, hi=10), 10)

    def test_invalid_bounds_raises(self):
        with self.assertRaises(ValueError):
            clamp(5, lo=10, hi=0)

    def test_float_bounds(self):
        self.assertAlmostEqual(clamp(1.5, lo=0.0, hi=1.0), 1.0)


class TestSafeRound(unittest.TestCase):
    def test_rounds_to_ndigits(self):
        self.assertEqual(safe_round(3.14159, 2), 3.14)

    def test_rounds_to_zero_digits(self):
        self.assertEqual(safe_round(3.7), 4.0)

    def test_none_returns_default(self):
        self.assertIsNone(safe_round(None))

    def test_non_numeric_returns_default(self):
        self.assertIsNone(safe_round("bad"))

    def test_custom_default_on_error(self):
        self.assertEqual(safe_round(None, default=0.0), 0.0)

    def test_returns_float(self):
        self.assertIsInstance(safe_round(3.14, 1), float)


if __name__ == "__main__":
    unittest.main()
