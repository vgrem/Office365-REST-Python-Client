from office365.runtime.odata.odata_path_parser import ODataPathParser
from office365.runtime.resource_path_entry import ResourcePathEntry
from office365.sharepoint.principal import Principal


class Group(Principal):
    """Represents a collection of users in a SharePoint site. A group is a type of SP.Principal."""

    @property
    def users(self):
        """Gets a collection of user objects that represents all of the users in the group."""
        from office365.sharepoint.user_collection import UserCollection
        if self.is_property_available('Users'):
            return self.properties['Users']
        else:
            return UserCollection(self.context, ResourcePathEntry(self.context, self.resource_path, "Users"))

    @property
    def resource_path(self):
        resource_path = super(Group, self).resource_path
        if resource_path:
            return resource_path

        # fallback: create a new resource path
        if self.is_property_available("Id"):
            self._resource_path = ResourcePathEntry(
                self.context,
                ResourcePathEntry.from_uri("Web/SiteGroups", self.context),
                ODataPathParser.from_method("GetById", [self.properties["Id"]]))
        elif self.is_property_available("LoginName"):
            self._resource_path = ResourcePathEntry(
                self.context,
                ResourcePathEntry.from_uri("Web/SiteGroups", self.context),
                ODataPathParser.from_method("GetByName", [self.properties["LoginName"]]))

        return self._resource_path
