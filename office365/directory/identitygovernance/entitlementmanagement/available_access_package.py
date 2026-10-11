from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource_role_scope import (
        AccessPackageResourceRoleScope,
    )


class AvailableAccessPackage(Entity):
    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def resource_role_scopes(self) -> EntityCollection[AccessPackageResourceRoleScope]:
        """Gets the resourceRoleScopes property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource_role_scope import (
            AccessPackageResourceRoleScope,
        )

        return self.properties.get(
            "resourceRoleScopes",
            EntityCollection[AccessPackageResourceRoleScope](
                self.context, AccessPackageResourceRoleScope, ResourcePath("resourceRoleScopes", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AvailableAccessPackage"
