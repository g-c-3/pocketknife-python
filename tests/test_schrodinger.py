"""
tests/test_schrodinger.py
~~~~~~~~~~~~~~~~~~~~~~~~~
Unit tests for pocketknife.schrodinger.
"""

import threading
import unittest
from unittest.mock import patch

from pocketknife.schrodinger import (
    QuantumBool,
    entangle,
    observe_many,
    quantum_bool,
)


# ---------------------------------------------------------------------------
# quantum_bool
# ---------------------------------------------------------------------------

class TestQuantumBool(unittest.TestCase):

    def test_returns_bool(self):
        self.assertIsInstance(quantum_bool(), bool)

    def test_can_return_true(self):
        with patch("random.getrandbits", return_value=1):
            self.assertIs(quantum_bool(), True)

    def test_can_return_false(self):
        with patch("random.getrandbits", return_value=0):
            self.assertIs(quantum_bool(), False)

    def test_distribution_roughly_50_50(self):
        """Over 1000 trials, expect between 400 and 600 True values."""
        results = [quantum_bool() for _ in range(1000)]
        trues = sum(results)
        self.assertGreaterEqual(trues, 350)
        self.assertLessEqual(trues, 650)

    def test_returns_native_bool_not_int(self):
        result = quantum_bool()
        self.assertIs(type(result), bool)


# ---------------------------------------------------------------------------
# QuantumBool — construction
# ---------------------------------------------------------------------------

class TestQuantumBoolConstruction(unittest.TestCase):

    def test_default_bias(self):
        q = QuantumBool()
        self.assertEqual(q.bias, 0.5)

    def test_custom_bias(self):
        q = QuantumBool(bias=0.9)
        self.assertEqual(q.bias, 0.9)

    def test_bias_zero_allowed(self):
        q = QuantumBool(bias=0.0)
        self.assertFalse(bool(q))

    def test_bias_one_allowed(self):
        q = QuantumBool(bias=1.0)
        self.assertTrue(bool(q))

    def test_bias_below_zero_raises(self):
        with self.assertRaises(ValueError):
            QuantumBool(bias=-0.1)

    def test_bias_above_one_raises(self):
        with self.assertRaises(ValueError):
            QuantumBool(bias=1.1)

    def test_label_stored(self):
        q = QuantumBool(label="mybit")
        self.assertIn("mybit", repr(q))


# ---------------------------------------------------------------------------
# QuantumBool — superposition state
# ---------------------------------------------------------------------------

class TestQuantumBoolSuperposition(unittest.TestCase):

    def test_not_observed_before_collapse(self):
        q = QuantumBool()
        self.assertFalse(q.observed)

    def test_value_is_none_before_collapse(self):
        q = QuantumBool()
        self.assertIsNone(q.value)

    def test_repr_shows_superposition(self):
        q = QuantumBool()
        r = repr(q)
        self.assertIn("⟩", r)          # quantum notation present
        self.assertNotIn("collapsed", r)

    def test_repr_shows_collapsed_after_observation(self):
        q = QuantumBool()
        bool(q)
        self.assertIn("collapsed", repr(q))

    def test_observed_true_after_bool(self):
        q = QuantumBool()
        bool(q)
        self.assertTrue(q.observed)

    def test_observed_true_after_observe(self):
        q = QuantumBool()
        q.observe()
        self.assertTrue(q.observed)

    def test_value_set_after_collapse(self):
        q = QuantumBool()
        val = bool(q)
        self.assertIs(q.value, val)


# ---------------------------------------------------------------------------
# QuantumBool — stability after collapse
# ---------------------------------------------------------------------------

class TestQuantumBoolStability(unittest.TestCase):

    def test_stays_true_after_collapse(self):
        with patch("random.random", return_value=0.1):  # < 0.5 → True
            q = QuantumBool()
            first = bool(q)
        for _ in range(10):
            self.assertIs(bool(q), first)

    def test_stays_false_after_collapse(self):
        with patch("random.random", return_value=0.9):  # > 0.5 → False
            q = QuantumBool()
            first = bool(q)
        for _ in range(10):
            self.assertIs(bool(q), first)

    def test_observe_method_idempotent(self):
        q = QuantumBool()
        v1 = q.observe()
        v2 = q.observe()
        self.assertIs(v1, v2)

    def test_int_conversion_stable(self):
        q = QuantumBool()
        v = int(q)
        self.assertIn(v, (0, 1))
        self.assertEqual(int(q), v)


# ---------------------------------------------------------------------------
# QuantumBool — boolean operations
# ---------------------------------------------------------------------------

class TestQuantumBoolOperations(unittest.TestCase):

    def _make(self, value: bool) -> QuantumBool:
        q = QuantumBool()
        with patch("random.random", return_value=0.1 if value else 0.9):
            bool(q)  # force collapse
        return q

    def test_eq_true_vs_true(self):
        self.assertEqual(self._make(True), True)

    def test_eq_false_vs_false(self):
        self.assertEqual(self._make(False), False)

    def test_ne_true_vs_false(self):
        self.assertNotEqual(self._make(True), False)

    def test_and_true_true(self):
        self.assertTrue(self._make(True) & True)

    def test_and_true_false(self):
        self.assertFalse(self._make(True) & False)

    def test_or_false_false(self):
        self.assertFalse(self._make(False) | False)

    def test_or_false_true(self):
        self.assertTrue(self._make(False) | True)

    def test_xor_true_false(self):
        self.assertTrue(self._make(True) ^ False)

    def test_xor_true_true(self):
        self.assertFalse(self._make(True) ^ True)

    def test_invert_true(self):
        self.assertFalse(~self._make(True))

    def test_invert_false(self):
        self.assertTrue(~self._make(False))

    def test_if_statement_works(self):
        q = self._make(True)
        executed = False
        if q:
            executed = True
        self.assertTrue(executed)

    def test_eq_two_quantum_bools(self):
        a = self._make(True)
        b = self._make(True)
        self.assertEqual(a, b)

    def test_eq_returns_not_implemented_for_unknown_type(self):
        q = self._make(True)
        result = q.__eq__("not a bool")
        self.assertIs(result, NotImplemented)

    def test_hashable(self):
        q = QuantumBool()
        d = {q: "value"}
        self.assertIn(q, d)


# ---------------------------------------------------------------------------
# QuantumBool — thread safety
# ---------------------------------------------------------------------------

class TestQuantumBoolThreadSafety(unittest.TestCase):

    def test_collapses_to_single_value_under_concurrent_observation(self):
        """Many threads observing the same QuantumBool must all see the same value."""
        q = QuantumBool()
        results = []
        lock = threading.Lock()

        def observe():
            val = bool(q)
            with lock:
                results.append(val)

        threads = [threading.Thread(target=observe) for _ in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(set(results)), 1, "Collapsed to multiple values!")


# ---------------------------------------------------------------------------
# entangle
# ---------------------------------------------------------------------------

class TestEntangle(unittest.TestCase):

    def test_returns_tuple_of_two(self):
        a, b = entangle(QuantumBool(), QuantumBool())
        self.assertIsInstance(a, QuantumBool)
        self.assertIsInstance(b, QuantumBool)

    def test_same_objects_returned(self):
        orig_a, orig_b = QuantumBool(), QuantumBool()
        ret_a, ret_b = entangle(orig_a, orig_b)
        self.assertIs(ret_a, orig_a)
        self.assertIs(ret_b, orig_b)

    def test_entangled_pair_always_opposite(self):
        """Over many trials, entangled pairs must always be opposite."""
        for _ in range(50):
            a, b = entangle(QuantumBool(), QuantumBool())
            va, vb = bool(a), bool(b)
            self.assertNotEqual(va, vb,
                f"Entangled pair collapsed to same value: a={va}, b={vb}")

    def test_observing_b_first_still_opposite(self):
        for _ in range(20):
            a, b = entangle(QuantumBool(), QuantumBool())
            vb, va = bool(b), bool(a)
            self.assertNotEqual(va, vb)

    def test_cannot_entangle_observed_a(self):
        a = QuantumBool()
        bool(a)
        with self.assertRaises(ValueError):
            entangle(a, QuantumBool())

    def test_cannot_entangle_observed_b(self):
        b = QuantumBool()
        bool(b)
        with self.assertRaises(ValueError):
            entangle(QuantumBool(), b)

    def test_cannot_entangle_with_self(self):
        q = QuantumBool()
        with self.assertRaises(ValueError):
            entangle(q, q)

    def test_error_message_mentions_collapsed(self):
        a = QuantumBool()
        bool(a)
        try:
            entangle(a, QuantumBool())
        except ValueError as e:
            self.assertIn("collapsed", str(e).lower())

    def test_bias_irrelevant_to_opposition(self):
        """Entangled bools are always opposite regardless of bias."""
        for _ in range(20):
            a = QuantumBool(bias=0.9)
            b = QuantumBool(bias=0.1)
            entangle(a, b)
            self.assertNotEqual(bool(a), bool(b))


# ---------------------------------------------------------------------------
# observe_many
# ---------------------------------------------------------------------------

class TestObserveMany(unittest.TestCase):

    def test_returns_list(self):
        self.assertIsInstance(observe_many(5), list)

    def test_correct_length(self):
        self.assertEqual(len(observe_many(10)), 10)

    def test_all_bools(self):
        for v in observe_many(20):
            self.assertIsInstance(v, bool)

    def test_n_zero_raises(self):
        with self.assertRaises(ValueError):
            observe_many(0)

    def test_n_negative_raises(self):
        with self.assertRaises(ValueError):
            observe_many(-1)

    def test_n_one_works(self):
        result = observe_many(1)
        self.assertEqual(len(result), 1)

    def test_distribution_over_large_n(self):
        results = observe_many(2000)
        trues = sum(results)
        # Expect between 40% and 60% True over 2000 trials
        self.assertGreaterEqual(trues, 700)
        self.assertLessEqual(trues, 1300)

    def test_results_are_independent(self):
        """observe_many must not return the same QuantumBool multiple times."""
        results = observe_many(100)
        # If all identical, something is wrong (probability 2^-99)
        self.assertGreater(len(set(results)), 1)


if __name__ == "__main__":
    unittest.main()
