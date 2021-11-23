from office365.runtime.queries.create_entity_query import CreateEntityQuery
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.principal.group import Group


class GroupCollection(BaseEntityCollection):
    """Represents a collection of Group resources."""
    def __init__(self, context, resource_path=None):
        super(GroupCollection, self).__init__(context, Group, resource_path)

    def add(self, group_creation_information):
        """Creates a Group resource

        :type group_creation_information: any
        """
        group = Group(self.context)
        self.add_child(group)
        qry = CreateEntityQuery(self, group_creation_information, group)
        self.context.add_query(qry)
        return group

    def get_by_id(self, group_id):
        """Returns the list item with the specified list item identifier.

        :type group_id: str
        """
        return Group(self.context, ServiceOperationPath("GetById", [group_id], self.resource_path))

    def get_by_name(self, group_name):
        """Returns a cross-site group from the collection based on the name of the group.

        :type group_name: str
        """
        return Group(self.context,
                     ServiceOperationPath("GetByName", [group_name], self.resource_path))

    def remove_by_id(self, group_id):
        """Removes the group with the specified member ID from the collection.

        :type group_id: str
        """
        qry = ServiceOperationQuery(self, "RemoveById", [group_id])
        self.context.add_query(qry)
        return self

    def remove_by_login_name(self, group_name):
        """Removes the cross-site group with the specified name from the collection.

        :type group_name: str
        """
        qry = ServiceOperationQuery(self, "RemoveByLoginName", [group_name])
        self.context.add_query(qry)
        return self
