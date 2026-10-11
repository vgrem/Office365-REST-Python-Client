from __future__ import annotations

from dataclasses import dataclass, field

from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_autopilot_devices_summary import (  # noqa: E501
    UserExperienceAnalyticsAutopilotDevicesSummary,
)
from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_cloud_identity_devices_summary import (  # noqa: E501
    UserExperienceAnalyticsCloudIdentityDevicesSummary,
)
from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_cloud_management_devices_summary import (  # noqa: E501
    UserExperienceAnalyticsCloudManagementDevicesSummary,
)
from office365.intune.devices.management.userexperienceanalytics.user_experience_analytics_windows10_devices_summary import (  # noqa: E501
    UserExperienceAnalyticsWindows10DevicesSummary,
)
from office365.runtime.client_value import ClientValue


@dataclass
class UserExperienceAnalyticsWorkFromAnywhereDevicesSummary(ClientValue):
    autopilotDevicesSummary: UserExperienceAnalyticsAutopilotDevicesSummary = field(
        default_factory=UserExperienceAnalyticsAutopilotDevicesSummary
    )
    cloudIdentityDevicesSummary: UserExperienceAnalyticsCloudIdentityDevicesSummary = field(
        default_factory=UserExperienceAnalyticsCloudIdentityDevicesSummary
    )
    cloudManagementDevicesSummary: UserExperienceAnalyticsCloudManagementDevicesSummary = field(
        default_factory=UserExperienceAnalyticsCloudManagementDevicesSummary
    )
    coManagedDevices: int | None = None
    devicesNotAutopilotRegistered: int | None = None
    devicesWithoutAutopilotProfileAssigned: int | None = None
    devicesWithoutCloudIdentity: int | None = None
    intuneDevices: int | None = None
    tenantAttachDevices: int | None = None
    totalDevices: int | None = None
    unsupportedOSversionDevices: int | None = None
    windows10Devices: int | None = None
    windows10DevicesSummary: UserExperienceAnalyticsWindows10DevicesSummary = field(
        default_factory=UserExperienceAnalyticsWindows10DevicesSummary
    )
    windows10DevicesWithoutTenantAttach: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserExperienceAnalyticsWorkFromAnywhereDevicesSummary"
