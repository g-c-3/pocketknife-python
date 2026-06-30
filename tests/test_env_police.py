"""Unit tests for pocketknife.env_police."""

import unittest

from pocketknife.env_police import MissingEnvError, require_env


class TestRequireEnv(unittest.TestCase):
    def test_returns_values_when_all_present(self):
        env = {"FOO": "bar", "BAZ": "qux"}
        result = require_env("FOO", "BAZ", env=env)
        self.assertEqual(result, {"FOO": "bar", "BAZ": "qux"})

    def test_raises_when_key_absent(self):
        env = {"FOO": "bar"}
        with self.assertRaises(MissingEnvError) as ctx:
            require_env("FOO", "MISSING", env=env)
        self.assertEqual(ctx.exception.missing, ["MISSING"])

    def test_raises_with_all_missing_keys_listed(self):
        env = {}
        with self.assertRaises(MissingEnvError) as ctx:
            require_env("A", "B", "C", env=env)
        self.assertEqual(ctx.exception.missing, ["A", "B", "C"])

    def test_error_message_contains_missing_keys(self):
        env = {}
        with self.assertRaises(MissingEnvError) as ctx:
            require_env("A", "B", env=env)
        message = str(ctx.exception)
        self.assertIn("A", message)
        self.assertIn("B", message)

    def test_empty_string_treated_as_missing_by_default(self):
        env = {"FOO": ""}
        with self.assertRaises(MissingEnvError) as ctx:
            require_env("FOO", env=env)
        self.assertEqual(ctx.exception.missing, ["FOO"])

    def test_empty_string_allowed_when_flag_set(self):
        env = {"FOO": ""}
        result = require_env("FOO", env=env, allow_empty=True)
        self.assertEqual(result, {"FOO": ""})

    def test_no_keys_raises_value_error(self):
        with self.assertRaises(ValueError):
            require_env()

    def test_partial_results_not_returned_on_failure(self):
        # If some keys exist and others don't, the call should raise
        # rather than returning a partial dict.
        env = {"FOUND": "yes"}
        with self.assertRaises(MissingEnvError):
            require_env("FOUND", "NOT_FOUND", env=env)

    def test_uses_os_environ_by_default(self):
        import os

        os.environ["PK_TEST_VAR_XYZ"] = "present"
        try:
            result = require_env("PK_TEST_VAR_XYZ")
            self.assertEqual(result, {"PK_TEST_VAR_XYZ": "present"})
        finally:
            del os.environ["PK_TEST_VAR_XYZ"]

    def test_missing_env_error_is_environment_error(self):
        self.assertTrue(issubclass(MissingEnvError, EnvironmentError))


if __name__ == "__main__":
    unittest.main()
