from office365.runtime.client_query import DeleteEntityQuery
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.principal.principal import Principal
from office365.sharepoint.principal.userIdInfo import UserIdInfo


class User(Principal):
    """Represents a user in Microsoft SharePoint Foundation. A user is a type of SP.Principal."""

    @property
    def groups(self):
        """Gets a collection of group objects that represents all of the groups for the user."""
        if self.is_property_available('Groups'):
            return self.properties['Groups']
        else:
            from office365.sharepoint.principal.group_collection import GroupCollection
            return GroupCollection(self.context, ResourcePath("Groups", self.resource_path))

    @property
    def is_site_admin(self):
        """Gets or sets a Boolean value that specifies whether the user is a site collection administrator."""
        if self.is_property_available('isSiteAdmin'):
            return self.properties['isSiteAdmin']
        else:
            return None

    @property
    def user_id(self):
        """Gets the information of the user that contains the user's name identifier and the issuer of the
         user's name identifier."""
        return self.properties.get('UserId', UserIdInfo())

    def delete_object(self):
        """Deletes the user."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()
