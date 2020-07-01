from office365.runtime.client_object_collection import ClientObjectCollection


class RoleAssignmentCollection(ClientObjectCollection):
    """Represents a collection of RoleAssignment resources."""

    def remove_role_assignment(self, principal_id, role_def_id):
        """Removes the role assignment with the specified principal and role definition from the collection.

        :param int role_def_id: The ID of the role definition in the role assignment.
        :param int principal_id: The ID of the user or group in the role assignment.
        """
        pass
