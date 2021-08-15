from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.onenote.notebooks.notebook import Notebook
from office365.onenote.operations.onenote_operation import OnenoteOperation
from office365.onenote.pages.page import OnenotePage
from office365.runtime.resource_path import ResourcePath


class Onenote(Entity):

    @property
    def notebooks(self):
        """Retrieve a list of notebook objects."""
        return self.get_property('notebooks',
                                 EntityCollection(self.context, Notebook,
                                                  ResourcePath("notebooks", self.resource_path)))

    @property
    def operations(self):
        """Retrieve a list of OneNote operations."""
        return self.get_property('operations',
                                 EntityCollection(self.context, OnenoteOperation,
                                                  ResourcePath("operations", self.resource_path)))

    @property
    def pages(self):
        """Retrieve a list of page objects."""
        return self.get_property('pages',
                                 EntityCollection(self.context, OnenotePage,
                                                  ResourcePath("pages", self.resource_path)))
