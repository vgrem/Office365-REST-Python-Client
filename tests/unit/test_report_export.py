"""Offline tests for streamed report export.

Covers :mod:`office365.reports.report_export` (``download_report`` /
``download_report_async``) and the thin :class:`~office365.reports.root.ReportRoot`
wrappers: the CSV body is streamed chunk-by-chunk into a path or binary stream,
the server's ``Content-Disposition`` file name is surfaced, and errors are
converted to :class:`ClientRequestException`.
"""

from __future__ import annotations

import asyncio
import io
from typing import Any

import pytest
from office365.graph_client import GraphClient
from office365.reports.report_export import (
    download_report,
    download_report_async,
)
from office365.runtime.client_request_exception import ClientRequestException
from tests._scripted_transport import ScriptedTransport

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


def _download_payload(body: bytes = _CSV, filename: str = "report.csv") -> dict[str, Any]:
    return _report(
        200,
        body,
        {
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(body)),
        },
    )


def test_download_report_reports_progress():
    client = _graph_client([_download_payload()])
    seen = []
    download_report(client.reports, "getX", io.BytesIO(), progress=seen.append)
    assert seen
    assert seen[-1].done == len(_CSV)
    assert seen[-1].total == len(_CSV)
    assert seen[-1].stage == "downloading"


def test_download_report_raises_on_error():
    client = _graph_client([_report(403, {"error": {"code": "Forbidden"}})])
    with pytest.raises(ClientRequestException):
        download_report(client.reports, "getX", io.BytesIO())


def test_download_report_async(tmp_path):
    csv = b"async csv\n"
    client = _graph_client([_download_payload(csv, "async.csv")])
    target = tmp_path / "async.csv"
    result = asyncio.run(download_report_async(client.reports, "getX", target, period="D30"))
    assert result.bytes_written == len(csv)
    assert result.file_name == "async.csv"
    assert target.read_bytes() == csv


def test_report_root_methods_delegate(tmp_path):
    client = _graph_client([_download_payload()])
    target = tmp_path / "root.csv"
    result = client.reports.download_report("getX", target)
    assert result.bytes_written == len(_CSV)
    assert target.read_bytes() == _CSV
