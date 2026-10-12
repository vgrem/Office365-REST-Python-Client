from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity_collection import EntityCollection
from office365.onenote.entity_hierarchy_model import OnenoteEntityHierarchyModel
from office365.onenote.sections.collection import OnenoteSectionCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.onenote.notebook_links import NotebookLinks
    from office365.onenote.userrole import OnenoteUserRole


class Notebook(OnenoteEntityHierarchyModel):
    """A OneNote notebook."""

    @property
    def sections(self) -> OnenoteSectionCollection:
        """
        Retrieve a list of onenoteSection objects from the specified notebook.
        """
        return self.properties.get(
            "sections",
            OnenoteSectionCollection(
                self.context,
                ResourcePath("sections", self.resource_path),
            ),
        )

    @odata(name="sectionGroups")
    @property
    def section_groups(self):
        """
        Retrieve a list of onenoteSection objects from the specified notebook.
        """

        from office365.onenote.sectiongroups.section_group import SectionGroup

        return self.properties.get(
            "sectionGroups",
            EntityCollection(
                self.context,
                SectionGroup,
                ResourcePath("sectionGroups", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return None  # type: ignore

    @property
    def is_default(self) -> Optional[bool]:
        """Gets the isDefault property"""
        return self.properties.get("isDefault", None)

    @property
    def is_shared(self) -> Optional[bool]:
        """Gets the isShared property"""
        return self.properties.get("isShared", None)

    @property
    def links(self) -> NotebookLinks:
        """Gets the links property"""
        from office365.onenote.notebook_links import NotebookLinks

        return self.properties.get("links", NotebookLinks())

    @property
    def section_groups_url(self) -> Optional[str]:
        """Gets the sectionGroupsUrl property"""
        return self.properties.get("sectionGroupsUrl", None)

    @property
    def sections_url(self) -> Optional[str]:
        """Gets the sectionsUrl property"""
        return self.properties.get("sectionsUrl", None)

    @property
    def user_role(self) -> OnenoteUserRole:
        """Gets the userRole property"""
        from office365.onenote.userrole import OnenoteUserRole

        return self.properties.get("userRole", OnenoteUserRole.Unknown)
