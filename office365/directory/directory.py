from office365.directory.directoryObjectCollection import DirectoryObjectCollection
from office365.entity import Entity
from office365.runtime.resource_path import ResourcePath


class Directory(Entity):
    """Represents a deleted item in the directory. When an item is deleted, it is added to the deleted items
    "container". Deleted items will remain available to restore for up to 30 days. After 30 days, the items are
    permanently deleted. """

    def deletedItems(self, entity_type=None):
        """Recently deleted items. Read-only. Nullable."""
        if entity_type:
            return DirectoryObjectCollection(self.context, ResourcePath(entity_type,
                                                                        ResourcePath("deletedItems",
                                                                                     self.resource_path)))
        else:
            return self.properties.get('deletedItems',
                                       DirectoryObjectCollection(self.context,
                                                                 ResourcePath("deletedItems", self.resource_path)))

    @property
    def deletedGroups(self):
        """Recently deleted groups"""
        return self.deletedItems("microsoft.graph.group")

    @property
    def deletedUsers(self):
        """Recently deleted users"""
        return self.deletedItems("microsoft.graph.user")

    @property
    def deletedApplications(self):
        """Recently deleted applications"""
        return self.deletedItems("microsoft.graph.application")
