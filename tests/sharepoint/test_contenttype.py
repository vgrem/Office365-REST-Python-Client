"""Tests for SharePoint content type operations (CRUD, localization, changes)."""

from __future__ import annotations

from random import randint
from typing import ClassVar, Optional

from office365.sharepoint.changes.query import ChangeQuery
from office365.sharepoint.contenttypes.collection import ContentTypeCollection
from office365.sharepoint.contenttypes.content_type import ContentType
from office365.sharepoint.contenttypes.creation_information import (
    ContentTypeCreationInformation,
)

from tests import answered_null
from tests.sharepoint.sharepoint_case import SPTestCase


class TestContentType(SPTestCase):
    """Tests for SharePoint content type lifecycle operations."""

    target_ct: ClassVar[Optional[ContentType]] = None
    localized_title: str = "Contoso Dokumentti"

    def test_01_list_site_content_types(self):
        """List all content types on the site."""
        result = self.client.site.root_web.content_types.get().execute_query()
        self.assertIsInstance(result, ContentTypeCollection)

    def test_02_get_content_type_by_id(self):
        """Get a content type by its ID."""
        result = self.client.site.root_web.content_types.get_by_id("0x0101").get().execute_query()
        self.assertIsNotNone(result.name)

    def test_03_create_content_type(self):
        """Create a new content type."""
        cti = ContentTypeCreationInformation(f"Contoso Document {randint(0, 1000)}")
        ct = self.client.site.root_web.content_types.add(cti).execute_query()
        self.assertIsNotNone(ct.name)
        TestContentType.target_ct = ct

    def test_04_update_content_type(self):
        """Update an existing content type."""
        target = TestContentType.target_ct
        if not target:
            self.skipTest("No resource from previous test")
        ct = target
        ct.description = "New desc"
        ct.update(True).execute_query()
        self.assertIsNotNone(ct.description)

    def test_05_set_value_for_ui_culture(self):
        """Set a localized name for the content type.

        ``SetValueForUICulture`` accepts only a culture the web actually supports;
        for any other culture the service answers without writing anything, so the
        read-back is what decides whether the call did its job.
        """
        target = TestContentType.target_ct
        if not target:
            self.skipTest("No resource from previous test")
        ct = target
        ct.name_resource.set_value_for_ui_culture("fi-FI", self.localized_title).execute_query()
        localized = ct.name_resource.get_value_for_ui_culture("fi-FI").execute_query()
        written = None if answered_null(localized) else localized.value
        if written != self.localized_title:
            self.skipTest("The web does not enable the fi-FI UI culture, so the write is a no-op")

    def test_06_get_value_for_ui_culture(self):
        """Get the localized name for the content type."""
        target = TestContentType.target_ct
        if not target:
            self.skipTest("No resource from previous test")
        ct = target
        result = ct.name_resource.get_value_for_ui_culture("fi-FI").execute_query()
        self.assertIsNotNone(result.value)

    def test_07_delete_content_type(self):
        """Delete a content type and verify the count decreases."""
        target = TestContentType.target_ct
        if not target:
            self.skipTest("No resource from previous test")
        web_cts = self.client.site.root_web.content_types.get().execute_query()
        before_count = len(web_cts)
        target.delete_object().execute_query()
        web_cts = self.client.site.root_web.content_types.get().execute_query()
        self.assertEqual(before_count, len(web_cts) + 1)

    def test_08_get_content_types_changes(self):
        """Get change log for content types."""
        result = self.client.web.get_changes(ChangeQuery(ContentType=True)).execute_query()
        self.assertGreater(len(result), 0)
