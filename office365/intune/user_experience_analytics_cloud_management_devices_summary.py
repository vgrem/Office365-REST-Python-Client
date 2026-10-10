from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class UserExperienceAnalyticsCloudManagementDevicesSummary(ClientValue):
    coManagedDeviceCount: int | None = None
    intuneDeviceCount: int | None = None
    tenantAttachDeviceCount: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserExperienceAnalyticsCloudManagementDevicesSummary"
