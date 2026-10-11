from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.connection_info import ConnectionInfo
    from office365.directory.identitygovernance.entitlementmanagement.accesspackage.resource import (
        AccessPackageResource,
    )


class AccessPackageResourceEnvironment(Entity):
    @property
    def created_date_time(self) -> datetime:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def is_default_environment(self) -> Optional[bool]:
        """Gets the isDefaultEnvironment property"""
        return self.properties.get("isDefaultEnvironment", None)

    @property
    def modified_date_time(self) -> datetime:
        """Gets the modifiedDateTime property"""
        return self.properties.get("modifiedDateTime", datetime.min)

    @property
    def origin_id(self) -> Optional[str]:
        """Gets the originId property"""
        return self.properties.get("originId", None)

    @property
    def origin_system(self) -> Optional[str]:
        """Gets the originSystem property"""
        return self.properties.get("originSystem", None)

    @property
    def resources(self) -> EntityCollection[AccessPackageResource]:
        """Gets the resources property"""
        return self.properties.get(
            "resources",
            EntityCollection[AccessPackageResource](
                self.context, AccessPackageResource, ResourcePath("resources", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AccessPackageResourceEnvironment"

    @property
    def connection_info(self) -> ConnectionInfo:
        """Gets the connectionInfo property"""
        from office365.directory.connection_info import ConnectionInfo

        return self.properties.get("connectionInfo", ConnectionInfo())
