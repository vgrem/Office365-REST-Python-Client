from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.onenote.notebooks.notebook_collection import NotebookCollection
from office365.onenote.operations.onenote_operation import OnenoteOperation
from office365.onenote.pages.page import OnenotePageCollection
from office365.onenote.resources.resource import OnenoteResource
from office365.onenote.sectiongroups.section_group import SectionGroup
from office365.onenote.sections.section import OnenoteSection
from office365.runtime.paths.resource_path import ResourcePath


class Onenote(Entity):

    @property
    def notebooks(self):
        """Retrieve a list of notebook objects.

        :rtype: NotebookCollection
        """
        return self.get_property('notebooks',
                                 NotebookCollection(self.context, ResourcePath("notebooks", self.resource_path)))

    @property
    def operations(self):
        """Retrieve a list of OneNote operations.

        :rtype: EntityCollection
        """
        return self.get_property('operations',
                                 EntityCollection(self.context, OnenoteOperation,
                                                  ResourcePath("operations", self.resource_path)))

    @property
    def pages(self):
        """Retrieve a list of page objects.

        :rtype: OnenotePageCollection
        """
        return self.get_property('pages',
                                 OnenotePageCollection(self.context, ResourcePath("pages", self.resource_path)))

    @property
    def resources(self):
        """Retrieve a list of Resources objects from the specified notebook.

        :rtype: EntityCollection
        """
        return self.get_property('resources',
                                 EntityCollection(self.context, OnenoteResource,
                                                  ResourcePath("resources", self.resource_path)))

    @property
    def sections(self):
        """Retrieve a list of onenoteSection objects from the specified notebook.

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

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "sectionGroups": self.section_groups
            }
            default_value = property_mapping.get(name, None)
        return super(Onenote, self).get_property(name, default_value)
