from office365.entity_collection import EntityCollection
from office365.onenote.entity_hierarchy_model import OnenoteEntityHierarchyModel
from office365.onenote.notebooks.notebook import Notebook
from office365.onenote.sections.section import OnenoteSection
from office365.runtime.paths.resource_path import ResourcePath


class SectionGroup(OnenoteEntityHierarchyModel):
    """A section group in a OneNote notebook. Section groups can contain sections and section groups."""

    @property
    def section_groups_url(self):
        """The URL for the sectionGroups navigation property, which returns all the section groups in the section group.

        :rtype: str or None
        """
        return self.properties.get("sectionGroupsUrl", None)

    @property
    def sections_url(self):
        """The URL for the sections navigation property, which returns all the sections in the section group.

        :rtype: str or None
        """
        return self.properties.get("sectionsUrl", None)

    @property
    def parent_notebook(self):
        """The notebook that contains the section group. Read-only."""
        return self.get_property('parentNotebook',
                                 Notebook(self.context, ResourcePath("parentNotebook", self.resource_path)))

    @property
    def sections(self):
        """The sections in the section group. Read-only. Nullable.

        :rtype: EntityCollection
        """
        return self.get_property('sections',
                                 EntityCollection(self.context, OnenoteSection,
                                                  ResourcePath("sections", self.resource_path)))

    @property
    def section_groups(self):
        """Retrieve a list of onenoteSection objects from the specified notebook.

        :rtype: EntityCollection
        """
        return self.get_property('sectionGroups',
                                 EntityCollection(self.context, SectionGroup,
                                                  ResourcePath("sectionGroups", self.resource_path)))
