from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.copilot.admin_limited_mode import CopilotAdminLimitedMode


class CopilotAdminSetting(Entity):
    @property
    def limited_mode(self) -> CopilotAdminLimitedMode:
        """Gets the limitedMode property"""
        from office365.copilot.admin_limited_mode import CopilotAdminLimitedMode

        return self.properties.get(
            "limitedMode", CopilotAdminLimitedMode(self.context, ResourcePath("limitedMode", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CopilotAdminSetting"
