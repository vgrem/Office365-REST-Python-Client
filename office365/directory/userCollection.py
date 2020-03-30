from office365.directory.user import User
from office365.directory.directoryObjectCollection import DirectoryObjectCollection
from office365.runtime.client_query import CreateEntityQuery


class UserCollection(DirectoryObjectCollection):
    """User's collection"""

    def __init__(self, context, resource_path=None):
        super(UserCollection, self).__init__(context, User, resource_path)

    def add(self, user_properties):
        """Create a new user."""
        usr = User(self.context)
        qry = CreateEntityQuery(self, user_properties, usr)
        self.context.add_query(qry)
        self.add_child(usr)
        return usr
