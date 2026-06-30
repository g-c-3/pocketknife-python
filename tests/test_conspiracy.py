"""
tests/test_conspiracy.py
~~~~~~~~~~~~~~~~~~~~~~~~
Unit tests for pocketknife.conspiracy.
"""

import unittest

from pocketknife.conspiracy import (
    _pick_two_distinct,
    generate_theories,
    generate_theory,
)


# ---------------------------------------------------------------------------
# _pick_two_distinct
# ---------------------------------------------------------------------------

class TestPickTwoDistinct(unittest.TestCase):

    def test_returns_tuple_of_two(self):
        result = _pick_two_distinct(["a", "b", "c"])
        self.assertEqual(len(result), 2)

    def test_both_from_input_list(self):
        vars_list = ["a", "b", "c"]
        a, b = _pick_two_distinct(vars_list)
        self.assertIn(a, vars_list)
        self.assertIn(b, vars_list)

    def test_distinct_when_more_than_one_element(self):
        # Run several times to reduce flakiness from randomness
        for _ in range(20):
            a, b = _pick_two_distinct(["x", "y"])
            self.assertNotEqual(a, b)

    def test_single_element_returns_same_value_twice(self):
        a, b = _pick_two_distinct(["only_one"])
        self.assertEqual(a, "only_one")
        self.assertEqual(b, "only_one")


# ---------------------------------------------------------------------------
# generate_theory
# ---------------------------------------------------------------------------

class TestGenerateTheory(unittest.TestCase):

    def test_returns_string(self):
        result = generate_theory(["foo", "bar"])
        self.assertIsInstance(result, str)

    def test_non_empty_string(self):
        result = generate_theory(["foo", "bar"])
        self.assertTrue(len(result) > 0)

    def test_empty_list_raises_value_error(self):
        with self.assertRaises(ValueError):
            generate_theory([])

    def test_single_variable_works(self):
        result = generate_theory(["lonely_var"])
        self.assertIn("lonely_var", result)

    def test_at_least_one_variable_name_appears(self):
        vars_list = ["alpha", "beta", "gamma"]
        result = generate_theory(vars_list)
        self.assertTrue(any(v in result for v in vars_list))

    def test_two_variables_both_likely_to_appear(self):
        """With exactly two vars, both should appear since a and b are forced distinct."""
        vars_list = ["alpha", "beta"]
        result = generate_theory(vars_list)
        self.assertIn("alpha", result)
        self.assertIn("beta", result)

    def test_accepts_non_string_elements_via_str_conversion(self):
        """Should coerce non-string elements (like ints) to strings without error."""
        result = generate_theory([123, 456])
        self.assertIsInstance(result, str)
        self.assertTrue("123" in result or "456" in result)

    def test_varies_across_calls(self):
        """Across many calls, output should not always be identical."""
        results = {generate_theory(["a", "b", "c", "d", "e"]) for _ in range(30)}
        self.assertGreater(len(results), 1)

    def test_ends_with_a_period_or_punctuation(self):
        result = generate_theory(["x", "y"])
        self.assertTrue(result.strip()[-1] in ".!?")

    def test_third_variable_sometimes_included(self):
        """With 3+ vars, the third-variable line should appear in at least
        some of many generated theories (since remaining is non-empty)."""
        vars_list = ["one", "two", "three", "four"]
        found_extra_mention = False
        for _ in range(30):
            theory = generate_theory(vars_list)
            # Count how many distinct vars appear; with 3+ present it means
            # the third-var line fired at least once across the run.
            mentioned = sum(1 for v in vars_list if v in theory)
            if mentioned >= 3:
                found_extra_mention = True
                break
        self.assertTrue(found_extra_mention)


# ---------------------------------------------------------------------------
# generate_theories
# ---------------------------------------------------------------------------

class TestGenerateTheories(unittest.TestCase):

    def test_returns_list(self):
        result = generate_theories(["a", "b"], n=3)
        self.assertIsInstance(result, list)

    def test_correct_length(self):
        result = generate_theories(["a", "b"], n=5)
        self.assertEqual(len(result), 5)

    def test_all_elements_are_strings(self):
        result = generate_theories(["a", "b", "c"], n=4)
        self.assertTrue(all(isinstance(t, str) for t in result))

    def test_default_n_is_three(self):
        result = generate_theories(["a", "b"])
        self.assertEqual(len(result), 3)

    def test_zero_n_raises_value_error(self):
        with self.assertRaises(ValueError):
            generate_theories(["a", "b"], n=0)

    def test_negative_n_raises_value_error(self):
        with self.assertRaises(ValueError):
            generate_theories(["a", "b"], n=-2)

    def test_non_int_n_raises_value_error(self):
        with self.assertRaises(ValueError):
            generate_theories(["a", "b"], n=2.5)

    def test_empty_vars_raises_value_error(self):
        with self.assertRaises(ValueError):
            generate_theories([], n=2)

    def test_theories_can_vary(self):
        results = generate_theories(["a", "b", "c", "d", "e"], n=20)
        unique = set(results)
        self.assertGreater(len(unique), 1)


if __name__ == "__main__":
    unittest.main()
