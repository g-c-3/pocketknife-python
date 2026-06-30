"""Unit tests for pocketknife.secret_keeper."""

import unittest

from pocketknife.secret_keeper import DEFAULT_SENSITIVE_KEYS, mask_secrets


class TestMaskSecrets(unittest.TestCase):

    # --- basic masking ---

    def test_masks_specified_key(self):
        result = mask_secrets({"password": "secret"}, keys=["password"])
        self.assertEqual(result["password"], "***")

    def test_leaves_other_keys_untouched(self):
        result = mask_secrets({"password": "secret", "user": "alice"}, keys=["password"])
        self.assertEqual(result["user"], "alice")

    def test_default_keys_masks_common_secrets(self):
        for key in ("password", "api_key", "token", "secret", "client_secret"):
            with self.subTest(key=key):
                result = mask_secrets({key: "val"})
                self.assertEqual(result[key], "***")

    def test_custom_mask_string(self):
        result = mask_secrets({"password": "x"}, mask="[REDACTED]")
        self.assertEqual(result["password"], "[REDACTED]")

    # --- nested structures ---

    def test_masks_nested_dict(self):
        data = {"db": {"password": "secret", "host": "localhost"}}
        result = mask_secrets(data, keys=["password"])
        self.assertEqual(result["db"]["password"], "***")
        self.assertEqual(result["db"]["host"], "localhost")

    def test_masks_deeply_nested(self):
        data = {"a": {"b": {"c": {"token": "xyz"}}}}
        result = mask_secrets(data, keys=["token"])
        self.assertEqual(result["a"]["b"]["c"]["token"], "***")

    def test_masks_list_of_dicts(self):
        data = [{"password": "a"}, {"password": "b"}]
        result = mask_secrets(data, keys=["password"])
        self.assertEqual(result[0]["password"], "***")
        self.assertEqual(result[1]["password"], "***")

    def test_masks_dicts_inside_list_inside_dict(self):
        data = {"users": [{"name": "alice", "token": "t1"}, {"name": "bob", "token": "t2"}]}
        result = mask_secrets(data, keys=["token"])
        self.assertEqual(result["users"][0]["token"], "***")
        self.assertEqual(result["users"][1]["token"], "***")
        self.assertEqual(result["users"][0]["name"], "alice")

    def test_masks_tuple_contents(self):
        data = ({"password": "x"}, {"password": "y"})
        result = mask_secrets(data, keys=["password"])
        self.assertIsInstance(result, tuple)
        self.assertEqual(result[0]["password"], "***")

    # --- case sensitivity ---

    def test_case_insensitive_by_default(self):
        result = mask_secrets({"Password": "x", "API_KEY": "y"}, keys=["password", "api_key"])
        self.assertEqual(result["Password"], "***")
        self.assertEqual(result["API_KEY"], "***")

    def test_case_sensitive_does_not_match_wrong_case(self):
        result = mask_secrets({"Password": "x"}, keys=["password"], case_sensitive=True)
        self.assertNotEqual(result["Password"], "***")

    def test_case_sensitive_matches_exact(self):
        result = mask_secrets({"password": "x"}, keys=["password"], case_sensitive=True)
        self.assertEqual(result["password"], "***")

    # --- mutation safety ---

    def test_original_not_mutated_by_default(self):
        original = {"password": "secret", "user": "alice"}
        mask_secrets(original, keys=["password"])
        self.assertEqual(original["password"], "secret")

    def test_in_place_mutates_original(self):
        original = {"password": "secret"}
        mask_secrets(original, keys=["password"], in_place=True)
        self.assertEqual(original["password"], "***")

    # --- edge cases ---

    def test_empty_dict_returns_empty(self):
        self.assertEqual(mask_secrets({}, keys=["password"]), {})

    def test_empty_keys_list_masks_nothing(self):
        data = {"password": "secret"}
        result = mask_secrets(data, keys=[])
        self.assertEqual(result["password"], "secret")

    def test_scalar_data_returned_unchanged(self):
        self.assertEqual(mask_secrets("hello", keys=["password"]), "hello")
        self.assertIsNone(mask_secrets(None, keys=["password"]))

    def test_non_string_dict_keys_not_crashed(self):
        data = {1: "safe", "password": "secret"}
        result = mask_secrets(data, keys=["password"])
        self.assertEqual(result["password"], "***")
        self.assertEqual(result[1], "safe")

    def test_default_sensitive_keys_exported(self):
        self.assertIn("password", DEFAULT_SENSITIVE_KEYS)
        self.assertIn("api_key", DEFAULT_SENSITIVE_KEYS)
        self.assertIn("token", DEFAULT_SENSITIVE_KEYS)


if __name__ == "__main__":
    unittest.main()
