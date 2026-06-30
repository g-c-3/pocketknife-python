"""
tests/test_snark.py
~~~~~~~~~~~~~~~~~~~
Unit tests for pocketknife.snark.
"""

import unittest

from pocketknife.snark import judge_type


class TestJudgeTypeBasics(unittest.TestCase):

    def test_returns_string(self):
        self.assertIsInstance(judge_type(5), str)

    def test_includes_type_name(self):
        self.assertTrue(judge_type(5).startswith("int."))

    def test_includes_commentary(self):
        result = judge_type(5)
        # Should have more than just "int." — actual commentary follows
        self.assertGreater(len(result), len("int."))


class TestJudgeTypeNone(unittest.TestCase):

    def test_none_type_name(self):
        self.assertTrue(judge_type(None).startswith("NoneType."))

    def test_none_has_commentary(self):
        result = judge_type(None)
        self.assertIn("absence", result.lower())


class TestJudgeTypeBool(unittest.TestCase):

    def test_true_type_name_is_bool(self):
        self.assertTrue(judge_type(True).startswith("bool."))

    def test_false_type_name_is_bool(self):
        self.assertTrue(judge_type(False).startswith("bool."))

    def test_true_and_false_have_different_commentary(self):
        self.assertNotEqual(judge_type(True), judge_type(False))

    def test_bool_not_misidentified_as_int(self):
        """Critical: bool is an int subclass, but should be judged as bool."""
        result = judge_type(True)
        self.assertTrue(result.startswith("bool."))
        self.assertFalse(result.startswith("int."))


class TestJudgeTypeInt(unittest.TestCase):

    def test_zero_commentary(self):
        result = judge_type(0)
        self.assertIn("Zero", result)

    def test_negative_commentary(self):
        result = judge_type(-10)
        self.assertIn("egative", result)  # "Negative"/"negative"

    def test_large_number_commentary(self):
        result = judge_type(5_000_000)
        self.assertIn("big", result.lower())

    def test_ordinary_positive_int(self):
        result = judge_type(42)
        self.assertTrue(result.startswith("int."))
        self.assertNotIn("Zero", result)


class TestJudgeTypeFloat(unittest.TestCase):

    def test_float_type_name(self):
        self.assertTrue(judge_type(3.14).startswith("float."))

    def test_nan_commentary(self):
        result = judge_type(float("nan"))
        self.assertIn("NaN", result)

    def test_zero_float_commentary(self):
        result = judge_type(0.0)
        self.assertIn("Zero", result)

    def test_zero_float_not_confused_with_zero_int(self):
        self.assertTrue(judge_type(0.0).startswith("float."))
        self.assertTrue(judge_type(0).startswith("int."))


class TestJudgeTypeString(unittest.TestCase):

    def test_empty_string_commentary(self):
        result = judge_type("")
        self.assertIn("empty", result.lower())

    def test_all_caps_commentary(self):
        result = judge_type("HELLO")
        self.assertIn("CAPS", result)

    def test_whitespace_padded_commentary(self):
        result = judge_type("  padded  ")
        self.assertIn("whitespace", result.lower())

    def test_normal_string_commentary(self):
        result = judge_type("just a normal sentence")
        self.assertTrue(result.startswith("str."))

    def test_single_char_not_treated_as_all_caps_shouting(self):
        """A single uppercase letter like 'A' shouldn't trigger the ALL CAPS line."""
        result = judge_type("A")
        self.assertNotIn("CAPS", result)


class TestJudgeTypeList(unittest.TestCase):

    def test_empty_list_commentary(self):
        result = judge_type([])
        self.assertIn("empty", result.lower())

    def test_large_list_commentary(self):
        result = judge_type(list(range(2000)))
        self.assertIn("2000", result)

    def test_nested_list_commentary(self):
        result = judge_type([[1, 2], [3, 4]])
        self.assertIn("list of lists", result.lower())

    def test_normal_list_commentary(self):
        result = judge_type([1, 2, 3])
        self.assertTrue(result.startswith("list."))


class TestJudgeTypeDict(unittest.TestCase):

    def test_empty_dict_commentary(self):
        result = judge_type({})
        self.assertIn("empty", result.lower())

    def test_nonempty_dict_commentary(self):
        result = judge_type({"a": 1})
        self.assertTrue(result.startswith("dict."))


class TestJudgeTypeTuple(unittest.TestCase):

    def test_empty_tuple_commentary(self):
        result = judge_type(())
        self.assertIn("empty", result.lower())

    def test_nonempty_tuple_commentary(self):
        result = judge_type((1, 2))
        self.assertTrue(result.startswith("tuple."))


class TestJudgeTypeSet(unittest.TestCase):

    def test_empty_set_commentary(self):
        result = judge_type(set())
        self.assertIn("empty", result.lower())

    def test_nonempty_set_commentary(self):
        result = judge_type({1, 2, 3})
        self.assertTrue(result.startswith("set."))


class TestJudgeTypeCallable(unittest.TestCase):

    def test_function_commentary(self):
        def my_func():
            pass
        result = judge_type(my_func)
        self.assertIn("callable", result.lower())

    def test_builtin_function_commentary(self):
        result = judge_type(print)
        self.assertIn("callable", result.lower())

    def test_lambda_commentary(self):
        result = judge_type(lambda: None)
        self.assertIn("callable", result.lower())


class TestJudgeTypeFallback(unittest.TestCase):

    def test_custom_object_does_not_raise(self):
        class Thing:
            pass
        result = judge_type(Thing())
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("Thing."))

    def test_custom_object_gets_fallback_commentary(self):
        class Mystery:
            pass
        result = judge_type(Mystery())
        self.assertGreater(len(result), len("Mystery."))


class TestJudgeTypeNeverRaises(unittest.TestCase):
    """Sanity sweep: judge_type should never raise for any of these inputs."""

    def test_does_not_raise_for_assorted_inputs(self):
        samples = [
            None, True, False, 0, -1, 1, 10**10,
            0.0, -0.0, float("inf"), float("-inf"), float("nan"), 3.14,
            "", "x", "X", "ALLCAPS", "  spaced  ",
            [], [1], [[1]], list(range(1500)),
            {}, {"k": "v"},
            (), (1,),
            set(), {1, 2},
            print, lambda: None,
            object(),
        ]
        for sample in samples:
            try:
                result = judge_type(sample)
            except Exception as exc:
                self.fail(f"judge_type raised {exc!r} for input {sample!r}")
            self.assertIsInstance(result, str)


if __name__ == "__main__":
    unittest.main()
