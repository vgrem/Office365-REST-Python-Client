from office365.graph.directory.directoryObjectCollection import DirectoryObjectCollection
from office365.graph.directory.user import User
from office365.runtime.client_query import CreateEntityQuery
from office365.runtime.resource_path import ResourcePath


class UserCollection(DirectoryObjectCollection):
    """User's collection"""

    def __init__(self, context, resource_path=None):
        super(UserCollection, self).__init__(context, resource_path)
        self._item_type = User

    def __getitem__(self, key):
        if type(key) == int:
            return self._data[key]
        return User(self.context, ResourcePath(key, self.resource_path))

    def add(self, user_properties):
        """Create a new user.

        :type user_properties: UserCreationProperties
        """
        usr = User(self.context)
        qry = CreateEntityQuery(self, user_properties, usr)
        self.context.add_query(qry)
        self.add_child(usr)
        return usr
