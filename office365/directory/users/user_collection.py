from office365.directory.users.user import User
from office365.entity_collection import EntityCollection
from office365.runtime.queries.create_entity_query import CreateEntityQuery


class UserCollection(EntityCollection):
    """User's collection"""

    def __init__(self, context, resource_path=None):
        super(UserCollection, self).__init__(context, User, resource_path)

    def add(self, user_properties):
        """Create a new user.

        :type user_properties: UserProfile
        """
        usr = User(self.context)
        qry = CreateEntityQuery(self, user_properties, usr)
        self.context.add_query(qry)
        self.add_child(usr)
        return usr
