from office365.entity import Entity


class RbacApplication(Entity):
    """Role management container for unified role definitions and role assignments for Microsoft 365 role-based
    access control (RBAC) providers. The role assignments support only a single principal and a single scope.
    Currently directory and entitlementManagement are the two RBAC providers supported."""
