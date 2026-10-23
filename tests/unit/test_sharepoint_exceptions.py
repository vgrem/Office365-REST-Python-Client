"""Offline tests for locale-independent SharePoint exception classification.

SharePoint encodes errors as ``"<HRESULT>, <dotnet-type>"`` in ``error.code``;
these tests pin that classification keys off the code / embedded type name (never
translated messages) and that the priority dispatcher resolves the overlapping
HTTP 423 cases (shared coauthoring lock vs. check-out).
"""

from __future__ import annotations

import json
import unittest

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.exceptions import DuplicatedObjectException, FileLockedException
from office365.sharepoint.exceptions import (
    SharePointException,
    SPFileCheckOutException,
    SPListDataValidationException,
)
from requests import Response


def _error_response(code: str, message: str = "", status: int = 400) -> Response:
    resp = Response()
    resp.status_code = status
    resp.url = "https://contoso.sharepoint.com/_api/web/lists"
    body = {"error": {"code": code, "message": message}}
    resp._content = json.dumps(body).encode("utf-8")
    return resp


class TestCodeAndTypeNameMatching(unittest.TestCase):
    def test_sharepoint_catch_all(self):
        exc = ClientRequestException.from_response(_error_response("-1234567, Microsoft.SharePoint.SPException", "boom"))
        self.assertIsInstance(exc, SharePointException)
        self.assertNotIsInstance(exc, DuplicatedObjectException)


class TestPriorityDispatch(unittest.TestCase):
    def test_checkout_beats_status_only_lock(self):
        exc = ClientRequestException.from_response(
            _error_response(
                "-2130575306, Microsoft.SharePoint.SPFileCheckOutException",
                "The file is checked out for editing.",
                status=423,
            )
        )
        self.assertIsInstance(exc, SPFileCheckOutException)
        self.assertNotIsInstance(exc, FileLockedException)

    def test_specific_beats_catch_all(self):
        # Duplicate-list is SPException + a known HRESULT: the specific type wins.
        exc = ClientRequestException.from_response(
            _error_response(
                "-2130575342, Microsoft.SharePoint.SPException",
                "A list with the specified title already exists in this Web site.",
            )
        )
        self.assertIsInstance(exc, DuplicatedObjectException)
        self.assertNotIsInstance(exc, SharePointException)
        self.assertNotIsInstance(exc, SPListDataValidationException)


class TestParsedAccessors(unittest.TestCase):
    def test_hresult_and_error_type(self):
        exc = ClientRequestException.from_response(
            _error_response("-2130575169, Microsoft.SharePoint.SPDuplicateValuesFoundException", "dup")
        )
        self.assertEqual(exc.hresult, "-2130575169")
        self.assertEqual(exc.error_type, "Microsoft.SharePoint.SPDuplicateValuesFoundException")

    def test_graph_symbolic_code_has_no_hresult(self):
        resp = Response()
        resp.status_code = 423
        resp.url = "https://graph.microsoft.com/v1.0/drives/d/items/i"
        resp._content = b'{"error":{"code":"resourceLocked","message":"The resource is locked."}}'
        exc = ClientRequestException.from_response(resp)
        self.assertIsInstance(exc, FileLockedException)
        self.assertIsNone(exc.hresult)
        self.assertIsNone(exc.error_type)


if __name__ == "__main__":
    unittest.main()
