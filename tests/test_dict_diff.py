"""Unit tests for pocketknife.dict_diff."""

import unittest

from pocketknife.dict_diff import compare


class TestCompare(unittest.TestCase):
    def test_identical_dicts_return_empty(self):
        self.assertEqual(compare({"a": 1, "b": 2}, {"a": 1, "b": 2}), {})

    def test_both_empty_return_empty(self):
        self.assertEqual(compare({}, {}), {})

    def test_detects_added_keys(self):
        result = compare({}, {"a": 1})
        self.assertEqual(result, {"added": {"a": 1}})

    def test_detects_removed_keys(self):
        result = compare({"a": 1}, {})
        self.assertEqual(result, {"removed": {"a": 1}})

    def test_detects_modified_keys(self):
        result = compare({"a": 1}, {"a": 2})
        self.assertEqual(result, {"modified": {"a": {"before": 1, "after": 2}}})

    def test_all_three_buckets_at_once(self):
        a = {"x": 1, "y": 2, "z": 3}
        b = {"x": 99, "y": 2, "w": 4}
        result = compare(a, b)
        self.assertEqual(result["added"], {"w": 4})
        self.assertEqual(result["removed"], {"z": 3})
        self.assertEqual(result["modified"], {"x": {"before": 1, "after": 99}})

    def test_only_non_empty_buckets_included(self):
        result = compare({"a": 1}, {"a": 2})
        self.assertNotIn("added", result)
        self.assertNotIn("removed", result)
        self.assertIn("modified", result)

    def test_value_type_change_is_modification(self):
        result = compare({"a": 1}, {"a": "one"})
        self.assertEqual(result["modified"]["a"], {"before": 1, "after": "one"})

    def test_none_values_handled(self):
        result = compare({"a": None}, {"a": 0})
        self.assertEqual(result["modified"]["a"]["before"], None)
        self.assertEqual(result["modified"]["a"]["after"], 0)

    def test_recursive_diffs_nested_dicts(self):
        a = {"db": {"host": "localhost", "port": 5432}}
        b = {"db": {"host": "prod.example.com", "port": 5432}}
        result = compare(a, b, recursive=True)
        self.assertIn("db", result["modified"])
        nested = result["modified"]["db"]
        self.assertEqual(
            nested["modified"]["host"],
            {"before": "localhost", "after": "prod.example.com"},
        )

    def test_recursive_unchanged_nested_not_included(self):
        a = {"db": {"host": "localhost", "port": 5432}}
        b = {"db": {"host": "localhost", "port": 5432}}
        result = compare(a, b, recursive=True)
        self.assertEqual(result, {})

    def test_recursive_false_treats_dicts_as_opaque(self):
        a = {"db": {"host": "localhost"}}
        b = {"db": {"host": "prod"}}
        result = compare(a, b, recursive=False)
        # Should report modified with raw before/after, not a nested diff
        self.assertIn("before", result["modified"]["db"])
        self.assertIn("after", result["modified"]["db"])

    def test_type_change_dict_to_scalar_not_recursed(self):
        a = {"cfg": {"key": "val"}}
        b = {"cfg": "flat_string"}
        result = compare(a, b, recursive=True)
        # Different types, so should be a plain modification
        self.assertEqual(result["modified"]["cfg"]["before"], {"key": "val"})
        self.assertEqual(result["modified"]["cfg"]["after"], "flat_string")

    def test_non_string_keys(self):
        result = compare({1: "a", 2: "b"}, {1: "a", 3: "c"})
        self.assertEqual(result["added"], {3: "c"})
        self.assertEqual(result["removed"], {2: "b"})


if __name__ == "__main__":
    unittest.main()
