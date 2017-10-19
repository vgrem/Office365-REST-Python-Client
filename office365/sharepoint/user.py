from office365.runtime.client_query import ClientQuery
from office365.sharepoint.principal import Principal
from office365.runtime.resource_path_entry import ResourcePathEntry


class User(Principal):
    """Represents a user in Microsoft SharePoint Foundation. A user is a type of SP.Principal."""

    @property
    def groups(self):
        from office365.sharepoint.group_collection import GroupCollection
        """Gets a collection of group objects that represents all of the groups for the user."""
        if self.is_property_available('Groups'):
            return self.properties['Groups']
        else:
            return GroupCollection(self.context, ResourcePathEntry(self.context, self.resource_path, "Groups"))

    def delete_object(self):
        """Deletes the user."""
        qry = ClientQuery.delete_entry_query(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()
