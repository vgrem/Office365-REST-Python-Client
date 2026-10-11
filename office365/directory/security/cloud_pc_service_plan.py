from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class CloudPcServicePlan(Entity):
    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def ram_in_gb(self) -> Optional[int]:
        """Gets the ramInGB property"""
        return self.properties.get("ramInGB", None)

    @property
    def storage_in_gb(self) -> Optional[int]:
        """Gets the storageInGB property"""
        return self.properties.get("storageInGB", None)

    @property
    def vcpu_count(self) -> Optional[int]:
        """Gets the vCpuCount property"""
        return self.properties.get("vCpuCount", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CloudPcServicePlan"
