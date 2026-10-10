from __future__ import annotations

from dataclasses import dataclass

from office365.intune.devices.compliance.mdmappconfigkeytype import MdmAppConfigKeyType
from office365.runtime.client_value import ClientValue


@dataclass
class AppConfigurationSettingItem(ClientValue):
    appConfigKey: str | None = None
    appConfigKeyType: MdmAppConfigKeyType = MdmAppConfigKeyType.stringType
    appConfigKeyValue: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AppConfigurationSettingItem"
