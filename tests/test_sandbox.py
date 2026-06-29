"""
Tests for pocketknife.sandbox
"""

import os
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pocketknife.sandbox import temp_workspace


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def collect_rel_paths(root: Path) -> set:
    """Return a set of relative path strings for all files under *root*."""
    return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}


# ---------------------------------------------------------------------------
# Basic lifecycle
# ---------------------------------------------------------------------------

class TestLifecycle:

    def test_yields_a_path(self):
        with temp_workspace() as ws:
            assert isinstance(ws, Path)

    def test_directory_exists_inside_block(self):
        with temp_workspace() as ws:
            assert ws.exists()
            assert ws.is_dir()

    def test_directory_deleted_after_block(self):
        with temp_workspace() as ws:
            captured = ws
        assert not captured.exists()

    def test_directory_deleted_after_normal_exception(self):
        captured = None
        try:
            with temp_workspace() as ws:
                captured = ws
                raise ValueError("oops")
        except ValueError:
            pass
        assert captured is not None
        assert not captured.exists()

    def test_exception_is_re_raised(self):
        with pytest.raises(RuntimeError, match="propagate me"):
            with temp_workspace():
                raise RuntimeError("propagate me")

    def test_path_is_absolute(self):
        with temp_workspace() as ws:
            assert ws.is_absolute()

    def test_files_written_inside_are_readable(self):
        with temp_workspace() as ws:
            (ws / "hello.txt").write_text("world")
            assert (ws / "hello.txt").read_text() == "world"

    def test_subdirectories_can_be_created(self):
        with temp_workspace() as ws:
            sub = ws / "nested" / "deep"
            sub.mkdir(parents=True)
            assert sub.is_dir()

    def test_each_call_yields_unique_directory(self):
        with temp_workspace() as ws1:
            with temp_workspace() as ws2:
                assert ws1 != ws2

    def test_nested_workspaces_are_independent(self):
        """Deleting the outer should not affect the inner (they're separate tmp dirs)."""
        with temp_workspace() as outer:
            with temp_workspace() as inner:
                assert outer.exists()
                assert inner.exists()
            assert not inner.exists()
            assert outer.exists()
        assert not outer.exists()


# ---------------------------------------------------------------------------
# prefix / suffix
# ---------------------------------------------------------------------------

class TestPrefixSuffix:

    def test_default_prefix(self):
        with temp_workspace() as ws:
            assert ws.name.startswith("pocketknife-")

    def test_custom_prefix(self):
        with temp_workspace(prefix="myapp-") as ws:
            assert ws.name.startswith("myapp-")

    def test_custom_suffix(self):
        with temp_workspace(suffix="-test") as ws:
            assert ws.name.endswith("-test")

    def test_empty_prefix(self):
        with temp_workspace(prefix="") as ws:
            assert ws.exists()

    def test_prefix_and_suffix_together(self):
        with temp_workspace(prefix="pre-", suffix="-suf") as ws:
            assert ws.name.startswith("pre-")
            assert ws.name.endswith("-suf")


# ---------------------------------------------------------------------------
# keep_on_error
# ---------------------------------------------------------------------------

class TestKeepOnError:

    def test_keep_on_error_false_cleans_up_after_exception(self):
        captured = None
        try:
            with temp_workspace(keep_on_error=False) as ws:
                captured = ws
                raise RuntimeError("error")
        except RuntimeError:
            pass
        assert captured is not None
        assert not captured.exists()

    def test_keep_on_error_true_preserves_dir_after_exception(self):
        captured = None
        try:
            with temp_workspace(keep_on_error=True) as ws:
                captured = ws
                raise RuntimeError("error")
        except RuntimeError:
            pass
        assert captured is not None
        assert captured.exists()
        shutil.rmtree(captured)  # manual cleanup

    def test_keep_on_error_true_still_cleans_up_on_success(self):
        with temp_workspace(keep_on_error=True) as ws:
            captured = ws
        assert not captured.exists()

    def test_keep_on_error_preserves_file_contents(self):
        captured = None
        try:
            with temp_workspace(keep_on_error=True) as ws:
                captured = ws
                (ws / "clue.txt").write_text("the butler did it")
                raise RuntimeError("crime scene")
        except RuntimeError:
            pass
        assert (captured / "clue.txt").read_text() == "the butler did it"
        shutil.rmtree(captured)


# ---------------------------------------------------------------------------
# seed
# ---------------------------------------------------------------------------

class TestSeed:

    def test_seed_creates_files(self):
        seed = {"a.txt": "hello", "b.txt": "world"}
        with temp_workspace(seed=seed) as ws:
            assert (ws / "a.txt").read_text() == "hello"
            assert (ws / "b.txt").read_text() == "world"

    def test_seed_creates_subdirectories(self):
        seed = {"sub/nested/file.txt": "deep"}
        with temp_workspace(seed=seed) as ws:
            assert (ws / "sub" / "nested" / "file.txt").read_text() == "deep"

    def test_seed_bytes_value(self):
        data = b"\x00\x01\x02\x03"
        with temp_workspace(seed={"blob.bin": data}) as ws:
            assert (ws / "blob.bin").read_bytes() == data

    def test_seed_mixed_str_and_bytes(self):
        seed = {"text.txt": "hello", "data.bin": b"\xff\xfe"}
        with temp_workspace(seed=seed) as ws:
            assert (ws / "text.txt").read_text() == "hello"
            assert (ws / "data.bin").read_bytes() == b"\xff\xfe"

    def test_seed_none_produces_empty_workspace(self):
        with temp_workspace(seed=None) as ws:
            assert list(ws.iterdir()) == []

    def test_seed_empty_dict_produces_empty_workspace(self):
        with temp_workspace(seed={}) as ws:
            assert list(ws.iterdir()) == []

    def test_seed_files_are_all_present(self):
        seed = {
            "top.txt": "t",
            "a/one.txt": "1",
            "a/two.txt": "2",
            "b/c/three.txt": "3",
        }
        with temp_workspace(seed=seed) as ws:
            assert collect_rel_paths(ws) == set(seed.keys())

    def test_seed_raises_on_non_dict(self):
        with pytest.raises(TypeError):
            with temp_workspace(seed=["a.txt"]):
                pass

    def test_seed_raises_on_invalid_value_type(self):
        with pytest.raises(TypeError):
            with temp_workspace(seed={"file.txt": 12345}):
                pass

    def test_seed_utf8_content(self):
        content = "こんにちは 🌍"
        with temp_workspace(seed={"unicode.txt": content}) as ws:
            assert (ws / "unicode.txt").read_text(encoding="utf-8") == content


# ---------------------------------------------------------------------------
# Cleanup robustness
# ---------------------------------------------------------------------------

class TestCleanupRobustness:

    def test_cleanup_removes_nested_content(self):
        captured = None
        with temp_workspace() as ws:
            captured = ws
            deep = ws / "a" / "b" / "c"
            deep.mkdir(parents=True)
            (deep / "file.txt").write_text("deep file")
        assert not captured.exists()

    def test_cleanup_on_keyboard_interrupt(self):
        captured = None
        try:
            with temp_workspace() as ws:
                captured = ws
                raise KeyboardInterrupt
        except KeyboardInterrupt:
            pass
        assert captured is not None
        assert not captured.exists()
