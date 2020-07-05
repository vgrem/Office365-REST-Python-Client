from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.permissions.roleAssignment import RoleAssignment


class RoleAssignmentCollection(ClientObjectCollection):
    """Represents a collection of RoleAssignment resources."""

    def __init__(self, context, resource_path=None):
        super(RoleAssignmentCollection, self).__init__(context, RoleAssignment, resource_path)

    def __getitem__(self, index_or_principal_id):
        """

        :param int or str index_or_principal_id: key is used to address a RoleAssignment resource by either an index
        in collection or by resource id
        """
        if type(index_or_principal_id) == int:
            return super(RoleAssignmentCollection, self).__getitem__(index_or_principal_id)
        return self._item_type(self.context,
                               ResourcePath(index_or_principal_id, self.resource_path))

    def get_by_principal_id(self):
        """Retrieves the role assignment object (1) based on the specified user or group."""
        pass

    def remove_role_assignment(self, principal_id, role_def_id):
        """Removes the role assignment with the specified principal and role definition from the collection.

        :param int role_def_id: The ID of the role definition in the role assignment.
        :param int principal_id: The ID of the user or group in the role assignment.
        """
        pass
