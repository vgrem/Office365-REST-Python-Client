"""Offline tests for the report result CSV helper.

``ReportResult.csv_rows`` backs the reports examples, which previously inlined
the same BOM-tolerant ``csv.DictReader`` block ten times."""

import io
from typing import Any

import pytest
from office365.graph_client import GraphClient
from office365.reports.report_export import (
    download_report,
)
from office365.reports.report_result import ReportResult
from office365.runtime.client_request_exception import ClientRequestException
from tests._scripted_transport import ScriptedTransport

# The usage reports arrive as UTF-8 with a BOM on the first header.
_CSV_BOM = b"\xef\xbb\xbfReport Date,Send,Read\r\n2024-01-01,5,3\r\n2024-01-02,7,4\r\n"


def _result(content: bytes = _CSV_BOM) -> ReportResult:
    # The report methods return ReportResult; the runtime fills the Report
    # content from the raw CSV response body via the "__value" key.
    return ReportResult(None).set_property("__value", content)


def test_report_result_csv_rows_are_keyed_by_header():
    assert _result().csv_rows() == [
        {"Report Date": "2024-01-01", "Send": "5", "Read": "3"},
        {"Report Date": "2024-01-02", "Send": "7", "Read": "4"},
    ]


_CSV = b"UserPrincipalName,Count\nalice@contoso.com,3\nbob@contoso.com,1\n"


def _graph_client(payloads: list[Any]) -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = ScriptedTransport(list(payloads))
    return client


def _report(http_status: int = 200, body: Any = None, headers: dict[str, str] | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"http_status": http_status}
    if body is not None:
        payload["body"] = body
    if headers is not None:
        payload["headers"] = headers
    return payload


def test_download_report_raises_on_error():
    client = _graph_client([_report(403, {"error": {"code": "Forbidden"}})])
    with pytest.raises(ClientRequestException):
        download_report(client.reports, "getX", io.BytesIO())
