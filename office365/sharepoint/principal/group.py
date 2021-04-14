from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.principal.principal import Principal


class Group(Principal):
    """Represents a collection of users in a SharePoint site. A group is a type of SP.Principal."""

    @property
    def owner_title(self):
        """Specifies the name of the owner of the group.
        :rtype: str or None
        """
        return self.properties.get('OwnerTitle', None)

    @property
    def can_current_user_manage_group(self):
        """Gets a Boolean value that indicates whether the current user can manage the group.

        :rtype: bool or None
        """
        return self.properties.get('CanCurrentUserManageGroup', None)

    @property
    def owner(self):
        """Specifies the owner of the group."""
        return self.properties.get('Owner', Principal(self.context, ResourcePath("Owner", self.resource_path)))

    @property
    def users(self):
        """Gets a collection of user objects that represents all of the users in the group."""
        from office365.sharepoint.principal.user_collection import UserCollection
        return self.properties.get('Users', UserCollection(self.context, ResourcePath("Users", self.resource_path)))
