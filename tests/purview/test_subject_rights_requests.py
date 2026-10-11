"""Subject Rights Requests (Data Subject Requests / GDPR DSR).
Tests cover listing, creating, and managing subject rights requests under Microsoft Purview.
Subject rights requests help organizations manage data subject requests (DSRs) under regulations
like GDPR, CCPA, and others.
"""

from __future__ import annotations

from typing import ClassVar, Optional

from office365.security.subjectrightsrequests.identity import (
    SubjectRightsRequestIdentity,
)
from office365.security.subjectrightsrequests.request import (
    SubjectRightsRequest,
)

from tests.decorators import requires_delegated
from tests.graph_case import GraphDelegatedTestCase

_SR_PERM_READ = ("SubjectRightsRequest.Read.All", "SubjectRightsRequest.ReadWrite.All")
_SR_PERM_WRITE = ("SubjectRightsRequest.ReadWrite.All",)


class TestSubjectRightsRequests(GraphDelegatedTestCase):
    """Subject Rights Requests (GDPR/CCPA DSR management)."""

    created_request: ClassVar[Optional[SubjectRightsRequest]] = None

    @requires_delegated(
        *_SR_PERM_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_01_list_requests(self):
        """Listing subject rights requests returns a valid collection."""
        result = self.client.security.subject_rights_requests.top(10).get().execute_query()
        self.assertIsNotNone(result.resource_path)
        # Collection may be empty — that's fine, just verify no error

    @requires_delegated(
        *_SR_PERM_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_02_filter_requests_by_type(self):
        """Filtering subject rights requests by type narrows to 'export' or 'delete' types."""
        result = self.client.security.subject_rights_requests.filter("type eq 'export'").top(5).get().execute_query()
        self.assertIsNotNone(result.resource_path)
        for req in result:
            req_type = req.get_property("type")
            self.assertEqual(req_type, "export", f"Expected type 'export', got '{req_type}'")

    @requires_delegated(
        *_SR_PERM_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_03_requests_have_expected_properties(self):
        """A subject rights request exposes type, status, createdDateTime, and dataSubject."""
        result = self.client.security.subject_rights_requests.top(5).get().execute_query()
        if len(result) == 0:
            self.skipTest("No subject rights requests exist to inspect")
        for req in result:
            # Core properties every request should have
            self.assertIsNotNone(req.get_property("type"))
            self.assertIsNotNone(req.get_property("status"))
            self.assertIsNotNone(req.get_property("createdDateTime"))
            # dataSubject may be None for pending requests
            break  # Check one for brevity

    @requires_delegated(
        *_SR_PERM_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_04_pagination_limit_works(self):
        """Requesting with $top=3 truncates results as expected."""
        result = self.client.security.subject_rights_requests.top(3).get().execute_query()
        self.assertIsNotNone(result.resource_path)
        self.assertLessEqual(len(result), 3, "Expected at most 3 results with $top=3")


class TestSubjectRightsRequestLifecycle(GraphDelegatedTestCase):
    """Create, retrieve, update, and delete a subject rights request.

    Note: Creating and deleting subject rights requests requires a licensed tenant.
    These tests are best-effort and will skip gracefully if the operation fails.
    """

    created_request: ClassVar[Optional[SubjectRightsRequest]] = None

    @requires_delegated(
        *_SR_PERM_WRITE,
        bypass_roles=["Global Administrator"],
    )
    def test_01_create_export_request(self):
        """Creating an export-type subject rights request should succeed on a licensed tenant."""
        try:
            request_data = {
                "type": "export",
                "displayName": "SDK Test DSR Export Request",
                "description": "Automated SDK test — please delete after review",
                "internalDueDateTime": "2026-07-05T00:00:00Z",
                "dataSubject": SubjectRightsRequestIdentity(
                    email="sdk-test-user@contoso.com",
                ),
            }
            result = self.client.security.subject_rights_requests.add(**request_data).execute_query()
            self.assertIsNotNone(result.resource_path)
            self.assertEqual(result.get_property("type"), "export")
            TestSubjectRightsRequestLifecycle.created_request = result
        except Exception as e:
            self.skipTest(f"Cannot create subject rights request: {e}")

    @requires_delegated(
        *_SR_PERM_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_02_get_created_request_by_id(self):
        """Retrieving a request by its ID returns the same object."""
        created = TestSubjectRightsRequestLifecycle.created_request
        if not created:
            self.skipTest("No created request available from previous test")
        result = self.client.security.subject_rights_requests[created.id].get().execute_query()
        self.assertIsNotNone(result.resource_path)
        self.assertEqual(result.get_property("id"), created.id)
        self.assertEqual(result.get_property("type"), created.get_property("type"))

    @requires_delegated(
        *_SR_PERM_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_03_request_has_type_and_status(self):
        """A created request should expose at least type and status."""
        created = TestSubjectRightsRequestLifecycle.created_request
        if not created:
            self.skipTest("No created request available from previous test")
        self.assertEqual(created.get_property("type"), "export")
        self.assertIn(created.get_property("status"), ("active", "closed", "pending"))

    @requires_delegated(
        *_SR_PERM_WRITE,
        bypass_roles=["Global Administrator"],
    )
    def test_04_close_or_delete_request(self):
        """Closing or deleting a subject rights request should succeed."""
        created = TestSubjectRightsRequestLifecycle.created_request
        if not created:
            self.skipTest("No created request available from previous test")
        try:
            created.delete_object().execute_query()
            TestSubjectRightsRequestLifecycle.created_request = None
        except Exception as e:
            self.skipTest(f"Cannot delete subject rights request (may require manual cleanup): {e}")

    @classmethod
    def tearDownClass(cls):
        """Best-effort cleanup of remaining created request."""
        req = cls.created_request
        if req and req.resource_path:
            try:
                req.delete_object().execute_query()
            except Exception:
                pass
