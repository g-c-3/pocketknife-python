"""Unit tests for pocketknife.gossip."""

import io
import unittest

from pocketknife.gossip import tell_me_about


class TestTellMeAbout(unittest.TestCase):
    def _capture(self, obj, **kwargs):
        """Run tell_me_about and capture output to a string."""
        buf = io.StringIO()
        result = tell_me_about(obj, output=buf, **kwargs)
        return buf.getvalue(), result

    # --- return value ---

    def test_returns_string(self):
        out, result = self._capture([])
        self.assertIsInstance(result, str)

    def test_return_matches_printed_output(self):
        out, result = self._capture([])
        self.assertEqual(out.strip(), result.strip())

    # --- header ---

    def test_header_contains_type_name(self):
        out, _ = self._capture([])
        self.assertIn("list", out.splitlines()[0])

    def test_header_contains_value_for_scalar(self):
        out, _ = self._capture(42)
        self.assertIn("42", out.splitlines()[0])

    def test_header_for_custom_object(self):
        class MyClass:
            pass
        out, _ = self._capture(MyClass())
        self.assertIn("MyClass", out)

    # --- member listing ---

    def test_list_methods_present(self):
        out, _ = self._capture([])
        self.assertIn("append", out)
        self.assertIn("extend", out)

    def test_dict_methods_present(self):
        out, _ = self._capture({})
        self.assertIn("keys", out)
        self.assertIn("values", out)
        self.assertIn("items", out)

    def test_shows_method_kind(self):
        out, _ = self._capture([])
        self.assertIn("method", out)

    def test_shows_docstring_fragment(self):
        out, _ = self._capture([])
        # "append" has a well-known one-liner docstring
        self.assertIn("Append", out)

    # --- private / dunder filtering ---

    def test_private_members_excluded_by_default(self):
        class Obj:
            def _private(self):
                pass
            def public(self):
                pass
        out, _ = self._capture(Obj())
        self.assertIn("public", out)
        self.assertNotIn("_private", out)

    def test_private_members_included_when_requested(self):
        class Obj:
            def _private(self):
                pass
        out, _ = self._capture(Obj(), include_private=True)
        self.assertIn("_private", out)

    def test_dunder_members_excluded_by_default(self):
        out, _ = self._capture([])
        self.assertNotIn("__len__", out)

    def test_dunder_members_included_when_requested(self):
        out, _ = self._capture([], include_dunder=True)
        self.assertIn("__len__", out)

    # --- docstring truncation ---

    def test_long_docstring_truncated(self):
        out, _ = self._capture(42, max_doc_length=20)
        # Every summary cell should fit within the column (plus ellipsis)
        for line in out.splitlines():
            if line.startswith("|") and "Name" not in line and "---" not in line:
                # Extract the summary column (last pipe-delimited cell)
                parts = line.split("|")
                if len(parts) >= 4:
                    summary = parts[3].strip()
                    self.assertLessEqual(len(summary), 21)  # 20 + ellipsis char

    # --- member count footer ---

    def test_footer_shows_member_count(self):
        out, _ = self._capture([])
        self.assertIn("member(s) shown", out)

    # --- custom attributes ---

    def test_shows_attributes_of_custom_class(self):
        class Config:
            host = "localhost"
            port = 5432

        out, _ = self._capture(Config())
        self.assertIn("host", out)
        self.assertIn("port", out)

    # --- edge cases ---

    def test_empty_object_does_not_crash(self):
        class Empty:
            pass
        out, _ = self._capture(Empty())
        self.assertIsInstance(out, str)

    def test_output_written_to_provided_buffer(self):
        buf = io.StringIO()
        tell_me_about([], output=buf)
        self.assertGreater(len(buf.getvalue()), 0)


if __name__ == "__main__":
    unittest.main()
