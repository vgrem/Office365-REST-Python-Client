"""Offline tests for the report result CSV helper.

``ReportResult.csv_rows`` backs the reports examples, which previously inlined
the same BOM-tolerant ``csv.DictReader`` block ten times.
"""

from __future__ import annotations

from office365.reports.report_result import ReportResult

# The usage reports arrive as UTF-8 with a BOM on the first header.
_CSV_BOM = b"\xef\xbb\xbfReport Date,Send,Read\r\n2024-01-01,5,3\r\n2024-01-02,7,4\r\n"


def _result(content: bytes = _CSV_BOM) -> ReportResult:
    # The report methods return ReportResult; the runtime fills the Report
    # content from the raw CSV response body via the "__value" key.
    return ReportResult(None).set_property("__value", content)


def test_report_result_to_text_strips_bom():
    assert _result().to_text().startswith("Report Date")


def test_report_result_csv_rows_are_keyed_by_header():
    assert _result().csv_rows() == [
        {"Report Date": "2024-01-01", "Send": "5", "Read": "3"},
        {"Report Date": "2024-01-02", "Send": "7", "Read": "4"},
    ]


def test_report_result_csv_rows_via_to_bytes_roundtrip():
    assert _result().csv_rows()[1]["Read"] == "4"
