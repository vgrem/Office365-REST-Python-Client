from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class UserExperienceAnalyticsMetric(Entity):
    @property
    def unit(self) -> Optional[str]:
        """Gets the unit property"""
        return self.properties.get("unit", None)

    @property
    def value(self) -> Optional[float]:
        """Gets the value property"""
        return self.properties.get("value", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserExperienceAnalyticsMetric"
