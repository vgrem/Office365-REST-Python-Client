"""Offline tests for the response-byte normalizers.

``ClientResult.to_bytes`` and ``Report.to_bytes`` back the report-download
examples, which previously inlined ``isinstance(value, bytes)`` checks.
"""

from __future__ import annotations

import pytest
from office365.reports.report import Report
from office365.runtime.client_result import ClientResult


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (b"abc", b"abc"),
        (bytearray(b"abc"), b"abc"),
        ("abc", b"abc"),
        (Report(content=b"csv,bytes"), b"csv,bytes"),
    ],
)
def test_client_result_to_bytes_normalises_content(value, expected):
    assert ClientResult(None, value).to_bytes() == expected


def test_client_result_to_bytes_from_object_with_str_content():
    class _Wrapper:
        content = "text"

    assert ClientResult(None, _Wrapper()).to_bytes() == b"text"


def test_to_bytes_when_empty_and_for_a_report():
    assert ClientResult(None).to_bytes() == b""
    assert ClientResult(None, Report()).to_bytes() == b""
    assert Report().to_bytes() == b""
    assert Report(content=b"x").to_bytes() == b"x"


def test_set_property_raw_value_fills_report_content():
    result = ClientResult(None, Report())
    result.set_property("__value", b"csv,bytes")
    assert isinstance(result.value, Report)
    assert result.value.content == b"csv,bytes"
    assert result.to_bytes() == b"csv,bytes"


def test_set_property_raw_value_replaces_plain_defaults():
    assert ClientResult(None, b"").set_property("__value", b"payload").value == b"payload"
    sentinel = 42
    assert ClientResult(None).set_property("__value", sentinel).value == sentinel
