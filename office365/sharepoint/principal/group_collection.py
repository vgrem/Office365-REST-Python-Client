from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.principal.group import Group
from office365.sharepoint.utilities.principal_info import PrincipalInfo


class GroupCollection(BaseEntityCollection):
    """Represents a collection of Group resources."""

    def __init__(self, context, resource_path=None):
        super(GroupCollection, self).__init__(context, Group, resource_path)

    def expand_to_principals(self, max_count):
        """
        Expands groups to a collection of principals.

        :param int max_count: Specifies the maximum number of principals to be returned.
        """
        return_type = ClientResult(self.context, ClientValueCollection(PrincipalInfo))
        for cur_grp in self:  # type: Group
            return_type = cur_grp.expand_to_principals(max_count)
        return return_type

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

        :param str group_id: Specifies the member identifier.
        """
        return Group(self.context, ServiceOperationPath("GetById", [group_id], self.resource_path))

    def get_by_name(self, group_name):
        """Returns a cross-site group from the collection based on the name of the group.

        :param str group_name: A string that contains the name of the group.
        """
        return Group(self.context,
                     ServiceOperationPath("GetByName", [group_name], self.resource_path))

    def remove_by_id(self, group_id):
        """Removes the group with the specified member ID from the collection.

        :param str group_id: Specifies the member identifier.
        """
        qry = ServiceOperationQuery(self, "RemoveById", [group_id])
        self.context.add_query(qry)
        return self

    def remove_by_login_name(self, group_name):
        """Removes the cross-site group with the specified name from the collection.

        :param str group_name:  A string that contains the name of the group.
        """
        qry = ServiceOperationQuery(self, "RemoveByLoginName", [group_name])
        self.context.add_query(qry)
        return self
