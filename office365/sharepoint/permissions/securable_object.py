from office365.runtime.client_result import ClientResult
from office365.runtime.queries.serviceOperationQuery import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.permissions.basePermissions import BasePermissions
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.permissions.roleAssignmentCollection import RoleAssignmentCollection


class SecurableObject(BaseEntity):
    """An object that can be assigned security permissions."""

    def break_role_inheritance(self, copyRoleAssignments=True, clearSubscopes=True):
        """Creates unique role assignments for the securable object. If the securable object already has
        unique role assignments, the protocol server MUST NOT alter any role assignments.

        :param bool clearSubscopes:  If the securable object is a site (2), and the clearSubscopes parameter is "true",
        the role assignments for all child securable objects in the current site (2) and in the sites (2) that inherit
        role assignments from the current site (2) MUST be cleared and those securable objects inherit role assignments
        from the current site (2) after this call. If the securable object is a site (2), and the clearSubscopes
        parameter is "false", the role assignments for all child securable objects that do not inherit role assignments
        from their parent object (1) MUST remain unchanged. If the securable object is not a site (2), and the
        clearSubscopes parameter is "true", the role assignments for all child securable objects MUST be cleared and
        those securable objects inherit role assignments from the current securable object after this call. If the
        securable object is not a site (2), and the clearSubscopes parameter is "false", the role assignments for all
        child securable objects that do not inherit role assignments from their parent object (1) MUST remain unchanged.
        :param bool copyRoleAssignments: Specifies whether to copy the role assignments from
        the parent securable object.If the value is "false", the collection of role assignments MUST contain
        only 1 role assignment containing the current user after the operation.

        """
        payload = {
            "copyRoleAssignments" : copyRoleAssignments,
            "clearSubscopes": clearSubscopes
        }
        qry = ServiceOperationQuery(self, "breakRoleInheritance", None, payload, None, None)
        self.context.add_query(qry)

    def reset_role_inheritance(self):
        """Resets the role inheritance for the securable object and inherits role assignments from
        the parent securable object."""
        qry = ServiceOperationQuery(self, "resetRoleInheritance", None, None, None, None)
        self.context.add_query(qry)

    def get_user_effective_permissions(self, user_name):
        """
        Returns the user permissions for this list.

        :param str user_name: Specifies the user login name.
        """
        result = ClientResult(BasePermissions())
        qry = ServiceOperationQuery(self, "getUserEffectivePermissions", [user_name], None, None, result)
        self.context.add_query(qry)
        return result

    @property
    def hasUniqueRoleAssignments(self):
        """Specifies whether the role assignments are uniquely defined for this securable object or inherited from a
        parent securable object. If the value is "false", role assignments are inherited from a parent securable
        object.
        """
        return self.properties.get("HasUniqueRoleAssignments", None)

    @property
    def firstUniqueAncestorSecurableObject(self):
        """Specifies the object where role assignments for this object are defined.<85>."""
        return self.properties.get("FirstUniqueAncestorSecurableObject",
                                   SecurableObject(self.context,
                                                   ResourcePath("FirstUniqueAncestorSecurableObject",
                                                                self.resource_path)))

    @property
    def roleAssignments(self):
        """The role assignments for the securable object."""
        return self.properties.get("RoleAssignments",
                                   RoleAssignmentCollection(self.context,
                                                            ResourcePath("RoleAssignments", self.resource_path)))
