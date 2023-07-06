from office365.entity import Entity
from office365.onedrive.termstore.sets.collection import SetCollection
from office365.runtime.paths.resource_path import ResourcePath


class Group(Entity):
    """Term Group"""

    @property
    def display_name(self):
        """Name of the group."""
        return self.properties.get("displayName", None)

    @property
    def parent_site_id(self):
        """ID of the parent site of this group."""
        return self.properties.get("parentSiteId", None)

    @property
    def sets(self):
        """Collection of all sets available in the term store."""
        return self.properties.get('sets',
                                   SetCollection(self.context, ResourcePath("sets", self.resource_path), self))

    @property
    def entity_type_name(self):
        return None
