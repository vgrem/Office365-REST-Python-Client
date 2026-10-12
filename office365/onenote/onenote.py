from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.onenote.notebooks.collection import NotebookCollection
from office365.onenote.operations.onenote import OnenoteOperation
from office365.onenote.pages.collection import OnenotePageCollection
from office365.onenote.resources.resource import OnenoteResource
from office365.onenote.sectiongroups.section_group import SectionGroup
from office365.onenote.sections.collection import OnenoteSectionCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata


class Onenote(Entity):
    """The entry point for OneNote resources."""

    @property
    def notebooks(self) -> NotebookCollection:
        """Retrieve a list of notebook objects."""
        return self.properties.get(
            "notebooks", NotebookCollection(self.context, ResourcePath("notebooks", self.resource_path))
        )

    @property
    def operations(self) -> EntityCollection[OnenoteOperation]:
        """Retrieve a list of OneNote operations."""
        return self.properties.get(
            "operations",
            EntityCollection(self.context, OnenoteOperation, ResourcePath("operations", self.resource_path)),
        )

    @property
    def pages(self) -> OnenotePageCollection:
        """Retrieve a list of page objects."""
        return self.properties.get(
            "pages", OnenotePageCollection(self.context, ResourcePath("pages", self.resource_path))
        )

    @property
    def resources(self) -> EntityCollection[OnenoteResource]:
        """Retrieve a list of Resources objects from the specified notebook."""
        return self.properties.get(
            "resources", EntityCollection(self.context, OnenoteResource, ResourcePath("resources", self.resource_path))
        )

    @property
    def sections(self) -> OnenoteSectionCollection:
        """Retrieve a list of onenoteSection objects from the specified notebook."""
        return self.properties.get(
            "sections", OnenoteSectionCollection(self.context, ResourcePath("sections", self.resource_path))
        )

    @odata(name="sectionGroups")
    @property
    def section_groups(self) -> EntityCollection[SectionGroup]:
        """Retrieve a list of onenoteSection objects from the specified notebook."""
        return self.properties.get(
            "sectionGroups",
            EntityCollection(self.context, SectionGroup, ResourcePath("sectionGroups", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Onenote"
