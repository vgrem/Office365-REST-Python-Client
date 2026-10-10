from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class UserExperienceAnalyticsAutopilotDevicesSummary(ClientValue):
    devicesNotAutopilotRegistered: int | None = None
    devicesWithoutAutopilotProfileAssigned: int | None = None
    totalWindows10DevicesWithoutTenantAttached: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserExperienceAnalyticsAutopilotDevicesSummary"
