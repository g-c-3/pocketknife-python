"""
Tests for pocketknife.flatpack
"""

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pocketknife.flatpack import flatten, unflatten


# ---------------------------------------------------------------------------
# flatten()
# ---------------------------------------------------------------------------

class TestFlatten:

    def test_simple_nested(self):
        d = {"a": {"b": 1}}
        assert flatten(d) == {"a.b": 1}

    def test_deeply_nested(self):
        d = {"a": {"b": {"c": {"d": 42}}}}
        assert flatten(d) == {"a.b.c.d": 42}

    def test_mixed_depth(self):
        d = {"x": 1, "y": {"z": 2}}
        assert flatten(d) == {"x": 1, "y.z": 2}

    def test_already_flat(self):
        d = {"a": 1, "b": 2, "c": 3}
        assert flatten(d) == {"a": 1, "b": 2, "c": 3}

    def test_empty_dict(self):
        assert flatten({}) == {}

    def test_empty_nested_dict_preserved_as_leaf(self):
        d = {"a": {}}
        result = flatten(d)
        assert result == {"a": {}}

    def test_list_value_is_leaf(self):
        d = {"scores": [1, 2, 3]}
        assert flatten(d) == {"scores": [1, 2, 3]}

    def test_none_value(self):
        d = {"a": {"b": None}}
        assert flatten(d) == {"a.b": None}

    def test_bool_value(self):
        d = {"flags": {"enabled": True, "debug": False}}
        assert flatten(d) == {"flags.enabled": True, "flags.debug": False}

    def test_custom_separator(self):
        d = {"a": {"b": 1}}
        assert flatten(d, sep="/") == {"a/b": 1}

    def test_custom_separator_double_char(self):
        d = {"a": {"b": {"c": 7}}}
        assert flatten(d, sep="__") == {"a__b__c": 7}

    def test_does_not_mutate_original(self):
        d = {"a": {"b": 1}}
        original_copy = {"a": {"b": 1}}
        flatten(d)
        assert d == original_copy

    def test_returns_new_dict(self):
        d = {"a": 1}
        result = flatten(d)
        assert result is not d

    def test_raises_on_non_dict_input(self):
        with pytest.raises(TypeError):
            flatten([1, 2, 3])

    def test_raises_on_empty_sep(self):
        with pytest.raises(TypeError):
            flatten({"a": 1}, sep="")

    def test_raises_on_non_string_sep(self):
        with pytest.raises(TypeError):
            flatten({"a": 1}, sep=42)

    def test_integer_keys(self):
        # Dicts can have integer keys; they should be stringified
        d = {1: {2: "hello"}}
        result = flatten(d)
        assert result == {"1.2": "hello"}

    def test_realistic_config(self):
        config = {
            "db": {"host": "localhost", "port": 5432},
            "cache": {"ttl": 300},
            "debug": False,
        }
        expected = {
            "db.host": "localhost",
            "db.port": 5432,
            "cache.ttl": 300,
            "debug": False,
        }
        assert flatten(config) == expected


# ---------------------------------------------------------------------------
# unflatten()
# ---------------------------------------------------------------------------

class TestUnflatten:

    def test_simple(self):
        d = {"a.b": 1}
        assert unflatten(d) == {"a": {"b": 1}}

    def test_deeply_nested(self):
        d = {"a.b.c.d": 42}
        assert unflatten(d) == {"a": {"b": {"c": {"d": 42}}}}

    def test_mixed_depth(self):
        d = {"x": 1, "y.z": 2}
        assert unflatten(d) == {"x": 1, "y": {"z": 2}}

    def test_already_flat_no_sep(self):
        d = {"a": 1, "b": 2}
        assert unflatten(d) == {"a": 1, "b": 2}

    def test_empty_dict(self):
        assert unflatten({}) == {}

    def test_none_value(self):
        assert unflatten({"a.b": None}) == {"a": {"b": None}}

    def test_list_value_preserved(self):
        d = {"scores": [1, 2, 3]}
        assert unflatten(d) == {"scores": [1, 2, 3]}

    def test_custom_separator(self):
        d = {"a/b": 1}
        assert unflatten(d, sep="/") == {"a": {"b": 1}}

    def test_does_not_mutate_original(self):
        d = {"a.b": 1}
        original_copy = {"a.b": 1}
        unflatten(d)
        assert d == original_copy

    def test_returns_new_dict(self):
        d = {"a": 1}
        result = unflatten(d)
        assert result is not d

    def test_raises_on_non_dict_input(self):
        with pytest.raises(TypeError):
            unflatten("a.b=1")

    def test_raises_on_empty_sep(self):
        with pytest.raises(TypeError):
            unflatten({"a.b": 1}, sep="")

    def test_raises_on_non_string_sep(self):
        with pytest.raises(TypeError):
            unflatten({"a.b": 1}, sep=None)

    def test_key_conflict_raises(self):
        # "a" is set as a leaf (value 99), but "a.b" tries to treat "a" as a dict
        with pytest.raises(ValueError):
            unflatten({"a": 99, "a.b": 1})

    def test_shared_prefix_builds_one_subtree(self):
        d = {"db.host": "localhost", "db.port": 5432}
        result = unflatten(d)
        assert result == {"db": {"host": "localhost", "port": 5432}}


# ---------------------------------------------------------------------------
# Round-trip
# ---------------------------------------------------------------------------

class TestRoundTrip:

    def _roundtrip(self, original, sep="."):
        flat = flatten(original, sep=sep)
        rebuilt = unflatten(flat, sep=sep)
        assert rebuilt == original, f"Round-trip failed:\n  original={original}\n  flat={flat}\n  rebuilt={rebuilt}"

    def test_simple(self):
        self._roundtrip({"a": {"b": 1}})

    def test_deep(self):
        self._roundtrip({"a": {"b": {"c": {"d": {"e": "deep"}}}}})

    def test_mixed_types(self):
        self._roundtrip({
            "name": "pocketknife",
            "version": 7,
            "config": {"debug": False, "timeout": 30.5},
            "tags": ["python", "utility"],
        })

    def test_custom_sep(self):
        self._roundtrip({"x": {"y": {"z": 0}}}, sep="->")

    def test_empty(self):
        self._roundtrip({})

    def test_flat_only(self):
        self._roundtrip({"a": 1, "b": 2, "c": 3})

    def test_realistic_config(self):
        self._roundtrip({
            "database": {
                "host": "localhost",
                "port": 5432,
                "credentials": {"user": "admin", "password": "s3cr3t"},
            },
            "feature_flags": {"dark_mode": True, "beta": False},
            "version": "1.0.0",
        })
