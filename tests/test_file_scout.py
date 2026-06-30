"""Unit tests for pocketknife.file_scout."""

import re
import tempfile
import unittest
from pathlib import Path

from pocketknife.file_scout import find_all, find_first


class TestFindFirst(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

        (self.root / "alpha.txt").touch()
        (self.root / "beta.csv").touch()
        (self.root / "sub").mkdir()
        (self.root / "sub" / "gamma.txt").touch()
        (self.root / "sub" / "delta.log").touch()
        (self.root / ".hidden").mkdir()
        (self.root / ".hidden" / "secret.txt").touch()

    def tearDown(self):
        self._tmp.cleanup()

    def test_returns_path_on_match(self):
        result = find_first(r"\.csv$", root=self.root)
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "beta.csv")

    def test_returns_none_when_no_match(self):
        result = find_first(r"\.parquet$", root=self.root)
        self.assertIsNone(result)

    def test_finds_file_in_subdirectory(self):
        result = find_first(r"\.log$", root=self.root)
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "delta.log")

    def test_ignores_hidden_by_default(self):
        result = find_first(r"secret", root=self.root)
        self.assertIsNone(result)

    def test_finds_hidden_when_flag_off(self):
        result = find_first(r"secret", root=self.root, ignore_hidden=False)
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "secret.txt")

    def test_max_depth_zero_limits_to_root(self):
        # gamma.txt is in sub/, so depth=0 should not find it
        result = find_first(r"gamma", root=self.root, max_depth=0)
        self.assertIsNone(result)

    def test_max_depth_one_reaches_subdirectory(self):
        result = find_first(r"gamma", root=self.root, max_depth=1)
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "gamma.txt")

    def test_case_insensitive_flag(self):
        (self.root / "UPPER.TXT").touch()
        result = find_first(r"upper\.txt", root=self.root, flags=re.IGNORECASE)
        self.assertIsNotNone(result)
        self.assertEqual(result.name, "UPPER.TXT")

    def test_raises_if_root_missing(self):
        with self.assertRaises(FileNotFoundError):
            find_first(r".*", root="/nonexistent/path/xyz")

    def test_raises_if_root_is_file(self):
        file_path = self.root / "alpha.txt"
        with self.assertRaises(NotADirectoryError):
            find_first(r".*", root=file_path)


class TestFindAll(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

        (self.root / "a.log").touch()
        (self.root / "b.log").touch()
        (self.root / "c.txt").touch()
        (self.root / "sub").mkdir()
        (self.root / "sub" / "d.log").touch()

    def tearDown(self):
        self._tmp.cleanup()

    def test_returns_all_matches(self):
        results = find_all(r"\.log$", root=self.root)
        names = [p.name for p in results]
        self.assertIn("a.log", names)
        self.assertIn("b.log", names)
        self.assertIn("d.log", names)
        self.assertEqual(len(results), 3)

    def test_returns_empty_list_on_no_match(self):
        self.assertEqual(find_all(r"\.parquet$", root=self.root), [])

    def test_results_are_sorted(self):
        results = find_all(r"\.log$", root=self.root)
        self.assertEqual(results, sorted(results))

    def test_max_depth_limits_results(self):
        results = find_all(r"\.log$", root=self.root, max_depth=0)
        names = [p.name for p in results]
        self.assertIn("a.log", names)
        self.assertNotIn("d.log", names)

    def test_returns_path_objects(self):
        results = find_all(r"\.txt$", root=self.root)
        self.assertTrue(all(isinstance(p, Path) for p in results))


if __name__ == "__main__":
    unittest.main()
