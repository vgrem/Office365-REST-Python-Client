from office365.runtime.client_object import ClientObject
from office365.runtime.odata.odata_path_parser import ODataPathParser
from office365.sharepoint.principal import Principal
from office365.runtime.resource_path_entry import ResourcePathEntry


class Group(Principal):
    """Represents a collection of users in a SharePoint site. A group is a type of SP.Principal."""

    @property
    def users(self):
        from office365.sharepoint.user_collection import UserCollection
        """Gets a collection of user objects that represents all of the users in the group."""
        if self.is_property_available('Users'):
            return self.properties['Users']
        else:
            return UserCollection(self.context, ResourcePathEntry(self.context, self.resource_path, "Users"))
