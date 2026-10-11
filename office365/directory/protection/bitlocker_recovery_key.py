from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.protection.volumetype import VolumeType


class BitlockerRecoveryKey(Entity):
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def device_id(self) -> Optional[str]:
        """Gets the deviceId property"""
        return self.properties.get("deviceId", None)

    @property
    def key(self) -> Optional[str]:
        """Gets the key property"""
        return self.properties.get("key", None)

    @property
    def volume_type(self) -> VolumeType:
        """Gets the volumeType property"""
        from office365.directory.protection.volumetype import VolumeType

        return self.properties.get("volumeType", VolumeType.operatingSystemVolume)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BitlockerRecoveryKey"
