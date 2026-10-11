from __future__ import annotations

from typing import Optional

from office365.entity import Entity
from office365.runtime.types.collections import GuidCollection


class OnPremisesConditionalAccessSettings(Entity):
    @property
    def enabled(self) -> Optional[bool]:
        """Gets the enabled property"""
        return self.properties.get("enabled", None)

    @property
    def excluded_groups(self) -> GuidCollection:
        """Gets the excludedGroups property"""
        return self.properties.get("excludedGroups", GuidCollection())

    @property
    def included_groups(self) -> GuidCollection:
        """Gets the includedGroups property"""
        return self.properties.get("includedGroups", GuidCollection())

    @property
    def override_default_rule(self) -> Optional[bool]:
        """Gets the overrideDefaultRule property"""
        return self.properties.get("overrideDefaultRule", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OnPremisesConditionalAccessSettings"
