from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity_collection import EntityCollection
from office365.onenote.entity_hierarchy_model import OnenoteEntityHierarchyModel
from office365.onenote.notebooks.notebook import Notebook
from office365.onenote.sections.collection import OnenoteSectionCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.onenote.sectiongroups.section_group import SectionGroup


class SectionGroup(OnenoteEntityHierarchyModel):
    """A section group in a OneNote notebook. Section groups can contain sections and section groups."""

    @property
    def section_groups_url(self) -> Optional[str]:
        """
        The URL for the sectionGroups navigation property, which returns all the section groups in the section group.
        """
        return self.properties.get("sectionGroupsUrl", None)

    @property
    def sections_url(self) -> Optional[str]:
        """The URL for the sections navigation property, which returns all the sections in the section group."""
        return self.properties.get("sectionsUrl", None)

    @odata(name="parentNotebook")
    @property
    def parent_notebook(self) -> Notebook:
        """The notebook that contains the section group. Read-only."""
        return self.properties.get(
            "parentNotebook",
            Notebook(self.context, ResourcePath("parentNotebook", self.resource_path)),
        )

    @property
    def sections(self) -> OnenoteSectionCollection:
        """The sections in the section group. Read-only. Nullable."""
        return self.properties.get(
            "sections",
            OnenoteSectionCollection(
                self.context,
                ResourcePath("sections", self.resource_path),
            ),
        )

    @odata(name="sectionGroups")
    @property
    def section_groups(self) -> EntityCollection[SectionGroup]:
        """Retrieve a list of onenoteSection objects from the specified notebook."""
        return self.properties.get(
            "sectionGroups",
            EntityCollection(
                self.context,
                SectionGroup,
                ResourcePath("sectionGroups", self.resource_path),
            ),
        )

    @property
    def parent_section_group(self) -> SectionGroup:
        """Gets the parentSectionGroup property"""
        from office365.onenote.sectiongroups.section_group import SectionGroup

        return self.properties.get(
            "parentSectionGroup", SectionGroup(self.context, ResourcePath("parentSectionGroup", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SectionGroup"
