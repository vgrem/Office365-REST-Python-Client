from office365.directory.user import User
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.resource_path_entity import ResourcePathEntity


class DirectoryObjectCollection(ClientObjectCollection):
    """User's collection"""

    def __getitem__(self, key):
        return User(self.context,
                    ResourcePathEntity(self.context, self.resourcePath, key))
