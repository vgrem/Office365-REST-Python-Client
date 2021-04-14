from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.permissions.roleDefinitionCollection import RoleDefinitionCollection
from office365.sharepoint.principal.principal import Principal


class RoleAssignment(BaseEntity):
    """An association between a principal or a site group and a role definition."""

    @property
    def principalId(self):
        """"""
        return self.properties.get("PrincipalId", None)

    @property
    def member(self):
        """Specifies the user or group corresponding to the role assignment."""
        return self.properties.get("Member",
                                   Principal(self.context, ResourcePath("Member", self.resource_path)))

    @property
    def roleDefinitionBindings(self):
        """Specifies a collection of role definitions for this role assignment."""
        return self.properties.get("RoleDefinitionBindings",
                                   RoleDefinitionCollection(self.context,
                                                            ResourcePath("RoleDefinitionBindings",
                                                                         self.resource_path)))
