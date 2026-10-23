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
    SecurityValidationException,
    SharePointException,
    SPContentTypeSealedException,
    SPDuplicateValuesFoundException,
    SPFieldValidationException,
    SPFileCheckOutException,
    SPFileLockedException,
    SPInvalidLookupValuesException,
    SPListDataValidationException,
    SPQueryThrottledException,
)
from requests import Response


def _error_response(code: str, message: str = "", status: int = 400) -> Response:
    resp = Response()
    resp.status_code = status
    resp.url = "https://contoso.sharepoint.com/_api/web/lists"
    body = {"error": {"code": code, "message": message}}
    resp._content = json.dumps(body).encode("utf-8")
    return resp


class TestSharePointExceptionHierarchy(unittest.TestCase):
    def test_concrete_types_are_sharepoint_exceptions(self):
        for exc_type in (
            SecurityValidationException,
            SPQueryThrottledException,
            SPFileCheckOutException,
            SPListDataValidationException,
            SPDuplicateValuesFoundException,
        ):
            self.assertTrue(issubclass(exc_type, SharePointException), exc_type)

    def test_alias_is_shared_lock_exception(self):
        self.assertIs(SPFileLockedException, FileLockedException)


class TestCodeAndTypeNameMatching(unittest.TestCase):
    def test_sharepoint_catch_all(self):
        exc = ClientRequestException.from_response(_error_response("-1234567, Microsoft.SharePoint.SPException", "boom"))
        self.assertIsInstance(exc, SharePointException)
        self.assertNotIsInstance(exc, DuplicatedObjectException)

    def test_non_sharepoint_stays_generic(self):
        exc = ClientRequestException.from_response(_error_response("-1, System.Exception", "boom"))
        self.assertNotIsInstance(exc, SharePointException)

    def test_list_data_validation_by_code(self):
        exc = ClientRequestException.from_response(
            _error_response(
                "-2130575162, Microsoft.SharePoint.SPListDataValidationException", "List data validation failed."
            )
        )
        self.assertIsInstance(exc, SPListDataValidationException)

    def test_field_value_validation_shares_server_type(self):
        # SharePoint reports both list- and field-level formula failures as SPListDataValidationException.
        exc = ClientRequestException.from_response(
            _error_response(
                "-2130575163, Microsoft.SharePoint.SPListDataValidationException", "List data validation failed."
            )
        )
        self.assertIsInstance(exc, SPListDataValidationException)

    def test_duplicate_unique_values(self):
        exc = ClientRequestException.from_response(
            _error_response(
                "-2130575169, Microsoft.SharePoint.SPDuplicateValuesFoundException",
                "duplicate values were found",
            )
        )
        self.assertIsInstance(exc, SPDuplicateValuesFoundException)

    def test_field_validation(self):
        exc = ClientRequestException.from_response(
            _error_response("-2146232832, Microsoft.SharePoint.SPFieldValidationException", "bad term")
        )
        self.assertIsInstance(exc, SPFieldValidationException)

    def test_type_name_only_without_known_hresult(self):
        # Types we could not probe still classify by the embedded .NET type name.
        for type_name, expected in (
            ("SPInvalidLookupValuesException", SPInvalidLookupValuesException),
            ("SPContentTypeSealedException", SPContentTypeSealedException),
        ):
            exc = ClientRequestException.from_response(
                _error_response(f"-9999999, Microsoft.SharePoint.{type_name}", "boom")
            )
            self.assertIsInstance(exc, expected, type_name)

    def test_localized_message_matches_by_code(self):
        exc = ClientRequestException.from_response(
            _error_response(
                "-2147024860, Microsoft.SharePoint.SPQueryThrottledException",
                "La operación supera el umbral de vista de lista.",
                status=500,
            )
        )
        self.assertIsInstance(exc, SPQueryThrottledException)

    def test_security_validation_by_hresult(self):
        exc = ClientRequestException.from_response(
            _error_response(
                "-2130575251, Microsoft.SharePoint.SPException",
                "The security validation for this page is invalid.",
                status=403,
            )
        )
        self.assertIsInstance(exc, SecurityValidationException)


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

    def test_shared_lock_still_typed(self):
        exc = ClientRequestException.from_response(
            _error_response(
                "-2147018894, Microsoft.SharePoint.SPFileLockException",
                "The file is locked for shared use by John Doe [membership].",
                status=423,
            )
        )
        self.assertIsInstance(exc, FileLockedException)
        self.assertNotIsInstance(exc, SPFileCheckOutException)

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
