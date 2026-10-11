from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.management.detectedappplatformtype import (
        DetectedAppPlatformType,
    )
    from office365.intune.devices.management.managed.managed import ManagedDevice


class DetectedApp(Entity):
    @property
    def device_count(self) -> Optional[int]:
        """Gets the deviceCount property"""
        return self.properties.get("deviceCount", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def platform(self) -> DetectedAppPlatformType:
        """Gets the platform property"""
        from office365.intune.devices.management.detectedappplatformtype import (
            DetectedAppPlatformType,
        )

        return self.properties.get("platform", DetectedAppPlatformType.unknown)

    @property
    def publisher(self) -> Optional[str]:
        """Gets the publisher property"""
        return self.properties.get("publisher", None)

    @property
    def size_in_byte(self) -> Optional[int]:
        """Gets the sizeInByte property"""
        return self.properties.get("sizeInByte", None)

    @property
    def version(self) -> Optional[str]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def managed_devices(self) -> EntityCollection[ManagedDevice]:
        """Gets the managedDevices property"""
        from office365.intune.devices.management.managed.managed import ManagedDevice

        return self.properties.get(
            "managedDevices",
            EntityCollection[ManagedDevice](
                self.context, ManagedDevice, ResourcePath("managedDevices", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DetectedApp"
