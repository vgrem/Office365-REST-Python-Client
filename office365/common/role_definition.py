from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.role_assignment import RoleAssignment
    from office365.directory.rolemanagement.roles.permission import RolePermission


class RoleDefinition(Entity):
    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def is_built_in(self) -> Optional[bool]:
        """Gets the isBuiltIn property"""
        return self.properties.get("isBuiltIn", None)

    @property
    def role_permissions(self) -> ClientValueCollection[RolePermission]:
        """Gets the rolePermissions property"""
        from office365.directory.rolemanagement.roles.permission import RolePermission

        return self.properties.get("rolePermissions", ClientValueCollection[RolePermission](RolePermission))

    @property
    def role_assignments(self) -> EntityCollection[RoleAssignment]:
        """Gets the roleAssignments property"""
        from office365.common.role_assignment import RoleAssignment

        return self.properties.get(
            "roleAssignments",
            EntityCollection[RoleAssignment](
                self.context, RoleAssignment, ResourcePath("roleAssignments", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RoleDefinition"
