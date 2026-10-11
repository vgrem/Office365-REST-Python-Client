from __future__ import annotations

from dataclasses import dataclass, field

from office365.common.setting_source import SettingSource
from office365.intune.devices.compliance.status import ComplianceStatus
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


@dataclass
class DeviceCompliancePolicySettingState(ClientValue):
    currentValue: str | None = None
    errorCode: int | None = None
    errorDescription: str | None = None
    instanceDisplayName: str | None = None
    setting: str | None = None
    settingName: str | None = None
    sources: ClientValueCollection[SettingSource] = field(default_factory=lambda: ClientValueCollection(SettingSource))
    state: ComplianceStatus = ComplianceStatus.unknown
    userEmail: str | None = None
    userId: str | None = None
    userName: str | None = None
    userPrincipalName: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceCompliancePolicySettingState"
