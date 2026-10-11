from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.intune.devices.management.mobileapps.app_configuration_setting_item import (
        AppConfigurationSettingItem,
    )


class IosMobileAppConfiguration(Entity):
    @property
    def encoded_setting_xml(self) -> Optional[bytes]:
        """Gets the encodedSettingXml property"""
        return self.properties.get("encodedSettingXml", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IosMobileAppConfiguration"

    @property
    def settings(self) -> ClientValueCollection[AppConfigurationSettingItem]:
        """Gets the settings property"""
        from office365.intune.devices.management.mobileapps.app_configuration_setting_item import (
            AppConfigurationSettingItem,
        )

        return self.properties.get(
            "settings", ClientValueCollection[AppConfigurationSettingItem](AppConfigurationSettingItem)
        )
