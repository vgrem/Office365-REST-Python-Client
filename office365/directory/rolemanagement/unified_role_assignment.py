from office365.directory.rolemanagement.unified_role_definition import UnifiedRoleDefinition
from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath


class UnifiedRoleAssignment(Entity):
    """
    A role assignment is used to grant access to resources. It represents a role definition assigned to a principal
    (for example, a user or a role-assignable group) at a particular scope.
    """

    @property
    def role_definition(self):
        """
        The roleDefinition the assignment is for. Supports $expand. roleDefinition.Id will be auto expanded.
        """
        return self.properties.get('roleDefinition',
                                   UnifiedRoleDefinition(self.context,
                                                         ResourcePath("roleDefinition", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "roleDefinition": self.role_definition,
            }
            default_value = property_mapping.get(name, None)
        return super(UnifiedRoleAssignment, self).get_property(name, default_value)
