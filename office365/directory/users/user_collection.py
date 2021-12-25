from office365.directory.users.user import User
from office365.entity_collection import DeltaCollection
from office365.runtime.queries.create_entity_query import CreateEntityQuery


class UserCollection(DeltaCollection):
    """User's collection"""

    def __init__(self, context, resource_path=None):
        super(UserCollection, self).__init__(context, User, resource_path)

    def add(self, user_properties):
        """Create a new user.

        :type user_properties: office365.directory.users.user_profile.UserProfile
        """
        return_type = User(self.context)
        qry = CreateEntityQuery(self, user_properties, return_type)
        self.context.add_query(qry)
        self.add_child(return_type)
        return return_type
