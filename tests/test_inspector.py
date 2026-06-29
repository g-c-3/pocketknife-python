"""
Tests for pocketknife.inspector
"""

import io
import sys
import os
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pocketknife.inspector import snoop, stopwatch, _human_bytes, _safe_len, _value_preview


# ---------------------------------------------------------------------------
# _human_bytes (internal helper — tested directly for thoroughness)
# ---------------------------------------------------------------------------

class TestHumanBytes:

    def test_bytes(self):
        assert _human_bytes(0) == "0 B"
        assert _human_bytes(500) == "500 B"
        assert _human_bytes(1023) == "1023 B"

    def test_kilobytes(self):
        assert _human_bytes(1024) == "1.00 KB"
        assert _human_bytes(2048) == "2.00 KB"

    def test_megabytes(self):
        assert _human_bytes(1024 * 1024) == "1.00 MB"

    def test_gigabytes(self):
        assert _human_bytes(1024 ** 3) == "1.00 GB"


# ---------------------------------------------------------------------------
# _safe_len (internal helper)
# ---------------------------------------------------------------------------

class TestSafeLen:

    def test_list(self):     assert _safe_len([1, 2, 3]) == 3
    def test_str(self):      assert _safe_len("hello") == 5
    def test_dict(self):     assert _safe_len({"a": 1}) == 1
    def test_set(self):      assert _safe_len({1, 2}) == 2
    def test_int(self):      assert _safe_len(42) is None
    def test_float(self):    assert _safe_len(3.14) is None
    def test_none(self):     assert _safe_len(None) is None
    def test_bool(self):     assert _safe_len(True) is None


# ---------------------------------------------------------------------------
# _value_preview (internal helper)
# ---------------------------------------------------------------------------

class TestValuePreview:

    def test_short_value_unchanged(self):
        assert _value_preview(42) == "42"

    def test_truncation(self):
        long_list = list(range(1000))
        preview = _value_preview(long_list, max_len=20)
        assert len(preview) == 20
        assert preview.endswith("...")

    def test_exactly_at_limit_not_truncated(self):
        s = "x" * 10
        preview = _value_preview(s, max_len=12)  # repr adds quotes → 12 chars
        assert "..." not in preview


# ---------------------------------------------------------------------------
# snoop()
# ---------------------------------------------------------------------------

class TestSnoop:

    def _capture(self, *args, **kwargs):
        buf = io.StringIO()
        snoop(*args, stream=buf, **kwargs)
        return buf.getvalue()

    # --- return value ---

    def test_returns_original_object(self):
        obj = [1, 2, 3]
        result = snoop(obj, stream=io.StringIO())
        assert result is obj

    def test_returns_int_unchanged(self):
        assert snoop(99, stream=io.StringIO()) == 99

    def test_returns_none_unchanged(self):
        assert snoop(None, stream=io.StringIO()) is None

    def test_inline_chaining(self):
        result = snoop({"a": 1}, stream=io.StringIO())["a"]
        assert result == 1

    # --- output content ---

    def test_type_line_present(self):
        out = self._capture(42)
        assert "type" in out
        assert "int" in out

    def test_size_line_present(self):
        out = self._capture(42)
        assert "size" in out
        assert "B" in out

    def test_value_line_present(self):
        out = self._capture(42)
        assert "value" in out
        assert "42" in out

    def test_len_line_for_list(self):
        out = self._capture([1, 2, 3])
        assert "len" in out
        assert "3" in out

    def test_no_len_line_for_int(self):
        out = self._capture(42)
        assert "len" not in out

    def test_no_len_line_for_float(self):
        out = self._capture(3.14)
        assert "len" not in out

    def test_no_len_line_for_none(self):
        out = self._capture(None)
        assert "len" not in out

    def test_len_line_for_string(self):
        out = self._capture("hello")
        assert "len" in out
        assert "5" in out

    def test_len_line_for_dict(self):
        out = self._capture({"a": 1, "b": 2})
        assert "len" in out
        assert "2" in out

    # --- label ---

    def test_label_appears_in_output(self):
        out = self._capture(42, label="my_var")
        assert "my_var" in out

    def test_no_label_still_produces_header(self):
        out = self._capture(42)
        assert "─" in out

    # --- type name formatting ---

    def test_builtin_type_no_module_prefix(self):
        out = self._capture(42)
        assert "builtins" not in out
        assert "int" in out

    def test_custom_class_shows_qualified_name(self):
        class MyThing:
            pass
        out = self._capture(MyThing())
        assert "MyThing" in out

    # --- stream ---

    def test_default_stream_is_stdout(self, capsys):
        snoop(42)
        captured = capsys.readouterr()
        assert "int" in captured.out

    def test_custom_stream_receives_output(self):
        buf = io.StringIO()
        snoop(42, stream=buf)
        assert len(buf.getvalue()) > 0

    def test_stdout_not_written_when_custom_stream(self, capsys):
        buf = io.StringIO()
        snoop(42, stream=buf)
        captured = capsys.readouterr()
        assert captured.out == ""

    # --- long value truncation ---

    def test_long_value_truncated_in_output(self):
        long_str = "x" * 200
        out = self._capture(long_str)
        assert "..." in out

    # --- various types ---

    def test_set(self):
        out = self._capture({1, 2, 3})
        assert "set" in out
        assert "len" in out

    def test_tuple(self):
        out = self._capture((1, 2))
        assert "tuple" in out
        assert "len" in out

    def test_bool(self):
        out = self._capture(True)
        assert "bool" in out

    def test_bytes_type(self):
        out = self._capture(b"hello")
        assert "bytes" in out
        assert "len" in out


# ---------------------------------------------------------------------------
# stopwatch()
# ---------------------------------------------------------------------------

class TestStopwatch:

    def _run(self, **kwargs):
        buf = io.StringIO()
        with stopwatch(stream=buf, **kwargs):
            pass
        return buf.getvalue()

    # --- output format ---

    def test_output_contains_label(self):
        out = self._run(label="mytask")
        assert "mytask" in out

    def test_default_label(self):
        out = self._run()
        assert "elapsed" in out

    def test_output_contains_seconds_unit(self):
        out = self._run()
        assert " s" in out

    def test_output_is_single_line(self):
        out = self._run()
        assert out.count("\n") == 1  # exactly one newline (from print)

    def test_precision_controls_decimal_places(self):
        out = self._run(precision=2)
        # format: "[label] 0.XX s"
        number_part = out.split("]")[1].strip().split(" s")[0]
        decimal_places = len(number_part.split(".")[1]) if "." in number_part else 0
        assert decimal_places == 2

    def test_precision_zero(self):
        out = self._run(precision=0)
        assert "." not in out.split("]")[1].split(" s")[0]

    # --- timing accuracy ---

    def test_elapsed_time_is_plausible(self):
        buf = io.StringIO()
        with stopwatch(stream=buf):
            time.sleep(0.05)
        out = buf.getvalue()
        number = float(out.split("]")[1].strip().rstrip(" s"))
        assert number >= 0.04  # at least ~50ms, allow clock slack

    def test_elapsed_is_non_negative(self):
        buf = io.StringIO()
        with stopwatch(stream=buf):
            pass
        out = buf.getvalue()
        number = float(out.split("]")[1].strip().rstrip(" s"))
        assert number >= 0.0

    # --- exception handling ---

    def test_timing_printed_even_on_exception(self):
        buf = io.StringIO()
        try:
            with stopwatch(stream=buf):
                raise RuntimeError("boom")
        except RuntimeError:
            pass
        assert "elapsed" in buf.getvalue()
        assert " s" in buf.getvalue()

    def test_exception_is_re_raised(self):
        with pytest.raises(ValueError, match="re-raise me"):
            with stopwatch(stream=io.StringIO()):
                raise ValueError("re-raise me")

    # --- stream ---

    def test_default_stream_is_stdout(self, capsys):
        with stopwatch():
            pass
        captured = capsys.readouterr()
        assert "elapsed" in captured.out

    def test_custom_stream_receives_output(self):
        buf = io.StringIO()
        with stopwatch(stream=buf):
            pass
        assert len(buf.getvalue()) > 0

    def test_stdout_not_written_when_custom_stream(self, capsys):
        buf = io.StringIO()
        with stopwatch(stream=buf):
            pass
        captured = capsys.readouterr()
        assert captured.out == ""

    # --- validation ---

    def test_raises_on_negative_precision(self):
        with pytest.raises(TypeError):
            with stopwatch(precision=-1):
                pass

    def test_raises_on_float_precision(self):
        with pytest.raises(TypeError):
            with stopwatch(precision=2.5):
                pass

    # --- nesting ---

    def test_nested_stopwatches(self):
        outer_buf = io.StringIO()
        inner_buf = io.StringIO()
        with stopwatch(label="outer", stream=outer_buf):
            with stopwatch(label="inner", stream=inner_buf):
                time.sleep(0.01)
        assert "outer" in outer_buf.getvalue()
        assert "inner" in inner_buf.getvalue()
        outer_val = float(outer_buf.getvalue().split("]")[1].strip().rstrip(" s"))
        inner_val = float(inner_buf.getvalue().split("]")[1].strip().rstrip(" s"))
        assert outer_val >= inner_val
