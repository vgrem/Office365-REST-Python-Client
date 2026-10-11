from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class AdminReportSettings(Entity):
    """Represents the tenant-level settings for Microsoft 365 reports."""

    @property
    def display_concealed_names(self) -> Optional[bool]:
        """Gets the displayConcealedNames property"""
        return self.properties.get("displayConcealedNames", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AdminReportSettings"
