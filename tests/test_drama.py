"""
Tests for pocketknife.drama
"""

import sys
import os
import io
import re

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from pocketknife.drama import dramatic_progress, excuse_generator


# ===========================================================================
# dramatic_progress
# ===========================================================================

class TestDramaticProgress:

    def _capture(self, iterable, **kwargs):
        """Run dramatic_progress, capturing stderr output and collected items."""
        buf = io.StringIO()
        kwargs.setdefault("stream", buf)
        kwargs.setdefault("delay", 0)
        kwargs.setdefault("anxiety_frequency", 0)  # deterministic by default
        items = list(dramatic_progress(iterable, **kwargs))
        return items, buf.getvalue()

    # --- yields all items unchanged ---

    def test_yields_all_items(self):
        items, _ = self._capture(range(5))
        assert items == [0, 1, 2, 3, 4]

    def test_yields_strings(self):
        data = ["a", "b", "c"]
        items, _ = self._capture(data)
        assert items == data

    def test_empty_iterable(self):
        items, output = self._capture([])
        assert items == []
        assert "nothing to do" in output

    def test_single_item(self):
        items, _ = self._capture([42])
        assert items == [42]

    def test_items_unchanged(self):
        data = [{"key": "value"}, None, 3.14]
        items, _ = self._capture(data)
        assert items == data

    # --- output structure ---

    def test_bar_reaches_100_percent(self):
        _, output = self._capture(range(4))
        assert "100%" in output

    def test_desc_appears_in_output(self):
        _, output = self._capture(range(3), desc="Loading stuff")
        assert "Loading stuff" in output

    def test_done_message_at_end(self):
        _, output = self._capture(range(3))
        assert "done" in output.lower()

    def test_bar_contains_block_chars(self):
        _, output = self._capture(range(5))
        assert "█" in output or "░" in output

    def test_item_count_in_output(self):
        _, output = self._capture(range(3))
        # Should see something like (3/3)
        assert "3/3" in output

    def test_custom_width_respected(self):
        # Width 10 means at most 10 block chars; can check by looking at bar content
        _, output = self._capture(range(2), width=10)
        assert "░" in output or "█" in output

    # --- anxiety messages ---

    def test_anxiety_frequency_zero_no_anxiety(self):
        _, output = self._capture(range(10), anxiety_frequency=0.0)
        assert "💭" not in output

    def test_anxiety_frequency_one_always_anxiety(self):
        # With frequency=1.0 and more than 1 item, at least one anxiety message appears
        _, output = self._capture(range(5), anxiety_frequency=1.0)
        assert "💭" in output

    def test_anxiety_not_shown_on_last_item(self):
        # Even at 100% frequency, no anxiety after the last item (before "done")
        buf = io.StringIO()
        list(dramatic_progress([1], stream=buf, delay=0, anxiety_frequency=1.0))
        output = buf.getvalue()
        # The only output should be the bar line + done message, no mid-loop anxiety
        assert output.count("💭") == 0  # single-item: no "i < total - 1" case

    # --- stress mood indicators ---

    def test_green_mood_at_start(self):
        buf = io.StringIO()
        gen = dramatic_progress(list(range(100)), stream=buf, delay=0, anxiety_frequency=0)
        next(gen)  # consume first item
        output = buf.getvalue()
        assert "🟢" in output

    # --- generator protocol ---

    def test_is_generator(self):
        import types
        gen = dramatic_progress(range(3), stream=io.StringIO(), delay=0)
        assert isinstance(gen, types.GeneratorType)

    def test_lazy_evaluation(self):
        """Items should be yielded one at a time, not all at once."""
        buf = io.StringIO()
        gen = dramatic_progress([10, 20, 30], stream=buf, delay=0, anxiety_frequency=0)
        first = next(gen)
        assert first == 10

    def test_stream_parameter(self):
        custom_stream = io.StringIO()
        list(dramatic_progress(range(3), stream=custom_stream, delay=0, anxiety_frequency=0))
        assert len(custom_stream.getvalue()) > 0


# ===========================================================================
# excuse_generator
# ===========================================================================

class TestExcuseGenerator:

    def test_returns_string(self):
        result = excuse_generator()
        assert isinstance(result, str)

    def test_non_empty(self):
        result = excuse_generator()
        assert len(result.strip()) > 0

    def test_contains_error_type(self):
        # Every template starts with a known Python exception class
        known_errors = [
            "RuntimeError", "MemoryError", "RecursionError", "OSError",
            "TimeoutError", "ValueError", "KeyError", "ConnectionResetError",
            "PermissionError", "AttributeError", "IndexError", "TypeError",
            "ImportError", "ZeroDivisionError", "AssertionError",
        ]
        result = excuse_generator()
        assert any(err in result for err in known_errors)

    def test_with_timestamp_contains_timestamp(self):
        result = excuse_generator(include_timestamp=True, include_traceback=False)
        # Should contain a datetime-looking string like [2024-03-14 09:26:53]
        assert re.search(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]", result)

    def test_without_timestamp(self):
        result = excuse_generator(include_timestamp=False, include_traceback=False)
        assert not re.search(r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]", result)

    def test_with_traceback_contains_traceback(self):
        result = excuse_generator(include_timestamp=False, include_traceback=True)
        assert "Traceback (most recent call last):" in result

    def test_without_traceback(self):
        result = excuse_generator(include_timestamp=False, include_traceback=False)
        assert "Traceback" not in result

    def test_different_calls_differ(self):
        # Run 10 times; expect at least 2 different results (no stuck seed)
        results = {excuse_generator() for _ in range(10)}
        assert len(results) > 1

    def test_multiline_by_default(self):
        result = excuse_generator()
        assert "\n" in result

    def test_critical_label_present_with_timestamp(self):
        result = excuse_generator(include_timestamp=True)
        assert "CRITICAL" in result

    def test_no_unfilled_placeholders(self):
        # Check that no {key} placeholders survive in the output
        for _ in range(20):
            result = excuse_generator()
            assert not re.search(r"\{[a-z_]+[!:}]", result), (
                f"Unfilled placeholder found in: {result}"
            )

    def test_traceback_contains_file_references(self):
        result = excuse_generator(include_timestamp=False, include_traceback=True)
        assert 'File "' in result

    def test_minimal_mode(self):
        result = excuse_generator(include_timestamp=False, include_traceback=False)
        # Should be a single line (no newlines from timestamp or traceback)
        assert result.count("\n") == 0
