from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.sharepoint.entity import Entity


class FeatureDefinition(Entity):
    """Contains the base definition of a feature, including its name, ID, scope, and version."""

    def __str__(self):
        return self.display_name or self.entity_type_name

    @property
    def display_name(self) -> str | None:
        return self.properties.get("DisplayName", None)

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.SharePoint.Administration.FeatureDefinition"

    @property
    def id(self) -> Optional[UUID]:
        """Gets the Id property"""
        return self.properties.get("Id", None)
