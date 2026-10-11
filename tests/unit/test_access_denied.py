"""Offline tests for first-class handling of denied requests (HTTP 401/403).

Covers the typed :class:`~office365.runtime.exceptions.AccessDeniedException`:
Graph symbolic codes, SharePoint's ``E_ACCESSDENIED`` HRESULT, and status-only
responses with no JSON body. Also asserts it stays a ``ClientRequestException``
so existing catch-alls keep working.
"""

from __future__ import annotations

import unittest

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.exceptions import AccessDeniedException, FileLockedException, ObjectNotFoundException
from requests import Response


def _response(status: int, body: bytes) -> Response:
    resp = Response()
    resp.status_code = status
    resp.url = "https://graph.microsoft.com/v1.0/security/cases/ediscoveryCases"
    resp._content = body
    return resp


def _graph_error(status: int, code: str) -> Response:
    body = ('{"error":{"code":"%s","message":"Access denied."}}' % code).encode()
    return _response(status, body)


class TestAccessDeniedClassification(unittest.TestCase):
    def test_graph_access_denied_is_typed(self):
        exc = ClientRequestException.from_response(_graph_error(403, "accessDenied"))
        self.assertIsInstance(exc, AccessDeniedException)

    def test_graph_authorization_request_denied_is_typed(self):
        exc = ClientRequestException.from_response(_graph_error(403, "Authorization_RequestDenied"))
        self.assertIsInstance(exc, AccessDeniedException)

    def test_graph_error_access_denied_is_typed(self):
        exc = ClientRequestException.from_response(_graph_error(403, "ErrorAccessDenied"))
        self.assertIsInstance(exc, AccessDeniedException)

    def test_sharepoint_unauthorized_access_is_typed(self):
        body = (
            b'{"error":{"code":"-2147024891, System.UnauthorizedAccessException",'
            b'"message":"Access denied. You do not have permission to perform this action."}}'
        )
        exc = ClientRequestException.from_response(_response(403, body))
        self.assertIsInstance(exc, AccessDeniedException)

    def test_status_only_401_is_typed(self):
        exc = ClientRequestException.from_response(_response(401, b""))
        self.assertIsInstance(exc, AccessDeniedException)

    def test_status_only_403_is_typed(self):
        exc = ClientRequestException.from_response(_response(403, b""))
        self.assertIsInstance(exc, AccessDeniedException)

    def test_is_still_a_client_request_exception(self):
        exc = ClientRequestException.from_response(_graph_error(403, "accessDenied"))
        self.assertIsInstance(exc, ClientRequestException)

    def test_not_found_is_not_access_denied(self):
        exc = ClientRequestException.from_response(_graph_error(404, "itemNotFound"))
        self.assertIsInstance(exc, ObjectNotFoundException)
        self.assertNotIsInstance(exc, AccessDeniedException)

    def test_locked_is_not_access_denied(self):
        exc = ClientRequestException.from_response(_response(423, b'{"error":{"code":"resourceLocked"}}'))
        self.assertIsInstance(exc, FileLockedException)
        self.assertNotIsInstance(exc, AccessDeniedException)

    def test_bad_request_is_not_access_denied(self):
        exc = ClientRequestException.from_response(
            _response(400, b'{"error":{"code":"invalidRequest","message":"boom"}}')
        )
        self.assertNotIsInstance(exc, AccessDeniedException)


if __name__ == "__main__":
    unittest.main()
