from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.onedrive.termstore.set import Set
from office365.runtime.paths.resource_path import ResourcePath


class Group(Entity):

    @property
    def sets(self):
        """Collection of all sets available in the term store."""
        return self.properties.get('sets',
                                   EntityCollection(self.context, Set, ResourcePath("sets", self.resource_path)))
