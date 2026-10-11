from __future__ import annotations

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection


class DeviceAndAppManagementRoleAssignment(Entity):
    @property
    def members(self) -> StringCollection:
        """Gets the members property"""
        return self.properties.get("members", StringCollection())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceAndAppManagementRoleAssignment"
