"""
tests/test_overengineer.py
~~~~~~~~~~~~~~~~~~~~~~~~~~
Unit tests for pocketknife.overengineer.
"""

import io
import sys
import unittest

from pocketknife.overengineer import (
    _arg_elements,
    _xml_escape,
    enterprise_edition,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _capture_stream():
    """Return a StringIO that can be passed as the log stream."""
    return io.StringIO()


# ---------------------------------------------------------------------------
# _xml_escape
# ---------------------------------------------------------------------------

class TestXmlEscape(unittest.TestCase):

    def test_ampersand(self):
        self.assertEqual(_xml_escape("a & b"), "a &amp; b")

    def test_less_than(self):
        self.assertEqual(_xml_escape("a < b"), "a &lt; b")

    def test_greater_than(self):
        self.assertEqual(_xml_escape("a > b"), "a &gt; b")

    def test_double_quote(self):
        self.assertEqual(_xml_escape('"hello"'), "&quot;hello&quot;")

    def test_single_quote(self):
        self.assertEqual(_xml_escape("it's"), "it&apos;s")

    def test_plain_string_unchanged(self):
        self.assertEqual(_xml_escape("hello world"), "hello world")

    def test_combined(self):
        result = _xml_escape('<a href="foo&bar">it\'s</a>')
        self.assertNotIn("<", result)
        self.assertNotIn(">", result)
        self.assertNotIn('"', result)
        self.assertNotIn("'", result)
        self.assertNotIn("&b", result)  # raw & gone


# ---------------------------------------------------------------------------
# _arg_elements
# ---------------------------------------------------------------------------

class TestArgElements(unittest.TestCase):

    def test_no_args_returns_empty_element(self):
        result = _arg_elements((), {})
        self.assertEqual(result.strip(), "<parameter />")

    def test_positional_arg_rendered(self):
        result = _arg_elements((42,), {})
        self.assertIn('strategy="POSITIONAL"', result)
        self.assertIn("42", result)

    def test_keyword_arg_rendered(self):
        result = _arg_elements((), {"key": "val"})
        self.assertIn('strategy="KEYWORD"', result)
        self.assertIn("key", result)
        self.assertIn("val", result)

    def test_type_attribute_correct(self):
        result = _arg_elements((3.14,), {})
        self.assertIn('type="float"', result)

    def test_multiple_positional_args_indexed(self):
        result = _arg_elements((1, 2, 3), {})
        self.assertIn('index="0"', result)
        self.assertIn('index="1"', result)
        self.assertIn('index="2"', result)

    def test_special_chars_in_kwarg_value_escaped(self):
        result = _arg_elements((), {"x": "<danger>"})
        self.assertNotIn("<danger>", result)
        self.assertIn("&lt;danger&gt;", result)


# ---------------------------------------------------------------------------
# @enterprise_edition — basic decoration
# ---------------------------------------------------------------------------

class TestEnterpriseEditionBasic(unittest.TestCase):

    def test_return_value_unchanged(self):
        """The decorated function must return the same value as the original."""
        stream = _capture_stream()

        @enterprise_edition(stream=stream)
        def add(a, b):
            return a + b

        self.assertEqual(add(1, 2), 3)

    def test_bare_decorator_no_parens(self):
        """@enterprise_edition without parentheses should work."""
        stream = _capture_stream()

        @enterprise_edition
        def double(x):
            return x * 2

        # Redirect the default stderr output during the call
        old_stderr = sys.stderr
        sys.stderr = stream
        try:
            result = double(5)
        finally:
            sys.stderr = old_stderr

        self.assertEqual(result, 10)

    def test_functools_wraps_preserves_name(self):
        """__name__ and __doc__ of the original function are preserved."""
        stream = _capture_stream()

        @enterprise_edition(stream=stream)
        def my_func():
            """My docstring."""
            pass

        self.assertEqual(my_func.__name__, "my_func")
        self.assertEqual(my_func.__doc__, "My docstring.")

    def test_exception_is_reraised(self):
        """Exceptions from the wrapped function must propagate unchanged."""
        stream = _capture_stream()

        @enterprise_edition(stream=stream)
        def boom():
            raise ValueError("kaboom")

        with self.assertRaises(ValueError, msg="kaboom"):
            boom()

    def test_none_return_value(self):
        """Functions returning None should work without error."""
        stream = _capture_stream()

        @enterprise_edition(stream=stream)
        def nothing():
            return None

        self.assertIsNone(nothing())

    def test_kwargs_passed_correctly(self):
        """Keyword arguments are forwarded to the original function."""
        stream = _capture_stream()

        @enterprise_edition(stream=stream)
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        self.assertEqual(greet("World", greeting="Hi"), "Hi, World!")

    def test_custom_namespace_in_output(self):
        """The custom namespace string should appear in the XML output."""
        stream = _capture_stream()
        ns = "com.test.custom.namespace"

        @enterprise_edition(namespace=ns, stream=stream)
        def noop():
            pass

        noop()
        self.assertIn(ns, stream.getvalue())

    def test_custom_log_level_in_output(self):
        """The custom log_level string should appear in the XML output."""
        stream = _capture_stream()

        @enterprise_edition(log_level="TRACE", stream=stream)
        def noop():
            pass

        noop()
        self.assertIn("TRACE", stream.getvalue())


# ---------------------------------------------------------------------------
# XML structure of emitted logs
# ---------------------------------------------------------------------------

class TestEnterpriseEditionXmlOutput(unittest.TestCase):

    def _decorated_add(self):
        stream = _capture_stream()

        @enterprise_edition(stream=stream)
        def add(a, b):
            return a + b

        add(3, 4)
        return stream.getvalue()

    def test_xml_declaration_present(self):
        output = self._decorated_add()
        self.assertIn('<?xml version="1.0"', output)

    def test_invocation_manifest_root_element(self):
        output = self._decorated_add()
        self.assertIn("enterpriseExecutionManifest", output)

    def test_execution_report_root_element(self):
        output = self._decorated_add()
        self.assertIn("enterpriseExecutionReport", output)

    def test_correlation_id_present(self):
        output = self._decorated_add()
        self.assertIn("correlationId=", output)

    def test_function_name_in_output(self):
        output = self._decorated_add()
        self.assertIn("add", output)

    def test_return_value_in_report(self):
        output = self._decorated_add()
        # Result of add(3, 4) is 7
        self.assertIn("7", output)

    def test_success_status_in_report(self):
        output = self._decorated_add()
        self.assertIn("SUCCESS", output)

    def test_lifecycle_state_complete(self):
        output = self._decorated_add()
        self.assertIn("EXECUTION_COMPLETE", output)

    def test_two_xml_documents_emitted_on_success(self):
        """On success, two XML documents should be emitted (manifest + report)."""
        output = self._decorated_add()
        self.assertEqual(output.count('<?xml version="1.0"'), 2)

    def test_parameter_count_attribute(self):
        stream = _capture_stream()

        @enterprise_edition(stream=stream)
        def three_args(a, b, c):
            pass

        three_args(1, 2, 3)
        self.assertIn('totalCount="3"', stream.getvalue())


# ---------------------------------------------------------------------------
# Exception path
# ---------------------------------------------------------------------------

class TestEnterpriseEditionExceptionPath(unittest.TestCase):

    def _output_from_failing_call(self):
        stream = _capture_stream()

        @enterprise_edition(stream=stream)
        def fail():
            raise RuntimeError("it broke")

        try:
            fail()
        except RuntimeError:
            pass
        return stream.getvalue()

    def test_exception_report_root_element(self):
        output = self._output_from_failing_call()
        self.assertIn("enterpriseExceptionReport", output)

    def test_catastrophic_failure_status(self):
        output = self._output_from_failing_call()
        self.assertIn("CATASTROPHIC_FAILURE", output)

    def test_exception_class_in_report(self):
        output = self._output_from_failing_call()
        self.assertIn("RuntimeError", output)

    def test_exception_message_in_report(self):
        output = self._output_from_failing_call()
        self.assertIn("it broke", output)

    def test_two_xml_documents_emitted_on_exception(self):
        """On exception: manifest + exception report = 2 docs."""
        output = self._output_from_failing_call()
        self.assertEqual(output.count('<?xml version="1.0"'), 2)

    def test_lifecycle_state_exception_propagation(self):
        output = self._output_from_failing_call()
        self.assertIn("EXCEPTION_PROPAGATION_INITIATED", output)

    def test_original_exception_type_preserved(self):
        """The exact exception type must be re-raised, not wrapped."""
        stream = _capture_stream()

        @enterprise_edition(stream=stream)
        def typed_fail():
            raise TypeError("wrong type")

        with self.assertRaises(TypeError):
            typed_fail()

    def test_escalation_required_true(self):
        output = self._output_from_failing_call()
        self.assertIn("<escalationRequired>true</escalationRequired>", output)


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEnterpriseEditionEdgeCases(unittest.TestCase):

    def test_no_args_no_kwargs(self):
        """Zero-argument functions should not error."""
        stream = _capture_stream()

        @enterprise_edition(stream=stream)
        def noop():
            return "ok"

        self.assertEqual(noop(), "ok")

    def test_large_number_of_args(self):
        """Functions with many arguments should be handled gracefully."""
        stream = _capture_stream()

        @enterprise_edition(stream=stream)
        def many(*args):
            return sum(args)

        result = many(*range(100))
        self.assertEqual(result, sum(range(100)))

    def test_string_with_xml_chars_in_args(self):
        """XML-special characters in arguments must not break output XML."""
        stream = _capture_stream()

        @enterprise_edition(stream=stream)
        def identity(x):
            return x

        identity("<script>alert('xss')</script>")
        output = stream.getvalue()
        # Raw dangerous string must not appear unescaped
        self.assertNotIn("<script>", output)

    def test_each_call_gets_unique_correlation_id(self):
        """Every invocation should produce a unique correlationId."""
        stream = _capture_stream()

        @enterprise_edition(stream=stream)
        def noop():
            pass

        noop()
        noop()
        output = stream.getvalue()
        ids = [
            line.split('correlationId="')[1].split('"')[0]
            for line in output.splitlines()
            if 'correlationId="' in line
        ]
        # Each call emits 2 docs each with a correlationId; pairs should match
        # but pair 1 != pair 2
        self.assertEqual(ids[0], ids[1])   # manifest & report share same ID
        self.assertEqual(ids[2], ids[3])   # second call's pair
        self.assertNotEqual(ids[0], ids[2])  # different calls → different IDs

    def test_sla_compliant_for_fast_function(self):
        """Fast functions should be marked COMPLIANT."""
        stream = _capture_stream()

        @enterprise_edition(stream=stream)
        def fast():
            return 42

        fast()
        self.assertIn("COMPLIANT", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
