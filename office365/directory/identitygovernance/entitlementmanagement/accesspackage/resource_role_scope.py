from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource_role import (
        AccessPackageResourceRole,
    )
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource_scope import (
        AccessPackageResourceScope,
    )


class AccessPackageResourceRoleScope(Entity):
    @property
    def created_date_time(self) -> datetime:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AccessPackageResourceRoleScope"

    @property
    def role(self) -> AccessPackageResourceRole:
        """Gets the role property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource_role import (
            AccessPackageResourceRole,
        )

        return self.properties.get(
            "role", AccessPackageResourceRole(self.context, ResourcePath("role", self.resource_path))
        )

    @property
    def scope(self) -> AccessPackageResourceScope:
        """Gets the scope property"""
        from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource_scope import (
            AccessPackageResourceScope,
        )

        return self.properties.get(
            "scope", AccessPackageResourceScope(self.context, ResourcePath("scope", self.resource_path))
        )
