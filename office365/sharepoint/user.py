from office365.runtime.client_query import ClientQuery
from office365.runtime.odata.odata_path_parser import ODataPathParser
from office365.runtime.resource_path_entry import ResourcePathEntry
from office365.sharepoint.principal import Principal


class User(Principal):
    """Represents a user in Microsoft SharePoint Foundation. A user is a type of SP.Principal."""

    @property
    def groups(self):
        """Gets a collection of group objects that represents all of the groups for the user."""
        if self.is_property_available('Groups'):
            return self.properties['Groups']
        else:
            from office365.sharepoint.group_collection import GroupCollection
            return GroupCollection(self.context, ResourcePathEntry(self.context, self.resource_path, "Groups"))

    def delete_object(self):
        """Deletes the user."""
        qry = ClientQuery.delete_entry_query(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()

    @property
    def resource_path(self):
        resource_path = super(User, self).resource_path
        if resource_path:
            return resource_path

        # fallback: create a new resource path
        if self.is_property_available("Id"):
            self._resource_path = ResourcePathEntry(
                self.context,
                ResourcePathEntry.from_uri("Web/SiteUsers", self.context),
                ODataPathParser.from_method("GetById", [self.properties["Id"]]))
        elif self.is_property_available("LoginName"):
            self._resource_path = ResourcePathEntry(
                self.context,
                ResourcePathEntry.from_uri("Web/SiteUsers", self.context),
                ODataPathParser.from_method("GetByName", [self.properties["LoginName"]]))

        return self._resource_path
