from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.intune.devices.compliance.status import ComplianceStatus


@dataclass
class DeviceCompliancePolicySettingState(ClientValue):
    currentValue: str | None = None
    errorCode: int | None = None
    errorDescription: str | None = None
    instanceDisplayName: str | None = None
    setting: str | None = None
    settingName: str | None = None
    state: ComplianceStatus = ComplianceStatus.unknown
    userEmail: str | None = None
    userId: str | None = None
    userName: str | None = None
    userPrincipalName: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceCompliancePolicySettingState"
