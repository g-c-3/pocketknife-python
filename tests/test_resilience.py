"""
Tests for pocketknife.resilience
"""

import sys
import os
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pocketknife.resilience import stubborn, fallback


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_flaky(fail_times: int, exc_type=ValueError, return_value="ok"):
    """Returns a function that raises *exc_type* the first *fail_times* calls,
    then returns *return_value*."""
    calls = {"n": 0}

    def fn():
        calls["n"] += 1
        if calls["n"] <= fail_times:
            raise exc_type(f"fail #{calls['n']}")
        return return_value

    fn.calls = calls
    return fn


# ---------------------------------------------------------------------------
# @stubborn — basic behaviour
# ---------------------------------------------------------------------------

class TestStubborn:

    def test_succeeds_first_try(self):
        @stubborn(retries=3, delay=0)
        def good():
            return 42

        assert good() == 42

    def test_succeeds_after_failures(self):
        fn = make_flaky(fail_times=2)

        @stubborn(retries=3, delay=0)
        def call():
            return fn()

        assert call() == "ok"
        assert fn.calls["n"] == 3  # 2 failures + 1 success

    def test_re_raises_after_all_retries_exhausted(self):
        @stubborn(retries=2, delay=0)
        def always_fails():
            raise RuntimeError("boom")

        with pytest.raises(RuntimeError, match="boom"):
            always_fails()

    def test_total_call_count_is_retries_plus_one(self):
        calls = {"n": 0}

        @stubborn(retries=3, delay=0)
        def always_fails():
            calls["n"] += 1
            raise OSError("nope")

        with pytest.raises(OSError):
            always_fails()

        assert calls["n"] == 4  # 1 initial + 3 retries

    def test_zero_retries_calls_once_and_raises(self):
        calls = {"n": 0}

        @stubborn(retries=0, delay=0)
        def fn():
            calls["n"] += 1
            raise ValueError("x")

        with pytest.raises(ValueError):
            fn()

        assert calls["n"] == 1

    def test_returns_correct_value(self):
        @stubborn(retries=2, delay=0)
        def fn():
            return {"data": [1, 2, 3]}

        assert fn() == {"data": [1, 2, 3]}

    def test_passes_args_and_kwargs(self):
        @stubborn(retries=1, delay=0)
        def add(a, b, c=0):
            return a + b + c

        assert add(1, 2, c=3) == 6

    def test_preserves_function_name_and_docstring(self):
        @stubborn(retries=1, delay=0)
        def my_func():
            """My docstring."""
            return True

        assert my_func.__name__ == "my_func"
        assert my_func.__doc__ == "My docstring."

    def test_only_retries_on_specified_exception(self):
        """If a non-matching exception is raised it should propagate immediately."""
        calls = {"n": 0}

        @stubborn(retries=5, delay=0, exceptions=(ValueError,))
        def fn():
            calls["n"] += 1
            raise TypeError("wrong type")

        with pytest.raises(TypeError):
            fn()

        # Should have been called only once — no retry on TypeError
        assert calls["n"] == 1

    def test_catches_specified_exception_subclass(self):
        """Subclasses of the specified exception should also be retried."""
        fn = make_flaky(fail_times=1, exc_type=FileNotFoundError)

        @stubborn(retries=2, delay=0, exceptions=(OSError,))
        def call():
            return fn()

        # FileNotFoundError is a subclass of OSError — should retry
        assert call() == "ok"

    def test_delay_is_respected(self):
        calls = {"n": 0}

        @stubborn(retries=1, delay=0.05)
        def fn():
            calls["n"] += 1
            if calls["n"] < 2:
                raise RuntimeError("retry me")
            return "done"

        start = time.monotonic()
        fn()
        elapsed = time.monotonic() - start
        assert elapsed >= 0.04  # allow a little clock slack

    def test_backoff_increases_delay(self):
        """With backoff=2 the second wait should be ~2x the first."""
        sleep_calls = []
        original_sleep = time.sleep

        import unittest.mock as mock

        with mock.patch("pocketknife.resilience.time.sleep", side_effect=lambda s: sleep_calls.append(s)):
            @stubborn(retries=2, delay=0.1, backoff=2.0)
            def fn():
                raise RuntimeError("x")

            with pytest.raises(RuntimeError):
                fn()

        assert len(sleep_calls) == 2
        assert sleep_calls[1] == pytest.approx(sleep_calls[0] * 2.0)

    # --- constructor validation ---

    def test_raises_on_negative_retries(self):
        with pytest.raises(TypeError):
            stubborn(retries=-1)

    def test_raises_on_non_int_retries(self):
        with pytest.raises(TypeError):
            stubborn(retries=2.5)

    def test_raises_on_negative_delay(self):
        with pytest.raises(TypeError):
            stubborn(delay=-0.1)

    def test_raises_on_backoff_less_than_one(self):
        with pytest.raises(TypeError):
            stubborn(backoff=0.5)

    def test_raises_on_empty_exceptions_tuple(self):
        with pytest.raises(TypeError):
            stubborn(exceptions=())

    def test_raises_on_non_tuple_exceptions(self):
        with pytest.raises(TypeError):
            stubborn(exceptions=ValueError)  # type: ignore


# ---------------------------------------------------------------------------
# fallback()
# ---------------------------------------------------------------------------

class TestFallback:

    def test_returns_fn_result_on_success(self):
        assert fallback(lambda: 42, default=0) == 42

    def test_returns_default_on_exception(self):
        assert fallback(lambda: int("nope"), default=-1) == -1

    def test_default_can_be_none(self):
        assert fallback(lambda: 1 / 0, default=None) is None

    def test_default_can_be_false(self):
        assert fallback(lambda: [][0], default=False) is False

    def test_default_can_be_zero(self):
        assert fallback(lambda: {}["missing"], default=0) == 0

    def test_default_can_be_empty_string(self):
        assert fallback(lambda: int("x"), default="") == ""

    def test_default_can_be_dict(self):
        result = fallback(lambda: 1 / 0, default={"status": "error"})
        assert result == {"status": "error"}

    def test_only_catches_specified_exceptions(self):
        """A non-matching exception should propagate even with a default set."""
        # int("x") raises ValueError; we only catch TypeError → ValueError propagates
        with pytest.raises(ValueError):
            fallback(
                lambda: int("x"),  # raises ValueError
                default=0,
                exceptions=(TypeError,),  # only catches TypeError, not ValueError
            )

    def test_catches_specified_exception(self):
        result = fallback(
            lambda: int("x"),
            default=0,
            exceptions=(ValueError,),
        )
        assert result == 0

    def test_fn_with_side_effects_runs(self):
        log = []
        fallback(lambda: log.append("ran") or 1, default=None)
        assert log == ["ran"]

    def test_raises_if_fn_not_callable(self):
        with pytest.raises(TypeError):
            fallback("not_a_function", default=0)  # type: ignore

    def test_raises_on_empty_exceptions_tuple(self):
        with pytest.raises(TypeError):
            fallback(lambda: 1, default=0, exceptions=())

    def test_raises_on_non_tuple_exceptions(self):
        with pytest.raises(TypeError):
            fallback(lambda: 1, default=0, exceptions=ValueError)  # type: ignore

    def test_fn_returning_none_is_not_treated_as_error(self):
        result = fallback(lambda: None, default="should-not-appear")
        assert result is None

    def test_fn_returning_false_is_not_treated_as_error(self):
        result = fallback(lambda: False, default="should-not-appear")
        assert result is False

    def test_fn_returning_zero_is_not_treated_as_error(self):
        result = fallback(lambda: 0, default=999)
        assert result == 0
