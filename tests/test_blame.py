"""
tests/test_blame.py
~~~~~~~~~~~~~~~~~~~
Unit tests for pocketknife.blame.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch

from pocketknife.blame import (
    _blame_message,
    _get_git_authors,
    _pick_culprit,
    blame_once,
    git_roulette,
)


class TestGetGitAuthors(unittest.TestCase):
    """Tests for the git log parsing helper."""

    def test_returns_list_of_names(self):
        """Authors parsed correctly from git log output."""
        mock_output = "Alice\nBob\nAlice\nCharlie\n"
        mock_result = MagicMock(returncode=0, stdout=mock_output)
        with patch("subprocess.run", return_value=mock_result):
            authors = _get_git_authors()
        self.assertEqual(authors, ["Alice", "Bob", "Charlie"])

    def test_deduplicates_names(self):
        """Each author appears only once even if they have many commits."""
        mock_output = "Jordan\nJordan\nJordan\nAlex\n"
        mock_result = MagicMock(returncode=0, stdout=mock_output)
        with patch("subprocess.run", return_value=mock_result):
            authors = _get_git_authors()
        self.assertEqual(authors, ["Jordan", "Alex"])

    def test_returns_empty_list_on_git_not_found(self):
        """Returns [] gracefully when git is not installed."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            authors = _get_git_authors()
        self.assertEqual(authors, [])

    def test_returns_empty_list_on_nonzero_returncode(self):
        """Returns [] when git returns a non-zero exit code (e.g. not a repo)."""
        mock_result = MagicMock(returncode=128, stdout="")
        with patch("subprocess.run", return_value=mock_result):
            authors = _get_git_authors()
        self.assertEqual(authors, [])

    def test_returns_empty_list_on_timeout(self):
        """Returns [] when git takes too long."""
        import subprocess
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("git", 5)):
            authors = _get_git_authors()
        self.assertEqual(authors, [])

    def test_strips_whitespace_from_names(self):
        """Leading/trailing whitespace is stripped from each name."""
        mock_output = "  Alice  \n  Bob\n"
        mock_result = MagicMock(returncode=0, stdout=mock_output)
        with patch("subprocess.run", return_value=mock_result):
            authors = _get_git_authors()
        self.assertEqual(authors, ["Alice", "Bob"])

    def test_ignores_blank_lines(self):
        """Blank lines in git output are skipped."""
        mock_output = "Alice\n\n\nBob\n"
        mock_result = MagicMock(returncode=0, stdout=mock_output)
        with patch("subprocess.run", return_value=mock_result):
            authors = _get_git_authors()
        self.assertEqual(authors, ["Alice", "Bob"])


class TestPickCulprit(unittest.TestCase):
    """Tests for the random author selector."""

    def test_returns_none_for_empty_list(self):
        self.assertIsNone(_pick_culprit([]))

    def test_returns_single_author_when_only_one(self):
        self.assertEqual(_pick_culprit(["Solo"]), "Solo")

    def test_returns_one_of_the_authors(self):
        authors = ["Alice", "Bob", "Charlie"]
        culprit = _pick_culprit(authors)
        self.assertIn(culprit, authors)


class TestBlameMessage(unittest.TestCase):
    """Tests for the blame string formatter."""

    def test_returns_string(self):
        msg = _blame_message("Jordan")
        self.assertIsInstance(msg, str)

    def test_contains_culprit_name(self):
        """The culprit's name should appear somewhere in the message."""
        msg = _blame_message("Jordan")
        self.assertIn("Jordan", msg)

    def test_fallback_message_when_no_culprit(self):
        """No culprit → returns a no-git fallback string (no KeyError etc.)."""
        msg = _blame_message(None)
        self.assertIsInstance(msg, str)
        self.assertTrue(len(msg) > 0)

    def test_deterministic_with_fixed_seed(self):
        """With a fixed random seed, the same template is chosen every time."""
        import random
        random.seed(42)
        msg1 = _blame_message("Jordan")
        random.seed(42)
        msg2 = _blame_message("Jordan")
        self.assertEqual(msg1, msg2)


class TestBlameOnce(unittest.TestCase):
    """Tests for the public blame_once() convenience function."""

    def test_returns_string_starting_with_emoji(self):
        mock_result = MagicMock(returncode=0, stdout="Alex\nBob\n")
        with patch("subprocess.run", return_value=mock_result):
            result = blame_once()
        self.assertTrue(result.startswith("🎲 Git Roulette says:"))

    def test_works_without_git(self):
        """blame_once() should not raise even when git is unavailable."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = blame_once()
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("🎲 Git Roulette says:"))

    def test_output_contains_author_when_git_available(self):
        mock_result = MagicMock(returncode=0, stdout="UniqueNameXYZ\n")
        with patch("subprocess.run", return_value=mock_result):
            result = blame_once()
        self.assertIn("UniqueNameXYZ", result)


class TestGitRoulette(unittest.TestCase):
    """Tests for the git_roulette() hook registration."""

    def setUp(self):
        """Save the original excepthook so we can restore it after each test."""
        self._original_hook = sys.excepthook

    def tearDown(self):
        """Restore the original excepthook."""
        sys.excepthook = self._original_hook

    def test_registers_custom_excepthook(self):
        """git_roulette() replaces sys.excepthook with a custom callable."""
        original = sys.excepthook
        git_roulette()
        self.assertIsNot(sys.excepthook, original)

    def test_hook_writes_blame_line(self):
        """The installed hook appends a blame line after the traceback."""
        import io
        stream = io.StringIO()
        git_roulette(stream=stream)

        mock_result = MagicMock(returncode=0, stdout="TestAuthor\n")
        with patch("subprocess.run", return_value=mock_result):
            try:
                raise ValueError("test crash")
            except ValueError:
                exc_type, exc_value, exc_tb = sys.exc_info()
                sys.excepthook(exc_type, exc_value, exc_tb)

        output = stream.getvalue()
        self.assertIn("🎲 Git Roulette says:", output)

    def test_hook_writes_traceback_before_blame(self):
        """The original traceback is preserved and appears before the blame line."""
        import io
        stream = io.StringIO()
        git_roulette(stream=stream)

        with patch("subprocess.run", side_effect=FileNotFoundError):
            try:
                raise RuntimeError("kaboom")
            except RuntimeError:
                exc_type, exc_value, exc_tb = sys.exc_info()
                sys.excepthook(exc_type, exc_value, exc_tb)

        output = stream.getvalue()
        blame_pos = output.find("🎲 Git Roulette says:")
        traceback_pos = output.find("RuntimeError")
        self.assertGreater(blame_pos, traceback_pos)

    def test_hook_works_without_git(self):
        """Hook should not raise even when git is not installed."""
        import io
        stream = io.StringIO()
        git_roulette(stream=stream)

        with patch("subprocess.run", side_effect=FileNotFoundError):
            try:
                raise RuntimeError("no git")
            except RuntimeError:
                exc_type, exc_value, exc_tb = sys.exc_info()
                # Should not raise
                sys.excepthook(exc_type, exc_value, exc_tb)

        output = stream.getvalue()
        self.assertIn("🎲 Git Roulette says:", output)


if __name__ == "__main__":
    unittest.main()
