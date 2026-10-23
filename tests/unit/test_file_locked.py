"""Offline tests for first-class handling of locked files (HTTP 423).

Covers the typed :class:`~office365.runtime.exceptions.FileLockedException`
(classification, lock-owner parsing), opt-in retry via ``retry_on`` and the
``bypass_shared_lock`` delete option on both Graph and SharePoint entities.
"""

from __future__ import annotations

import unittest
from unittest import mock

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.exceptions import FileLockedException
from office365.runtime.transport.base import BaseTransport
from office365.sharepoint.client_context import ClientContext
from requests import Response

SHAREPOINT_LOCK_BODY = (
    b'{"error":{"code":"-2147018894, Microsoft.SharePoint.SPFileLockException",'
    b'"message":"The file https://contoso.sharepoint.com/sites/team/Shared Documents/report.xlsx '
    b'is locked for shared use by John Doe [membership]."}}'
)


def _locked_response(status: int = 423, body: bytes = SHAREPOINT_LOCK_BODY) -> Response:
    resp = Response()
    resp.status_code = status
    resp.url = "https://contoso.sharepoint.com/_api/web"
    resp._content = body
    return resp


class _CaptureTransport(BaseTransport):
    """Records the last request so tests can assert on its headers."""

    def __init__(self) -> None:
        super().__init__()
        self.request = None

    def execute(self, request):
        self.request = request
        resp = Response()
        resp.status_code = 200
        resp.url = request.url
        resp.headers["Content-Type"] = "application/json;odata=verbose"
        resp._content = b"{}"
        return resp


class TestFileLockedClassification(unittest.TestCase):
    def test_str_includes_owner_and_guidance(self):
        exc = ClientRequestException.from_response(_locked_response())
        text = str(exc)
        self.assertIn("John Doe", text)
        self.assertIn("shared lock", text)


class TestFileLockedRetry(unittest.TestCase):
    def _context(self, outcomes):
        ctx = ClientContext("https://contoso.sharepoint.com")
        execute_query = mock.Mock(side_effect=outcomes)
        ctx.execute_query = execute_query  # type: ignore[method-assign]
        return ctx, execute_query

    def test_locked_is_not_retried_by_default(self):
        ctx, execute_query = self._context([ClientRequestException.from_response(_locked_response())])

        with mock.patch("office365.runtime.retry.sleep"):
            with self.assertRaises(FileLockedException):
                ctx.execute_query_retry(max_retry=3, timeout_secs=1)

        self.assertEqual(execute_query.call_count, 1)


class TestBypassSharedLockHeader(unittest.TestCase):
    def test_sharepoint_delete_sends_prefer_header(self):
        ctx = ClientContext("https://contoso.sharepoint.com")
        transport = _CaptureTransport()
        ctx.pending_request().beforeExecute.clear()
        ctx.pending_request().transport = transport

        file = ctx.web.get_file_by_server_relative_url("/sites/team/Shared Documents/report.xlsx")
        file.delete_object(bypass_shared_lock=True).execute_query()

        assert transport.request is not None
        self.assertEqual(transport.request.headers.get("Prefer"), "bypass-shared-lock")

    def test_graph_delete_sends_prefer_header(self):
        client = GraphClient()
        transport = _CaptureTransport()
        client.pending_request().beforeExecute.clear()
        client.pending_request().transport = transport

        client.drives["d"].items["i"].delete_object(bypass_shared_lock=True).execute_query()

        assert transport.request is not None
        self.assertEqual(transport.request.headers.get("Prefer"), "bypass-shared-lock")


if __name__ == "__main__":
    unittest.main()
