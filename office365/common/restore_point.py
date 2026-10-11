from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.backuprestore.protection_unit_base import ProtectionUnitBase
    from office365.backuprestore.restorepoints.tags import RestorePointTags


class RestorePoint(Entity):
    @property
    def expiration_date_time(self) -> Optional[datetime]:
        """Gets the expirationDateTime property"""
        return self.properties.get("expirationDateTime", datetime.min)

    @property
    def protection_date_time(self) -> Optional[datetime]:
        """Gets the protectionDateTime property"""
        return self.properties.get("protectionDateTime", datetime.min)

    @property
    def tags(self) -> RestorePointTags:
        """Gets the tags property"""
        from office365.backuprestore.restorepoints.tags import RestorePointTags

        return self.properties.get("tags", RestorePointTags.none)

    @property
    def protection_unit(self) -> ProtectionUnitBase:
        """Gets the protectionUnit property"""
        from office365.backuprestore.protection_unit_base import ProtectionUnitBase

        return self.properties.get(
            "protectionUnit", ProtectionUnitBase(self.context, ResourcePath("protectionUnit", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RestorePoint"
