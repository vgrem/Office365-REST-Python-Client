from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.serviceprincipals.approved_client_app import (
        ApprovedClientApp,
    )
    from office365.directory.serviceprincipals.target_device_group import (
        TargetDeviceGroup,
    )


class RemoteDesktopSecurityConfiguration(Entity):
    @property
    def is_remote_desktop_protocol_enabled(self) -> Optional[bool]:
        """Gets the isRemoteDesktopProtocolEnabled property"""
        return self.properties.get("isRemoteDesktopProtocolEnabled", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RemoteDesktopSecurityConfiguration"

    @property
    def approved_client_apps(self) -> EntityCollection[ApprovedClientApp]:
        """Gets the approvedClientApps property"""
        from office365.directory.serviceprincipals.approved_client_app import (
            ApprovedClientApp,
        )

        return self.properties.get(
            "approvedClientApps",
            EntityCollection[ApprovedClientApp](
                self.context, ApprovedClientApp, ResourcePath("approvedClientApps", self.resource_path)
            ),
        )

    @property
    def target_device_groups(self) -> EntityCollection[TargetDeviceGroup]:
        """Gets the targetDeviceGroups property"""
        from office365.directory.serviceprincipals.target_device_group import (
            TargetDeviceGroup,
        )

        return self.properties.get(
            "targetDeviceGroups",
            EntityCollection[TargetDeviceGroup](
                self.context, TargetDeviceGroup, ResourcePath("targetDeviceGroups", self.resource_path)
            ),
        )
