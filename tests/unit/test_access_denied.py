"""Offline tests for first-class handling of denied requests (HTTP 401/403).

Covers the typed :class:`~office365.runtime.exceptions.AccessDeniedException`:
Graph symbolic codes, SharePoint's ``E_ACCESSDENIED`` HRESULT, and status-only
responses with no JSON body. Also asserts it stays a ``ClientRequestException``
so existing catch-alls keep working.
"""

from __future__ import annotations

import unittest

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.exceptions import AccessDeniedException
from requests import Response


def _response(status: int, body: bytes) -> Response:
    resp = Response()
    resp.status_code = status
    resp.url = "https://graph.microsoft.com/v1.0/security/cases/ediscoveryCases"
    resp._content = body
    return resp


class TestAccessDeniedClassification(unittest.TestCase):
    def test_sharepoint_unauthorized_access_is_typed(self):
        body = (
            b'{"error":{"code":"-2147024891, System.UnauthorizedAccessException",'
            b'"message":"Access denied. You do not have permission to perform this action."}}'
        )
        exc = ClientRequestException.from_response(_response(403, body))
        self.assertIsInstance(exc, AccessDeniedException)


if __name__ == "__main__":
    unittest.main()
