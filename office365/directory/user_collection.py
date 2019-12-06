from office365.directory.user import User
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.resource_path_entity import ResourcePathEntity


class UserCollection(ClientObjectCollection):
    """User's collection"""

    def __init__(self, context, resource_path=None):
        super(UserCollection, self).__init__(context, User, resource_path)

    def __getitem__(self, key):
        return User(self.context,
                    ResourcePathEntity(self.context, self.resource_path, key))
