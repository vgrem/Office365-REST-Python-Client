from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class PronounsSettings(Entity):
    @property
    def is_enabled_in_organization(self) -> Optional[bool]:
        """Gets the isEnabledInOrganization property"""
        return self.properties.get("isEnabledInOrganization", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PronounsSettings"
