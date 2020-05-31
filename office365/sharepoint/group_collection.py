from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import CreateEntityQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.runtime.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.group import Group


class GroupCollection(ClientObjectCollection):
    """Represents a collection of Group resources."""
    def __init__(self, context, resource_path=None):
        super(GroupCollection, self).__init__(context, Group, resource_path)

    def add(self, group_creation_information):
        """Creates a Group resource"""
        group = Group(self.context)
        self.add_child(group)
        qry = CreateEntityQuery(self, group_creation_information)
        self.context.add_query(qry)
        return group

    def get_by_id(self, group_id):
        """Returns the list item with the specified list item identifier."""
        group = Group(self.context,
                      ResourcePathServiceOperation("getbyid", [group_id], self.resource_path))
        return group

    def get_by_name(self, group_name):
        """Returns a cross-site group from the collection based on the name of the group."""
        return Group(self.context,
                     ResourcePathServiceOperation("getbyname", [group_name], self.resource_path))

    def remove_by_id(self, group_id):
        """Removes the group with the specified member ID from the collection."""
        qry = ServiceOperationQuery(self, "removebyid", [group_id])
        self.context.add_query(qry)

    def remove_by_login_name(self, group_name):
        """Removes the cross-site group with the specified name from the collection."""
        qry = ServiceOperationQuery(self, "removebyloginname", [group_name])
        self.context.add_query(qry)
