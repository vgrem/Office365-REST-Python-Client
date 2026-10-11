from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class CopilotAdminLimitedMode(Entity):
    @property
    def group_id(self) -> Optional[str]:
        """Gets the groupId property"""
        return self.properties.get("groupId", None)

    @property
    def is_enabled_for_group(self) -> Optional[bool]:
        """Gets the isEnabledForGroup property"""
        return self.properties.get("isEnabledForGroup", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CopilotAdminLimitedMode"
