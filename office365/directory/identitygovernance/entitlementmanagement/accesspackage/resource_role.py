from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource import (
        AccessPackageResource,
    )
    from office365.directory.role_type import RoleType


class AccessPackageResourceRole(Entity):
    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def origin_id(self) -> Optional[str]:
        """Gets the originId property"""
        return self.properties.get("originId", None)

    @property
    def origin_system(self) -> Optional[str]:
        """Gets the originSystem property"""
        return self.properties.get("originSystem", None)

    @property
    def resource(self) -> AccessPackageResource:
        """Gets the resource property"""
        return self.properties.get(
            "resource", AccessPackageResource(self.context, ResourcePath("resource", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AccessPackageResourceRole"

    @property
    def type(self) -> RoleType:
        """Gets the type property"""
        from office365.directory.role_type import RoleType

        return self.properties.get("type", RoleType.active)
