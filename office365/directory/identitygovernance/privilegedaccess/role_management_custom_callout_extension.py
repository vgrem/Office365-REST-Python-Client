from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.directory.identitygovernance.custom_callout_extension_type import (
        CustomCalloutExtensionType,
    )
    from office365.directory.identitygovernance.custom_extension_resource_type import (
        CustomExtensionResourceType,
    )


class RoleManagementCustomCalloutExtension(Entity):
    @property
    def custom_attributes(self) -> StringCollection:
        """Gets the customAttributes property"""
        return self.properties.get("customAttributes", StringCollection())

    @property
    def resource_type(self) -> CustomExtensionResourceType:
        """Gets the resourceType property"""
        from office365.directory.identitygovernance.custom_extension_resource_type import (
            CustomExtensionResourceType,
        )

        return self.properties.get("resourceType", CustomExtensionResourceType.entraRoles)

    @property
    def type(self) -> CustomCalloutExtensionType:
        """Gets the type property"""
        from office365.directory.identitygovernance.custom_callout_extension_type import (
            CustomCalloutExtensionType,
        )

        return self.properties.get("type", CustomCalloutExtensionType.preApproval)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RoleManagementCustomCalloutExtension"
