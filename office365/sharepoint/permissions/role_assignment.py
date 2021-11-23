from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.permissions.roleDefinitionCollection import RoleDefinitionCollection
from office365.sharepoint.principal.principal import Principal


class RoleAssignment(BaseEntity):
    """An association between a principal or a site group and a role definition."""

    @property
    def principal_id(self):
        """"""
        return self.properties.get("PrincipalId", None)

    @property
    def member(self):
        """Specifies the user or group corresponding to the role assignment."""
        return self.properties.get("Member",
                                   Principal(self.context, ResourcePath("Member", self.resource_path)))

    @property
    def role_definition_bindings(self):
        """Specifies a collection of role definitions for this role assignment."""
        return self.properties.get("RoleDefinitionBindings",
                                   RoleDefinitionCollection(self.context,
                                                            ResourcePath("RoleDefinitionBindings",
                                                                         self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "RoleDefinitionBindings": self.role_definition_bindings,
            }
            default_value = property_mapping.get(name, None)
        return super(RoleAssignment, self).get_property(name, default_value)
