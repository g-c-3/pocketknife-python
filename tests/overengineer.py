"""
pocketknife.overengineer
~~~~~~~~~~~~~~~~~~~~~~~~
Because every function deserves enterprise-grade ceremony.

The ``@enterprise_edition`` decorator transforms any humble Python callable
into a fully-compliant, XML-logged, namespace-qualified, SOA-ready
Business Logic Execution Unit (BLEU).

Usage
-----
    from pocketknife.overengineer import enterprise_edition

    @enterprise_edition
    def add(a, b):
        return a + b

    result = add(1, 2)
    # Prints a verbose XML execution manifest to stderr, then returns 3.

Customisation
-------------
    @enterprise_edition(namespace="com.megacorp.maths", log_level="VERBOSE")
    def multiply(a, b):
        return a * b
"""

import functools
import inspect
import sys
import traceback
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Optional


# ---------------------------------------------------------------------------
# XML generation helpers  (stdlib only — no xml.etree needed for this output)
# ---------------------------------------------------------------------------

def _ts() -> str:
    """Return an ISO-8601 timestamp with timezone, fit for an enterprise log."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _xml_escape(value: str) -> str:
    """Minimally escape a string for safe embedding in XML character data."""
    return (
        value
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _indent(text: str, spaces: int) -> str:
    pad = " " * spaces
    return "\n".join(pad + line if line.strip() else line for line in text.splitlines())


def _arg_elements(args: tuple, kwargs: dict) -> str:
    """Render positional and keyword arguments as XML parameter elements."""
    parts = []
    for i, v in enumerate(args):
        t = type(v).__name__
        escaped = _xml_escape(repr(v))
        parts.append(
            f'<parameter index="{i}" type="{t}" strategy="POSITIONAL">'
            f"{escaped}</parameter>"
        )
    for k, v in kwargs.items():
        t = type(v).__name__
        escaped = _xml_escape(repr(v))
        parts.append(
            f'<parameter name="{_xml_escape(k)}" type="{t}" strategy="KEYWORD">'
            f"{escaped}</parameter>"
        )
    return "\n".join(parts) if parts else "<parameter />"


def _invocation_manifest(
    *,
    correlation_id: str,
    namespace: str,
    func_name: str,
    qualified_name: str,
    module: str,
    args: tuple,
    kwargs: dict,
    log_level: str,
    timestamp: str,
) -> str:
    arg_block = _indent(_arg_elements(args, kwargs), 8)
    return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<enterpriseExecutionManifest
    xmlns="{namespace}"
    correlationId="{correlation_id}"
    schemaVersion="4.2.1"
    logLevel="{log_level}">

  <invocationContext>
    <timestamp>{timestamp}</timestamp>
    <businessLogicUnitName>{_xml_escape(func_name)}</businessLogicUnitName>
    <qualifiedName>{_xml_escape(qualified_name)}</qualifiedName>
    <deploymentModule>{_xml_escape(module)}</deploymentModule>
    <executionEnvironment>PythonRuntimeAdapter/3.x</executionEnvironment>
    <threadSafetyGuarantee>UNVERIFIED</threadSafetyGuarantee>
    <complianceFramework>SOA-2000/REST-B2B/TOGAF-Phase-C</complianceFramework>
  </invocationContext>

  <parameterManifest totalCount="{len(args) + len(kwargs)}">
{arg_block}
  </parameterManifest>

  <lifecycleState>INVOCATION_INITIATED</lifecycleState>

</enterpriseExecutionManifest>"""


def _execution_report(
    *,
    correlation_id: str,
    namespace: str,
    func_name: str,
    result: Any,
    elapsed_ms: float,
    log_level: str,
    timestamp: str,
) -> str:
    result_type = type(result).__name__
    result_repr = _xml_escape(repr(result))
    return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<enterpriseExecutionReport
    xmlns="{namespace}"
    correlationId="{correlation_id}"
    schemaVersion="4.2.1"
    logLevel="{log_level}">

  <executionOutcome status="SUCCESS">
    <timestamp>{timestamp}</timestamp>
    <businessLogicUnitName>{_xml_escape(func_name)}</businessLogicUnitName>
    <elapsedMilliseconds>{elapsed_ms:.4f}</elapsedMilliseconds>
    <slaStatus>{"COMPLIANT" if elapsed_ms < 5000 else "BREACH_DETECTED"}</slaStatus>
  </executionOutcome>

  <returnValueDescriptor>
    <type>{result_type}</type>
    <value>{result_repr}</value>
    <nullabilityAssessment>{"NULLABLE_CONCERN" if result is None else "NON_NULL"}</nullabilityAssessment>
    <serializationStrategy>REPR_BASED</serializationStrategy>
  </returnValueDescriptor>

  <lifecycleState>EXECUTION_COMPLETE</lifecycleState>

</enterpriseExecutionReport>"""


def _exception_report(
    *,
    correlation_id: str,
    namespace: str,
    func_name: str,
    exc: BaseException,
    elapsed_ms: float,
    log_level: str,
    timestamp: str,
) -> str:
    tb_str = _xml_escape("".join(traceback.format_exception(type(exc), exc, exc.__traceback__)))
    exc_type = type(exc).__name__
    exc_module = type(exc).__module__
    return f"""\
<?xml version="1.0" encoding="UTF-8"?>
<enterpriseExceptionReport
    xmlns="{namespace}"
    correlationId="{correlation_id}"
    schemaVersion="4.2.1"
    logLevel="{log_level}">

  <executionOutcome status="CATASTROPHIC_FAILURE">
    <timestamp>{timestamp}</timestamp>
    <businessLogicUnitName>{_xml_escape(func_name)}</businessLogicUnitName>
    <elapsedMilliseconds>{elapsed_ms:.4f}</elapsedMilliseconds>
    <incidentSeverity>CRITICAL</incidentSeverity>
    <escalationRequired>true</escalationRequired>
  </executionOutcome>

  <exceptionDescriptor>
    <exceptionClass>{exc_module}.{exc_type}</exceptionClass>
    <message>{_xml_escape(str(exc))}</message>
    <rootCauseAnalysis>PENDING_ARCHITECT_REVIEW</rootCauseAnalysis>
    <remediationStrategy>RAISE_JIRA_TICKET</remediationStrategy>
  </exceptionDescriptor>

  <stackTraceManifest>
    <![CDATA[
{tb_str}    ]]>
  </stackTraceManifest>

  <lifecycleState>EXCEPTION_PROPAGATION_INITIATED</lifecycleState>

</enterpriseExceptionReport>"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_SENTINEL = object()


def enterprise_edition(
    func: Optional[Callable] = None,
    *,
    namespace: str = "com.enterprise.pocketknife.bleu",
    log_level: str = "VERBOSE",
    stream=None,
):
    """Decorator that wraps a function with verbose Java-style XML execution logs.

    Can be used with or without arguments:

        @enterprise_edition
        def my_func(): ...

        @enterprise_edition(namespace="com.acme.core", log_level="DEBUG")
        def my_func(): ...

    Parameters
    ----------
    func : callable, optional
        The function to decorate (supplied automatically when used without
        parentheses).
    namespace : str
        XML namespace URI embedded in every document
        (default ``"com.enterprise.pocketknife.bleu"``).
    log_level : str
        Freeform log level string stamped on every XML document
        (default ``"VERBOSE"``).
    stream :
        Where to write the XML output. Defaults to ``sys.stderr``.

    Returns
    -------
    callable
        The wrapped function.  Return value and exceptions are passed through
        unchanged; the decorator only adds logging side-effects.

    Example
    -------
    >>> from pocketknife.overengineer import enterprise_edition
    >>> @enterprise_edition
    ... def greet(name):
    ...     return f"Hello, {name}!"
    >>> greet("World")          # doctest: +SKIP
    'Hello, World!'
    """
    _stream = stream  # capture for closure; resolved lazily if None

    def _decorator(fn: Callable) -> Callable:
        fn_name = fn.__name__
        qualified = fn.__qualname__
        module = fn.__module__ or "<unknown>"

        @functools.wraps(fn)
        def _wrapper(*args, **kwargs):
            out = _stream if _stream is not None else sys.stderr
            correlation_id = str(uuid.uuid4()).upper()
            t_start = datetime.now(timezone.utc)

            # --- PRE-INVOCATION MANIFEST ---
            manifest = _invocation_manifest(
                correlation_id=correlation_id,
                namespace=namespace,
                func_name=fn_name,
                qualified_name=qualified,
                module=module,
                args=args,
                kwargs=kwargs,
                log_level=log_level,
                timestamp=t_start.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z",
            )
            out.write(manifest + "\n\n")
            out.flush()

            # --- EXECUTE ---
            import time as _time
            t0 = _time.monotonic()
            try:
                result = fn(*args, **kwargs)
                elapsed_ms = (_time.monotonic() - t0) * 1000

                # --- SUCCESS REPORT ---
                report = _execution_report(
                    correlation_id=correlation_id,
                    namespace=namespace,
                    func_name=fn_name,
                    result=result,
                    elapsed_ms=elapsed_ms,
                    log_level=log_level,
                    timestamp=_ts(),
                )
                out.write(report + "\n\n")
                out.flush()
                return result

            except Exception as exc:
                elapsed_ms = (_time.monotonic() - t0) * 1000

                # --- EXCEPTION REPORT ---
                exc_doc = _exception_report(
                    correlation_id=correlation_id,
                    namespace=namespace,
                    func_name=fn_name,
                    exc=exc,
                    elapsed_ms=elapsed_ms,
                    log_level=log_level,
                    timestamp=_ts(),
                )
                out.write(exc_doc + "\n\n")
                out.flush()
                raise  # re-raise unchanged

        return _wrapper

    # Support both @enterprise_edition and @enterprise_edition(...)
    if func is not None:
        # Called as @enterprise_edition with no parens — func is the decorated fn
        return _decorator(func)
    # Called as @enterprise_edition(...) — return the decorator
    return _decorator


# ---------------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import io

    print("=== pocketknife.overengineer demo ===\n")
    print("All XML logs will appear below.\n")
    print("-" * 60)

    # --- bare decorator ---
    @enterprise_edition
    def add(a, b):
        """Add two numbers together."""
        return a + b

    result = add(1, 2)
    print(f"\n>>> add(1, 2) returned: {result}\n")
    print("-" * 60)

    # --- decorator with custom namespace ---
    @enterprise_edition(namespace="com.megacorp.finance.v2", log_level="DEBUG")
    def divide(numerator, denominator):
        if denominator == 0:
            raise ZeroDivisionError("Cannot divide by zero — have you tried dividing by a non-zero number?")
        return numerator / denominator

    print()
    result2 = divide(10, 4)
    print(f"\n>>> divide(10, 4) returned: {result2}\n")
    print("-" * 60)

    # --- exception path ---
    print("\nNow triggering a CATASTROPHIC_FAILURE...\n")
    try:
        divide(10, 0)
    except ZeroDivisionError:
        print("\n>>> ZeroDivisionError was re-raised and caught by demo harness.\n")

    print("-" * 60)
    print("\nEnterprise logging complete. Please file a change request to read the output.")
