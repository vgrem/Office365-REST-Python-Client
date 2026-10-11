"""OneNote notebooks — creating, listing, recent notebooks, sections, deletion.

Tests cover:
  - Creating a notebook with a unique name
  - Listing all notebooks
  - Getting recent notebooks
  - Creating a section within a notebook
  - Listing sections in a notebook
  - Notebook property assertions (displayName, createdDateTime, isDefault)
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


class TestNotebook(GraphDelegatedTestCase):
    """OneNote notebook CRUD and sub-resources."""

    target_notebook: ClassVar[Optional[Notebook]] = None
    target_section: ClassVar[Optional[OnenoteSection]] = None

    @requires_delegated(
        "Notes.Create",
        "Notes.ReadWrite",
        "Notes.ReadWrite.All",
        bypass_roles=["Global Administrator"],
    )
    def test_01_create_notebook(self):
        """Creating a notebook with a unique name should succeed."""
        name = create_unique_name("SDK Test Notebook")
        result = self.client.me.onenote.notebooks.add(name).execute_query()
        self.assertIsNotNone(result.resource_path)
        self.assertIsNotNone(result.id)
        self.assertEqual(result.display_name, name)
        TestNotebook.target_notebook = result

    @requires_delegated(
        "Notes.Read",
        "Notes.Read.All",
        "Notes.ReadWrite",
        "Notes.ReadWrite.All",
        "Notes.Create",
        bypass_roles=["Global Administrator"],
    )
    def test_02_list_notebooks(self):
        """Listing all notebooks returns a valid collection."""
        result = self.client.me.onenote.notebooks.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    @requires_delegated(
        "Notes.Read",
        "Notes.Read.All",
        "Notes.ReadWrite",
        "Notes.ReadWrite.All",
        bypass_roles=["Global Administrator"],
    )
    def test_03_get_recent_notebooks(self):
        """Getting recent notebooks returns a list of accessed notebooks."""
        result = self.client.me.onenote.notebooks.get_recent_notebooks().execute_query()
        self.assertIsNotNone(result.value)

    @requires_delegated(
        "Notes.Read",
        "Notes.Read.All",
        "Notes.ReadWrite",
        "Notes.ReadWrite.All",
        bypass_roles=["Global Administrator"],
    )
    def test_04_notebook_has_expected_properties(self):
        """A notebook exposes displayName, createdDateTime, isDefault, and links."""
        notebook = TestNotebook.target_notebook
        if not notebook:
            self.skipTest("No notebook created from previous test")

        self.assertIsNotNone(notebook.display_name)
        self.assertIsNotNone(notebook.created_datetime)
        self.assertIsNotNone(notebook.get_property("isDefault"))

    @requires_delegated(
        "Notes.Create",
        "Notes.ReadWrite",
        "Notes.ReadWrite.All",
        bypass_roles=["Global Administrator"],
    )
    def test_05_create_section_in_notebook(self):
        """Creating a section within the notebook should succeed."""
        notebook = TestNotebook.target_notebook
        if not notebook:
            self.skipTest("No notebook created from previous test")

        name = create_unique_name("SDK Test Section")
        result = notebook.sections.add(displayName=name).execute_query()
        self.assertIsNotNone(result.resource_path)
        self.assertEqual(result.display_name, name)
        TestNotebook.target_section = result

    @requires_delegated(
        "Notes.Read",
        "Notes.Read.All",
        "Notes.ReadWrite",
        "Notes.ReadWrite.All",
        bypass_roles=["Global Administrator"],
    )
    def test_06_list_sections_in_notebook(self):
        """Listing sections in a notebook returns a valid collection."""
        notebook = TestNotebook.target_notebook
        if not notebook:
            self.skipTest("No notebook created from previous test")

        sections = notebook.sections.get().execute_query()
        self.assertIsNotNone(sections)

    @requires_delegated(
        "Notes.Read",
        "Notes.Read.All",
        "Notes.ReadWrite",
        "Notes.ReadWrite.All",
        bypass_roles=["Global Administrator"],
    )
    def test_07_section_has_expected_properties(self):
        """A section exposes displayName, createdDateTime, and pagesUrl."""
        section = TestNotebook.target_section
        if not section:
            self.skipTest("No section created from previous test")

        self.assertIsNotNone(section.display_name)
        self.assertIsNotNone(section.created_datetime)
        self.assertIsNotNone(section.get_property("pagesUrl"))

    @requires_delegated(
        "Notes.ReadWrite",
        "Notes.ReadWrite.All",
        bypass_roles=["Global Administrator"],
    )
    def test_08_notebook_delete_is_not_supported(self):
        """Graph exposes no delete-notebook operation, so the request is rejected."""
        notebook = TestNotebook.target_notebook
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
