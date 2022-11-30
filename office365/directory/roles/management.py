from office365.directory.rbac.application import RbacApplication
from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath


class RoleManagement(Entity):
    """
    Represents a Microsoft 365 role-based access control (RBAC) role management entity.
    This resource provides access to role definitions and role assignments surfaced from RBAC providers.
    directory (Azure Active Directory), entitlementManagement, and deviceManagement (Intune) providers
    are currently supported.
    """

    @property
    def directory(self):
        return self.properties.get('directory',
                                   RbacApplication(self.context, ResourcePath("directory", self.resource_path)))
