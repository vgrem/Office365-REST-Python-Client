from client.client_object_collection import ClientObjectCollection
from client.group import Group
from client.runtime.client_query import ClientQuery


class GroupCollection(ClientObjectCollection):
    """Represents a collection of Group resources."""

    def add(self, group_creation_information):
        """Creates a Group resource"""
        group = Group(self.context)
        qry = ClientQuery.create_create_query(self.url, group_creation_information)
        self.context.add_query(qry, group)
        self.add_child(group)
        return group

    def get_by_id(self, group_id):
        """Returns the list item with the specified list item identifier."""
        group = Group(self.context, "getbyid('{0}')".format(group_id), self.resource_path)
        return group

    def get_by_name(self, group_name):
        """Returns a cross-site group from the collection based on the name of the group."""
        return Group(self.context, "getbyname('{0}')".format(group_name), self.resource_path)

    def remove_by_id(self, group_id):
        """Removes the group with the specified member ID from the collection."""
        qry = ClientQuery.create_delete_query(self, self.url + "/removebyid('{0}')".format(group_id))
        self.context.add_query(qry)

    def remove_by_login_name(self, group_name):
        """Removes the cross-site group with the specified name from the collection."""
        qry = ClientQuery.create_delete_query(self, self.url + "/removebyloginname('{0}')".format(group_name))
        self.context.add_query(qry)
