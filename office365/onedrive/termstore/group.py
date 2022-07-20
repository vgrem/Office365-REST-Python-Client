from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.onedrive.termstore.set_collection import SetCollection
from office365.runtime.paths.resource_path import ResourcePath


class GroupCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(GroupCollection, self).__init__(context, Group, resource_path)

    def add(self, display_name):
        """
        Create a new group object in a term store.

        :param str display_name: Name of the group to be created.
        :rtype: Group
        """
        props = {"displayName": display_name}
        return super(GroupCollection, self).add(**props)


class Group(Entity):

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
