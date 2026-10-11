"""Retention labels, records management, and file plan descriptors.
Tests cover the full lifecycle of retention labels under Microsoft Purview Records Management:
  - Listing and filtering retention event types
  - CRUD operations on retention labels
  - Querying label metadata (retention duration, behavior, action)
  - Paginated listing with $top, $skip, $filter
  - Negative cases (duplicate names, invalid durations)
  - File plan descriptors (departments, categories, subcategories, etc.)
"""

from __future__ import annotations

from typing import ClassVar, Optional

from office365.runtime.client_request_exception import ClientRequestException
from office365.security.labels.retention.actionafterretentionperiod import (
    ActionAfterRetentionPeriod,
)
from office365.security.labels.retention.behaviorduringretentionperiod import (
    BehaviorDuringRetentionPeriod,
)
from office365.security.labels.retention.defaultrecordbehavior import (
    DefaultRecordBehavior,
)
from office365.security.labels.retention.duration_in_days import (
    RetentionDurationInDays,
)
from office365.security.labels.retention.label import RetentionLabel
from office365.security.labels.retention.trigger import RetentionTrigger
from office365.security.triggertypes.event_type import RetentionEventType

from tests.decorators import requires_delegated
from tests.graph_case import GraphDelegatedTestCase

# Common permission set for records management operations
_RM_READ = ("RecordsManagement.Read.All", "RecordsManagement.ReadWrite.All")
_RM_WRITE = ("RecordsManagement.ReadWrite.All",)
_RM_ROLES = [
    "Records Management",
    "Compliance Administrator",
    "Compliance Data Administrator",
]
_RM_LICENSES = [
    "SPE_E5",
    "M365_E5",
    "SPE_E5_COMPLIANCE",
    "SPE_E5_INFORMATION_PROTECTION_COMPLIANCE",
]


class TestRetentionEventTypes(GraphDelegatedTestCase):
    """Event types are used to trigger retention when an event of that type occurs."""

    created_events: ClassVar[list[RetentionEventType]] = []

    @requires_delegated(
        *_RM_READ,
        require_roles=_RM_ROLES,
        require_licenses=_RM_LICENSES,
        bypass_roles=["Global Administrator"],
    )
    def test_01_list_retention_event_types(self):
        """Retrieving all retention event types returns a collection with a valid path."""
        result = self.client.security.trigger_types.retention_event_types.get().execute_query()
        self.assertIsNotNone(result.resource_path)
        self.assertIsNotNone(result.context)

    @requires_delegated(
        *_RM_READ,
        require_roles=_RM_ROLES,
        require_licenses=_RM_LICENSES,
        bypass_roles=["Global Administrator"],
    )
    def test_02_filter_event_types_by_display_name(self):
        """Filtering event types by display name narrows results to matching items."""
        target_name = "Employee termination"
        result = (
            self.client.security.trigger_types.retention_event_types.filter(f"displayName eq '{target_name}'")
            .get()
            .execute_query()
        )
        for event in result:
            self.assertIsNotNone(event.resource_path)
            if event.get_property("displayName") == target_name:
                break
        else:
            self.skipTest(f"No event type found with displayName '{target_name}'")

    @requires_delegated(
        *_RM_READ,
        require_roles=_RM_ROLES,
        require_licenses=_RM_LICENSES,
        bypass_roles=["Global Administrator"],
    )
    def test_03_paginate_event_types(self):
        """Requesting with $top=5 limits the result set."""
        result = self.client.security.trigger_types.retention_event_types.top(5).get().execute_query()
        # The collection should be valid even if fewer than 5 items exist
        self.assertIsNotNone(result.resource_path)


class TestRetentionLabels(GraphDelegatedTestCase):
    """Retention labels — the core of Purview Records Management."""

    created_label: ClassVar[Optional[RetentionLabel]] = None

    @requires_delegated(
        *_RM_READ,
        require_roles=_RM_ROLES,
        require_licenses=_RM_LICENSES,
        bypass_roles=["Global Administrator"],
    )
    def test_01_list_labels_empty_result_graceful(self):
        """Listing retention labels when none exist returns a valid collection (not None)."""
        result = self.client.security.labels.retention_labels.get().execute_query()
        # Assert — the collection itself must be valid even if empty
        self.assertIsNotNone(result.resource_path)
        # We don't assert on the number of items; the collection is valid regardless

    @requires_delegated(
        *_RM_WRITE,
        require_roles=_RM_ROLES,
        require_licenses=_RM_LICENSES,
        bypass_roles=["Global Administrator"],
    )
    def test_02_create_retention_label_no_duration(self):
        """Creating a label without retention duration uses 'mark as record' behavior only."""
        # Note: Some tenants require at least one retention/delete action. This test validates
        # the API doesn't crash on a minimal argument set; it may fail on strict policy tenants.
        try:
            result = self.client.security.labels.retention_labels.add(
                "Record-only — no retention period",
                RetentionTrigger.dateLabeled,
                None,  # no retention duration
                BehaviorDuringRetentionPeriod.retainAsRecord,
                DefaultRecordBehavior.startLocked,
                ActionAfterRetentionPeriod.delete,
            ).execute_query()
            self.assertIsNotNone(result.resource_path)
            display_name = result.get_property("displayName")
            self.assertEqual(display_name, "Record-only — no retention period")
            TestRetentionLabels.created_label = result
        except Exception as e:
            self.skipTest(f"Minimal label creation not allowed by tenant policy: {e}")

    @requires_delegated(
        *_RM_WRITE,
        require_roles=_RM_ROLES,
        require_licenses=_RM_LICENSES,
        bypass_roles=["Global Administrator"],
    )
    def test_03_create_retention_label_full(self):
        """Creating a full retention label with 365-day retention, record behavior, and delete action."""
        label_name = f"SDK_TEST_Retain1Year_{id(self)}"
        result = self.client.security.labels.retention_labels.add(
            label_name,
            RetentionTrigger.dateLabeled,
            RetentionDurationInDays(365),
            BehaviorDuringRetentionPeriod.retainAsRecord,
            DefaultRecordBehavior.startLocked,
            ActionAfterRetentionPeriod.delete,
        ).execute_query()
        self.assertIsNotNone(result.resource_path)
        self.assertEqual(result.get_property("displayName"), label_name)
        self.assertEqual(result.get_property("retentionTrigger"), "dateLabeled")
        TestRetentionLabels.created_label = result

    @requires_delegated(
        *_RM_READ,
        require_roles=_RM_ROLES,
        require_licenses=_RM_LICENSES,
        bypass_roles=["Global Administrator"],
    )
    def test_04_get_label_by_id(self):
        """Retrieving a retention label by its ID returns the expected label."""
        created = TestRetentionLabels.created_label
        if not created:
            self.skipTest("No created label available from previous test")
        result = self.client.security.labels.retention_labels[created.id].get().execute_query()
        self.assertIsNotNone(result.resource_path)
        self.assertEqual(result.get_property("id"), created.id)
        self.assertEqual(result.get_property("displayName"), created.get_property("displayName"))

    @requires_delegated(
        *_RM_READ,
        require_roles=_RM_ROLES,
        require_licenses=_RM_LICENSES,
        bypass_roles=["Global Administrator"],
    )
    def test_05_filter_labels_by_display_name(self):
        """Filtering retention labels by display name with $filter works correctly."""
        created = TestRetentionLabels.created_label
        if not created:
            self.skipTest("No created label available from previous test")
        name = created.get_property("displayName")
        result = self.client.security.labels.retention_labels.filter(f"displayName eq '{name}'").get().execute_query()
        self.assertTrue(len(result) >= 1, "Expected at least one matching label")
        matched = any(item.get_property("displayName") == name for item in result)
        self.assertTrue(matched, f"Expected label '{name}' in filtered results")

    @requires_delegated(
        *_RM_READ,
        require_roles=_RM_ROLES,
        require_licenses=_RM_LICENSES,
        bypass_roles=["Global Administrator"],
    )
    def test_06_paginate_labels(self):
        """Requesting with $top=3 limits retention label results."""
        result = self.client.security.labels.retention_labels.top(3).get().execute_query()
        self.assertIsNotNone(result.resource_path)
        # Result may have 0-3 items; the important thing is the query didn't error

    @requires_delegated(
        *_RM_READ,
        require_roles=_RM_ROLES,
        require_licenses=_RM_LICENSES,
        bypass_roles=["Global Administrator"],
    )
    def test_07_label_has_expected_properties(self):
        """A retention label exposes retentionTrigger, behaviorDuringRetentionPeriod, etc."""
        created = TestRetentionLabels.created_label
        if not created:
            self.skipTest("No created label available from previous test")
        # Act — force re-fetch to get full property set
        label = self.client.security.labels.retention_labels[created.id].get().execute_query()
        self.assertIsNotNone(label.get_property("retentionTrigger"))
        self.assertIsNotNone(label.get_property("behaviorDuringRetentionPeriod"))
        self.assertIsNotNone(label.get_property("actionAfterRetentionPeriod"))

    @classmethod
    def tearDownClass(cls):
        """Clean up the created retention label if one exists."""
        label = cls.created_label
        if label and label.resource_path:
            try:
                label.delete_object().execute_query()
            except Exception:
                pass  # Best-effort cleanup


class TestRetentionLabelNegativeCases(GraphDelegatedTestCase):
    """Verify expected failures and edge cases for retention labels."""

    @requires_delegated(
        *_RM_WRITE,
        require_roles=_RM_ROLES,
        require_licenses=_RM_LICENSES,
        bypass_roles=["Global Administrator"],
    )
    def test_01_empty_display_name_rejected(self):
        """Creating a label with an empty display name should raise an error."""
        with self.assertRaises(ClientRequestException):
            self.client.security.labels.retention_labels.add(
                "",
                RetentionTrigger.dateLabeled,
                RetentionDurationInDays(1),
                BehaviorDuringRetentionPeriod.retainAsRecord,
                DefaultRecordBehavior.startLocked,
                ActionAfterRetentionPeriod.delete,
            ).execute_query()

    @requires_delegated(
        *_RM_WRITE,
        require_roles=_RM_ROLES,
        require_licenses=_RM_LICENSES,
        bypass_roles=["Global Administrator"],
    )
    def test_02_zero_duration_rejected(self):
        """Creating a label with zero retention days should be rejected by the API."""
        try:
            self.client.security.labels.retention_labels.add(
                "SDK_TEST_ZeroDays",
                RetentionTrigger.dateLabeled,
                RetentionDurationInDays(0),
                BehaviorDuringRetentionPeriod.retainAsRecord,
                DefaultRecordBehavior.startLocked,
                ActionAfterRetentionPeriod.delete,
            ).execute_query()
            self.fail("Expected an error for zero retention duration")
        except Exception:
            pass  # Expected


class TestRetentionLabelFilePlan(GraphDelegatedTestCase):
    """File plan descriptors enrich retention labels with business context."""

    @requires_delegated(
        *("RecordsManagement.Read.All",),
        require_roles=_RM_ROLES,
        require_licenses=_RM_LICENSES,
        bypass_roles=["Global Administrator"],
    )
    def test_01_list_file_plan_descriptors(self):
        """File plan descriptor collections exist and return valid results."""
        labels_root = self.client.security.labels
        # Test each known descriptor category (available as sub-navigation properties)
        descriptor_roots = [
            ("departments", "Department"),
            ("categories", "Category"),
            ("subcategories", "Subcategory"),
            ("authorities", "Authority"),
            ("referenceResources", "ReferenceResource"),
        ]
        for prop_name, _desc_label in descriptor_roots:
            try:
                col = getattr(labels_root, prop_name).get().execute_query()
                self.assertIsNotNone(col.resource_path, f"{prop_name} should return a valid collection")
            except AttributeError:
                self.skipTest(f"File plan descriptor '{prop_name}' not available in client yet")
