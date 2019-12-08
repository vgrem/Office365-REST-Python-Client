from office365.runtime.client_query import ClientQuery, DeleteEntityQuery
from office365.runtime.resource_path_entity import ResourcePathEntity
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
            return GroupCollection(self.context, ResourcePathEntity(self.context, self.resource_path, "Groups"))

    def delete_object(self):
        """Deletes the user."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()
