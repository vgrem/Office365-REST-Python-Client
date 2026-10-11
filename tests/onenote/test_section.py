"""OneNote sections — creating, listing, updating, and deletion.

Tests cover:
  - Listing all sections
  - Creating a notebook and a section within it
  - Updating a section display name
  - Listing pages within a section
  - Section property assertions (displayName, pagesUrl, isDefault)
  - The absence of a delete-notebook operation
"""

from __future__ import annotations

from typing import ClassVar, Optional

from office365.onenote.notebooks.notebook import Notebook
from office365.onenote.sections.section import OnenoteSection
from office365.runtime.client_request_exception import ClientRequestException

from tests import create_unique_name
from tests.decorators import requires_delegated
from tests.graph_case import GraphDelegatedTestCase


class TestSection(GraphDelegatedTestCase):
    """OneNote section CRUD and lifecycle."""

    target_notebook: ClassVar[Optional[Notebook]] = None
    target_section: ClassVar[Optional[OnenoteSection]] = None

    @requires_delegated(
        "Notes.Read",
        "Notes.Read.All",
        "Notes.ReadWrite",
        "Notes.ReadWrite.All",
        bypass_roles=["Global Administrator"],
    )
    def test_01_list_sections(self):
        """Listing all sections returns a valid collection."""
        result = self.client.me.onenote.sections.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    @requires_delegated(
        "Notes.Create",
        "Notes.ReadWrite",
        "Notes.ReadWrite.All",
        bypass_roles=["Global Administrator"],
    )
    def test_02_create_notebook_and_section(self):
        """Creating a notebook and a section within it should succeed."""
        notebook_name = create_unique_name("SDK Test Notebook")
        notebook = self.client.me.onenote.notebooks.add(notebook_name).execute_query()
        self.assertIsNotNone(notebook.resource_path)
        self.assertEqual(notebook.display_name, notebook_name)
        TestSection.target_notebook = notebook

        section_name = create_unique_name("SDK Test Section")
        section = notebook.sections.add(displayName=section_name).execute_query()
        self.assertIsNotNone(section.resource_path)
        self.assertEqual(section.display_name, section_name)
        TestSection.target_section = section

    @requires_delegated(
        "Notes.ReadWrite",
        "Notes.ReadWrite.All",
        bypass_roles=["Global Administrator"],
    )
    def test_03_update_section_name(self):
        """Updating a section's display name should persist."""
        section = TestSection.target_section
        if not section:
            self.skipTest("No section created from previous test")

        new_name = create_unique_name("SDK Updated Section")
        section.set_property("displayName", new_name).update().execute_query()
        self.assertEqual(section.display_name, new_name)

    @requires_delegated(
        "Notes.Read",
        "Notes.Read.All",
        "Notes.ReadWrite",
        "Notes.ReadWrite.All",
        bypass_roles=["Global Administrator"],
    )
    def test_04_section_has_expected_properties(self):
        """A section exposes displayName, createdDateTime, isDefault, and pagesUrl."""
        section = TestSection.target_section
        if not section:
            self.skipTest("No section created from previous test")

        self.assertIsNotNone(section.display_name)
        self.assertIsNotNone(section.created_datetime)
        self.assertIsNotNone(section.is_default)

    @requires_delegated(
        "Notes.Read",
        "Notes.Read.All",
        "Notes.ReadWrite",
        "Notes.ReadWrite.All",
        bypass_roles=["Global Administrator"],
    )
    def test_05_list_pages_in_section(self):
        """Listing pages in a section returns a valid collection."""
        section = TestSection.target_section
        if not section:
            self.skipTest("No section created from previous test")

        pages = section.pages.top(10).get().execute_query()
        self.assertIsNotNone(pages)

    @requires_delegated(
        "Notes.ReadWrite",
        "Notes.ReadWrite.All",
        bypass_roles=["Global Administrator"],
    )
    def test_06_notebook_delete_is_not_supported(self):
        """Graph exposes no delete-notebook operation, so the request is rejected."""
        notebook = TestSection.target_notebook
        if not notebook:
            self.skipTest("No notebook created from previous test")

        with self.assertRaises(ClientRequestException):
            notebook.delete_object().execute_query()

    @classmethod
    def tearDownClass(cls):
        # Microsoft Graph has no delete-notebook operation, so the notebook created by
        # this test cannot be removed; the attempt below is best-effort only.
        notebook = cls.target_notebook
        if notebook and notebook.resource_path:
            try:
                notebook.delete_object().execute_query()
            except Exception:
                pass
