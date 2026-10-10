from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class ConditionalAccessPolicy(Entity):
    @property
    def conditions(self) -> Optional[str]:
        """Gets the conditions property"""
        return self.properties.get("conditions", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def grant_controls(self) -> Optional[str]:
        """Gets the grantControls property"""
        return self.properties.get("grantControls", None)

    @property
    def id_(self) -> Optional[str]:
        """Gets the id property"""
        return self.properties.get("id", None)

    @property
    def session_controls(self) -> Optional[str]:
        """Gets the sessionControls property"""
        return self.properties.get("sessionControls", None)

    @property
    def state(self) -> Optional[str]:
        """Gets the state property"""
        return self.properties.get("state", None)

    @property
    def template_id(self) -> Optional[str]:
        """Gets the templateId property"""
        return self.properties.get("templateId", None)

    @property
    def entity_type_name(self) -> str:
        return "SP.Directory.ConditionalAccessPolicy"

    @property
    def id(self) -> Optional[str]:
        """Gets the id property"""
        return self.properties.get("id", None)
