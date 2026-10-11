from __future__ import annotations

from typing import Optional

from office365.entity import Entity


class WindowsUniversalAppXContainedApp(Entity):
    @property
    def app_user_model_id(self) -> Optional[str]:
        """Gets the appUserModelId property"""
        return self.properties.get("appUserModelId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsUniversalAppXContainedApp"
