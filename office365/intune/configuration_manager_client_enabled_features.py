from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class ConfigurationManagerClientEnabledFeatures(ClientValue):
    compliancePolicy: bool | None = None
    deviceConfiguration: bool | None = None
    inventory: bool | None = None
    modernApps: bool | None = None
    resourceAccess: bool | None = None
    windowsUpdateForBusiness: bool | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ConfigurationManagerClientEnabledFeatures"
