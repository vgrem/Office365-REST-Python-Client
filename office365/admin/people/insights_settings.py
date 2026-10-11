from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class InsightsSettings(Entity):
    @property
    def disabled_for_group(self) -> Optional[str]:
        """Gets the disabledForGroup property"""
        return self.properties.get("disabledForGroup", None)

    @property
    def is_enabled_in_organization(self) -> Optional[bool]:
        """Gets the isEnabledInOrganization property"""
        return self.properties.get("isEnabledInOrganization", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.InsightsSettings"
