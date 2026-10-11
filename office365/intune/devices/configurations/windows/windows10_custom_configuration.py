from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.intune.devices.configurations.oma_setting import OmaSetting


class Windows10CustomConfiguration(Entity):
    @property
    def oma_settings(self) -> ClientValueCollection[OmaSetting]:
        """Gets the omaSettings property"""
        from office365.intune.devices.configurations.oma_setting import OmaSetting

        return self.properties.get("omaSettings", ClientValueCollection[OmaSetting](OmaSetting))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Windows10CustomConfiguration"
