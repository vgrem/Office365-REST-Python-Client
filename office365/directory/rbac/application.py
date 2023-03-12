from office365.directory.rbac.unified_role_assignment import UnifiedRoleAssignment
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath


class RbacApplication(Entity):
    """Role management container for unified role definitions and role assignments for Microsoft 365 role-based
    access control (RBAC) providers. The role assignments support only a single principal and a single scope.
    Currently directory and entitlementManagement are the two RBAC providers supported."""

    @property
    def role_assignments(self):
        """Resource to grant access to users or groups."""
        return self.properties.get('roleAssignments',
                                   EntityCollection(self.context, UnifiedRoleAssignment,
                                                    ResourcePath("roleAssignments", self.resource_path)))

