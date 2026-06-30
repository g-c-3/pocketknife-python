"""Unit tests for pocketknife.diet_pandas."""

import unittest

from pocketknife.diet_pandas import groupby_key


class TestGroupbyKey(unittest.TestCase):
    def test_groups_by_string_key(self):
        records = [
            {"team": "red", "score": 10},
            {"team": "blue", "score": 7},
            {"team": "red", "score": 3},
        ]
        result = groupby_key(records, "team")
        self.assertEqual(
            result,
            {
                "red": [
                    {"team": "red", "score": 10},
                    {"team": "red", "score": 3},
                ],
                "blue": [{"team": "blue", "score": 7}],
            },
        )

    def test_preserves_group_order_and_record_order(self):
        records = [
            {"k": "b", "n": 1},
            {"k": "a", "n": 2},
            {"k": "b", "n": 3},
            {"k": "a", "n": 4},
        ]
        result = groupby_key(records, "k")
        self.assertEqual(list(result.keys()), ["b", "a"])
        self.assertEqual([r["n"] for r in result["b"]], [1, 3])
        self.assertEqual([r["n"] for r in result["a"]], [2, 4])

    def test_groups_by_callable_key(self):
        records = [{"n": 1}, {"n": 2}, {"n": 3}, {"n": 4}]
        result = groupby_key(records, lambda r: r["n"] % 2)
        self.assertEqual(result, {1: [{"n": 1}, {"n": 3}], 0: [{"n": 2}, {"n": 4}]})

    def test_missing_field_uses_default_none(self):
        records = [{"a": 1}, {"b": 2}]
        result = groupby_key(records, "a")
        self.assertEqual(result, {1: [{"a": 1}], None: [{"b": 2}]})

    def test_missing_field_uses_custom_default(self):
        records = [{"a": 1}, {"b": 2}]
        result = groupby_key(records, "a", default="N/A")
        self.assertEqual(result, {1: [{"a": 1}], "N/A": [{"b": 2}]})

    def test_strict_raises_keyerror_on_missing_field(self):
        records = [{"a": 1}, {"b": 2}]
        with self.assertRaises(KeyError):
            groupby_key(records, "a", strict=True)

    def test_strict_does_not_raise_when_field_present(self):
        records = [{"a": 1}, {"a": 2}]
        result = groupby_key(records, "a", strict=True)
        self.assertEqual(result, {1: [{"a": 1}], 2: [{"a": 2}]})

    def test_strict_has_no_effect_with_callable_key(self):
        records = [{"a": 1}, {"b": 2}]
        # callable never looks at missing fields directly, so strict
        # should not interfere.
        result = groupby_key(records, lambda r: r.get("a", "none"), strict=True)
        self.assertEqual(result, {1: [{"a": 1}], "none": [{"b": 2}]})

    def test_empty_records_returns_empty_dict(self):
        self.assertEqual(groupby_key([], "anything"), {})

    def test_accepts_generic_iterable_not_just_list(self):
        def gen():
            yield {"x": "a"}
            yield {"x": "b"}
            yield {"x": "a"}

        result = groupby_key(gen(), "x")
        self.assertEqual(result, {"a": [{"x": "a"}, {"x": "a"}], "b": [{"x": "b"}]})


if __name__ == "__main__":
    unittest.main()
