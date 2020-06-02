from office365.graph.directory.directoryObjectCollection import DirectoryObjectCollection
from office365.graph.entity import Entity
from office365.runtime.resource_path import ResourcePath


class Directory(Entity):
    """Represents a deleted item in the directory. When an item is deleted, it is added to the deleted items
    "container". Deleted items will remain available to restore for up to 30 days. After 30 days, the items are
    permanently deleted. """

    def get_deleted_items(self, entity_type=None):
        """Recently deleted items. Read-only. Nullable."""
        if self.is_property_available('deletedItems'):
            return self.properties['deletedItems']
        else:
            res_path = entity_type and ResourcePath(entity_type, ResourcePath("deletedItems", self.resource_path)) or\
                       ResourcePath("deletedItems", self.resource_path)
            return DirectoryObjectCollection(self.context, res_path)

    @property
    def deletedGroups(self):
        """Recently deleted groups"""
        return self.get_deleted_items("microsoft.graph.group")

    @property
    def deletedUsers(self):
        """Recently deleted users"""
        return self.get_deleted_items("microsoft.graph.user")

    @property
    def deletedApplications(self):
        """Recently deleted applications"""
        return self.get_deleted_items("microsoft.graph.application")
