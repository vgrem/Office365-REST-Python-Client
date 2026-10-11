from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.unified_storage_quota import UnifiedStorageQuota


class StorageSettings(Entity):
    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.StorageSettings"

    @property
    def quota(self) -> UnifiedStorageQuota:
        """Gets the quota property"""
        from office365.directory.unified_storage_quota import UnifiedStorageQuota

        return self.properties.get("quota", UnifiedStorageQuota(self.context, ResourcePath("quota", self.resource_path)))
