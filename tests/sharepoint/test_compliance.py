"""Tests for SharePoint compliance operations (tags and records management)."""

from __future__ import annotations

import warnings
from typing import ClassVar, Optional

from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.features.definitions.scope import FeatureDefinitionScope
from office365.sharepoint.features.known_list import KnownFeaturesList
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.lists.list import List
from office365.sharepoint.lists.templates.type import ListTemplateType

from tests import answered_null, create_unique_name
from tests.sharepoint.sharepoint_case import SPTestCase


class TestCompliance(SPTestCase):
    """Tests for SharePoint compliance tag operations."""

    list_item: ClassVar[Optional[ListItem]] = None
    tag_name: ClassVar[Optional[str]] = None
    record_list: ClassVar[Optional[List]] = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.target_list: List = cls.client.web.lists.get_by_title("Documents")
        # Item-level records management runs on a library this test owns: the
        # shared document library may carry a tag whose term was deleted from the
        # tenant term store, which makes its items unreadable.
        cls.record_list = cls.client.web.lists.add_list(
            title=create_unique_name("Compliance_"), template_type=ListTemplateType.GenericList
        ).execute_query()

    @classmethod
    def tearDownClass(cls):
        if cls.record_list is None:
            return
        try:
            cls.record_list.delete_object().execute_query()
        except ClientRequestException as e:
            # ``test_08`` puts a retention label on its item, and a labelled item
            # cannot be deleted; the list stays behind for an operator to dispose of.
            warnings.warn(f"Could not delete {cls.record_list.title!r}: {e}", stacklevel=2)

    def test_01_get_site_available_tags(self):
        """Get available compliance tags for the site."""
        result = self.client.site.get_available_tags().execute_query()
        self.assertIsNotNone(result.value)
        if len(result.value) > 0:
            TestCompliance.tag_name = result.value[0].TagName

    def test_02_enable_place_records_management(self):
        """Enable the Place Records Management feature at the site scope.

        The feature definition has to be installed in the farm first, which is a
        tenant-wide configuration: when it is missing the service refuses the
        activation, and the library side of the contract (reading the activation
        state from the collection, not from a null ``GetById``) is pinned offline in
        ``tests/unit/test_feature_activation.py``.
        """
        if TestCompliance.tag_name is None:
            self.skipTest("No compliance tags available on this tenant")
        try:
            TestCompliance.enable_place_records_management()
        except ClientRequestException as e:
            self.skipTest(f"The farm does not install the Place Records Management feature: {e}")
        activated = self.client.site.features.get().execute_query()
        definition_ids = "".join(str(feature.definition_id).lower() for feature in activated)
        self.assertIn(KnownFeaturesList.PlaceRecordsManagement.value.lower(), definition_ids)

    @classmethod
    def enable_place_records_management(cls) -> None:
        """Activate the records management feature on the site (idempotent)."""
        cls.client.site.features.add(
            KnownFeaturesList.PlaceRecordsManagement, False, FeatureDefinitionScope.Site, True
        ).execute_query()

    def test_03_set_list_compliance_tag(self):
        """Apply a compliance tag to the target list."""
        if TestCompliance.tag_name is None:
            self.skipTest("No compliance tags available on this tenant")
        result = self.target_list.set_compliance_tag(TestCompliance.tag_name, True, True, True).execute_query()
        self.assertIsNotNone(result.resource_path)

    def test_04_get_list_compliance_tag(self):
        """Read back the compliance tag from the target list."""
        if TestCompliance.tag_name is None:
            self.skipTest("No compliance tags available on this tenant")
        result = self.target_list.get_compliance_tag().execute_query()
        self.assertIsNotNone(result.value)
        self.assertEqual(result.value.TagName, TestCompliance.tag_name)

    def test_05_reset_list_compliance_tag(self):
        """Reset (remove) the compliance tag from the target list."""
        if TestCompliance.tag_name is None:
            self.skipTest("No compliance tags available on this tenant")
        result = self.target_list.set_compliance_tag("", False, False, False).execute_query()
        self.assertIsNotNone(result.resource_path)

    def test_06_get_list_compliance_tag_after_reset(self):
        """Verify the compliance tag has been removed from the target list."""
        result = self.target_list.get_compliance_tag().execute_query()
        self.assertTrue(answered_null(result), "a reset list carries no compliance tag")

    def test_07_set_item_compliance_tag_with_hold(self):
        """Apply a compliance tag with hold to a list item."""
        if TestCompliance.tag_name is None:
            self.skipTest("No compliance tags available on this tenant")
        TestCompliance.list_item = self._get_target_item()
        if TestCompliance.list_item is None:
            self.skipTest("No items available in the target list")
        try:
            result = TestCompliance.list_item.set_compliance_tag_with_hold(TestCompliance.tag_name).execute_query()
            self.assertIsNotNone(result.resource_path)
        except ClientRequestException as e:
            self.skipTest(f"Tag with hold is not supported for the current site: {e}")

    def test_08_lock_record_item(self):
        """Lock a record item to prevent modifications."""
        if TestCompliance.list_item is None:
            self.skipTest("No list item is available to lock")
        try:
            self.assertIsNotNone(TestCompliance.list_item.resource_path)
            TestCompliance.list_item.lock_record_item().execute_query()
        except ClientRequestException as e:
            self.skipTest(f"Record locking is not available for the current item: {e}")

    def _get_target_item(self) -> Optional[ListItem]:
        """Returns the first item of the record list, or None when the list is empty."""
        records = self.record_list.items.get().execute_query()
        if not records:
            self.record_list.add_item({"Title": "record"}).execute_query()
            records = self.record_list.items.get().execute_query()
        return records[0] if records else None
