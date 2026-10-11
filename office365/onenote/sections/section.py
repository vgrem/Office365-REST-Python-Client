from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.directory.permissions.require_permission import require_permission
from office365.onenote.entity_hierarchy_model import OnenoteEntityHierarchyModel
from office365.onenote.operations.onenote import OnenoteOperation
from office365.onenote.pages.links import PageLinks
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.onenote.pages.collection import OnenotePageCollection
    from office365.onenote.sectiongroups.section_group import SectionGroup


class OnenoteSection(OnenoteEntityHierarchyModel):
    """A section in a OneNote notebook. Sections can contain pages."""

    @require_permission(delegated=["Notes.ReadWrite", "Notes.ReadWrite.All"], application=["Notes.ReadWrite.All"])
    def copy_to_section_group(
        self,
        group_id: str,
        id_: str,
        rename_as: str | None = None,
        site_collection_id: str | None = None,
        site_id: str | None = None,
    ) -> OnenoteOperation:
        """For Copy operations, you follow an asynchronous calling pattern: First call the Copy action,
        and then poll the operation endpoint for the result.

        Args:
            group_id (str): The id of the group to copy to. Use only when copying to a Microsoft 365 group.
            id_ (str): Required. The id of the destination section group.
            rename_as (str): The name of the copy. Defaults to the name of the existing item.
            site_collection_id (str):
            site_id (str):
        """
        return_type = OnenoteOperation(self.context)
        payload = {
            "groupId": group_id,
            "id": id_,
            "renameAs": rename_as,
            "siteCollectionId": site_collection_id,
            "siteId": site_id,
        }
        qry = ServiceOperationQuery(self, "copyToSectionGroup", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def is_default(self) -> Optional[bool]:
        """Indicates whether this is the user's default section. Read-only."""
        return self.properties.get("isDefault", None)

    @property
    def links(self) -> PageLinks:
        """Links for opening the section. The oneNoteClientURL link opens the section in the OneNote native client
        if it's installed. The oneNoteWebURL link opens the section in OneNote on the web.
        """
        return self.properties.get("links", PageLinks())

    @property
    def pages(self) -> OnenotePageCollection:
        """
        The collection of pages in the section. Read-only. Nullable.
        """
        from office365.onenote.pages.collection import OnenotePageCollection

        return self.properties.get(
            "pages",
            OnenotePageCollection(self.context, ResourcePath("pages", self.resource_path)),
        )

    @odata(name="parentNotebook")
    @property
    def parent_notebook(self):
        """
        The notebook that contains the page. Read-only.
        """
        from office365.onenote.notebooks.notebook import Notebook

        return self.properties.get(
            "parentNotebook",
            Notebook(self.context, ResourcePath("parentNotebook", self.resource_path)),
        )

    @odata(name="parentSectionGroup")
    @property
    def parent_section_group(self) -> SectionGroup:
        """
        The section group that contains the section. Read-only.
        """
        from office365.onenote.sectiongroups.section_group import SectionGroup

        return self.properties.get(
            "parentSectionGroup",
            SectionGroup(self.context, ResourcePath("parentSectionGroup", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return None  # type: ignore

    @property
    def pages_url(self) -> Optional[str]:
        """Gets the pagesUrl property"""
        return self.properties.get("pagesUrl", None)
