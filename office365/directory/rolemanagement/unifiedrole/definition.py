from __future__ import annotations

from typing import Optional

from office365.directory.rolemanagement.unifiedrole.permission import (
    UnifiedRolePermission,
)
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata


class UnifiedRoleDefinition(Entity):
    """A role definition is a collection of permissions in Azure Active Directory (Azure AD) listing the operations
    that can be performed and the resources against which they can performed."""

    def __str__(self):
        return self.display_name or self.entity_type_name

    @property
    def display_name(self) -> Optional[str]:
        """The display name for the unifiedRoleDefinition."""
        return self.properties.get("displayName", None)

    @property
    def is_built_in(self) -> Optional[bool]:
        """Flag indicating whether the role definition is part of the default set included in
        Azure Active Directory (Azure AD) or a custom definition.
        """
        return self.properties.get("isBuiltIn", None)

    @odata(name="rolePermissions")
    @property
    def role_permissions(self) -> ClientValueCollection[UnifiedRolePermission]:
        """
        List of permissions included in the role. Read-only when isBuiltIn is true. Required.
        """
        return self.properties.get("rolePermissions", ClientValueCollection(UnifiedRolePermission))

    @odata(name="inheritsPermissionsFrom")
    @property
    def inherits_permissions_from(self) -> EntityCollection[UnifiedRoleDefinition]:
        """
        Read-only collection of role definitions that the given role definition inherits from. Only Azure AD built-in
        roles (isBuiltIn is true) support this attribute. Supports $expand.
        """
        return self.properties.get(
            "inheritsPermissionsFrom",
            EntityCollection(
                self.context,
                UnifiedRoleDefinition,
                ResourcePath("inheritsPermissionsFrom", self.resource_path),
            ),
        )

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def is_enabled(self) -> Optional[bool]:
        """Gets the isEnabled property"""
        return self.properties.get("isEnabled", None)

    @property
    def resource_scopes(self) -> StringCollection:
        """Gets the resourceScopes property"""
        return self.properties.get("resourceScopes", StringCollection())

    @property
    def template_id(self) -> Optional[str]:
        """Gets the templateId property"""
        return self.properties.get("templateId", None)

    @property
    def version(self) -> Optional[str]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRoleDefinition"
