from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.management.userexperienceanalytics.healthstate import (
        UserExperienceAnalyticsHealthState,
    )


class UserExperienceAnalyticsWorkFromAnywhereModelPerformance(Entity):
    @property
    def cloud_identity_score(self) -> Optional[float]:
        """Gets the cloudIdentityScore property"""
        return self.properties.get("cloudIdentityScore", None)

    @property
    def cloud_management_score(self) -> Optional[float]:
        """Gets the cloudManagementScore property"""
        return self.properties.get("cloudManagementScore", None)

    @property
    def cloud_provisioning_score(self) -> Optional[float]:
        """Gets the cloudProvisioningScore property"""
        return self.properties.get("cloudProvisioningScore", None)

    @property
    def health_status(self) -> UserExperienceAnalyticsHealthState:
        """Gets the healthStatus property"""
        from office365.intune.devices.management.userexperienceanalytics.healthstate import (
            UserExperienceAnalyticsHealthState,
        )

        return self.properties.get("healthStatus", UserExperienceAnalyticsHealthState.unknown)

    @property
    def manufacturer(self) -> Optional[str]:
        """Gets the manufacturer property"""
        return self.properties.get("manufacturer", None)

    @property
    def model(self) -> Optional[str]:
        """Gets the model property"""
        return self.properties.get("model", None)

    @property
    def model_device_count(self) -> Optional[int]:
        """Gets the modelDeviceCount property"""
        return self.properties.get("modelDeviceCount", None)

    @property
    def windows_score(self) -> Optional[float]:
        """Gets the windowsScore property"""
        return self.properties.get("windowsScore", None)

    @property
    def work_from_anywhere_score(self) -> Optional[float]:
        """Gets the workFromAnywhereScore property"""
        return self.properties.get("workFromAnywhereScore", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UserExperienceAnalyticsWorkFromAnywhereModelPerformance"
