from office365.runtime.action_type import ActionType
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import ClientQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.group import Group


class GroupCollection(ClientObjectCollection):
    """Represents a collection of Group resources."""

    def add(self, group_creation_information):
        """Creates a Group resource"""
        group = Group(self.context)
        qry = ClientQuery(self.url, ActionType.CreateEntry, group_creation_information)
        self.context.add_query(qry, group)
        self.add_child(group)
        return group

    def get_by_id(self, group_id):
        """Returns the list item with the specified list item identifier."""
        group = Group(self.context,
                      ResourcePathServiceOperation(self.context, self.resource_path, "getbyid", [group_id]))
        return group

    def get_by_name(self, group_name):
        """Returns a cross-site group from the collection based on the name of the group."""
        return Group(self.context,
                     ResourcePathServiceOperation(self.context, self.resource_path, "getbyname", [group_name]))

    def remove_by_id(self, group_id):
        """Removes the group with the specified member ID from the collection."""
        qry = ClientQuery.service_operation_query(self, ActionType.PostMethod, "removebyid", [group_id])
        self.context.add_query(qry)

    def remove_by_login_name(self, group_name):
        """Removes the cross-site group with the specified name from the collection."""
        qry = ClientQuery.service_operation_query(self, ActionType.PostMethod, "removebyloginname", [group_name])
        self.context.add_query(qry)
