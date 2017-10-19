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

    @property
    def resource_path(self):
        orig_path = ClientObject.resource_path.fget(self)
        if self.is_property_available("Id") and orig_path is None:
            return ResourcePathEntry(self.context,
                                     self.context.web.site_groups.resource_path,
                                     ODataPathParser.from_method("GetById", [self.properties["Id"]]))
        if self.is_property_available("LoginName") and orig_path is None:
            return ResourcePathEntry(self.context,
                                     self.context.web.site_groups.resource_path,
                                     ODataPathParser.from_method("GetByName", [self.properties["LoginName"]]))
        return orig_path
