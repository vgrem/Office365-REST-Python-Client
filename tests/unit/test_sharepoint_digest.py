"""Offline tests for SharePoint form-digest caching, refresh and recovery."""

from __future__ import annotations

import json
import unittest
from unittest import mock

from office365.runtime.http.request_options import RequestOptions
from office365.runtime.transport.base import BaseTransport
from office365.sharepoint.exceptions import SecurityValidationException
from office365.sharepoint.request import SharePointRequest
from office365.sharepoint.webs.context_web_information import ContextWebInformation
from requests import Response


def _json_response(request, payload: dict, status: int = 200, headers: dict | None = None) -> Response:
    resp = Response()
    resp.status_code = status
    resp.url = request.url
    resp.headers["Content-Type"] = "application/json;odata=verbose"
    resp.headers.update(headers or {})
    resp._content = json.dumps(payload).encode()
    return resp


def _digest_payload(value: str, timeout: int = 1800) -> dict:
    return {"d": {"GetContextWebInformation": {"FormDigestValue": value, "FormDigestTimeoutSeconds": timeout}}}


def _digest_expired_payload() -> dict:
    return {
        "error": {
            "code": "-2130575251, Microsoft.SharePoint.SPException",
            "message": "The security validation for this page is invalid and might be corrupted.",
        }
    }


class _DigestTransport(BaseTransport):
    """Routes ``/contextInfo`` and main requests, scripting each side."""

    def __init__(
        self,
        context_info_statuses: list[int] | None = None,
        main_responses: list[tuple[int, dict]] | None = None,
    ):
        super().__init__()
        self._context_info_statuses = list(context_info_statuses or [])
        self._main_responses = list(main_responses or [(200, {})])
        self.context_info_calls = 0
        self.main_calls = 0

    def execute(self, request):
        if "contextInfo" in request.url:
            self.context_info_calls += 1
            status = self._context_info_statuses.pop(0) if self._context_info_statuses else 200
            if status == 429:  # noqa: PLR2004
                return _json_response(request, _digest_expired_payload(), status=429, headers={"Retry-After": "0"})
            return _json_response(request, _digest_payload(f"digest-{self.context_info_calls}"))
        self.main_calls += 1
        index = min(self.main_calls - 1, len(self._main_responses) - 1)
        status, payload = self._main_responses[index]
        return _json_response(request, payload, status=status)


def _request(transport: BaseTransport) -> SharePointRequest:
    request = SharePointRequest("https://contoso.sharepoint.com")
    request._auth_context.authenticate_request = lambda _r: None  # no credentials needed offline
    request._transport = transport
    return request


class TestContextWebInformationValidity(unittest.TestCase):
    def test_invalid_without_digest(self):
        self.assertFalse(ContextWebInformation().is_valid)


class TestFormDigestFetch(unittest.TestCase):
    def test_context_info_fetch_retries_transient(self):
        transport = _DigestTransport(context_info_statuses=[429])
        request = _request(transport)

        with mock.patch("office365.runtime.retry.sleep"):
            info = request._fetch_context_web_information()

        self.assertEqual(transport.context_info_calls, 2)  # noqa: PLR2004 — 429 then success
        self.assertEqual(info.FormDigestValue, "digest-2")


class TestDigestExpiryRecovery(unittest.TestCase):
    def test_security_validation_error_is_dispatched(self):
        from office365.runtime.client_request_exception import ClientRequestException

        exc = ClientRequestException.from_response(
            _json_response(RequestOptions("https://x"), _digest_expired_payload(), status=403)
        )
        self.assertIsInstance(exc, SecurityValidationException)

        other = ClientRequestException.from_response(
            _json_response(RequestOptions("https://x"), {"error": {"code": "123", "message": "boom"}}, status=400)
        )
        self.assertNotIsInstance(other, SecurityValidationException)

    def test_expired_digest_refreshes_and_retries_once(self):
        transport = _DigestTransport(main_responses=[(403, _digest_expired_payload()), (200, {})])
        request = _request(transport)

        response = request.execute_request_direct(RequestOptions("https://contoso.sharepoint.com/_api/web/lists"))

        self.assertEqual(response.status_code, 200)  # noqa: PLR2004
        self.assertEqual(transport.main_calls, 2)  # noqa: PLR2004 — failed then retried
        self.assertEqual(transport.context_info_calls, 2)  # noqa: PLR2004 — initial + refresh

    def test_non_digest_403_is_not_retried(self):
        from office365.runtime.client_request_exception import ClientRequestException

        transport = _DigestTransport(main_responses=[(403, {"error": {"code": "accessDenied", "message": "no"}})])
        request = _request(transport)

        with self.assertRaises(ClientRequestException):
            request.execute_request_direct(RequestOptions("https://contoso.sharepoint.com/_api/web/lists"))
        self.assertEqual(transport.main_calls, 1)
