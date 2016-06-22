from client.principal import Principal
from client.user_collection import UserCollection


class Group(Principal):
    """Represents a collection of users in a SharePoint site. A group is a type of SP.Principal."""

    @property
    def users(self):
        """Gets a collection of user objects that represents all of the users in the group."""
        if self.is_property_available('Users'):
            return self.properties['Users']
        else:
            return UserCollection(self.context, "users", self.resource_path)
