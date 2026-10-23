"""Offline tests for the response-byte normalizers.

``ClientResult.to_bytes`` and ``Report.to_bytes`` back the report-download
examples, which previously inlined ``isinstance(value, bytes)`` checks.
"""

from __future__ import annotations

from office365.runtime.client_result import ClientResult


def test_client_result_to_bytes_from_object_with_str_content():
    class _Wrapper:
        content = "text"

    assert ClientResult(None, _Wrapper()).to_bytes() == b"text"


def test_set_property_raw_value_replaces_plain_defaults():
    assert ClientResult(None, b"").set_property("__value", b"payload").value == b"payload"
    sentinel = 42
    assert ClientResult(None).set_property("__value", sentinel).value == sentinel
