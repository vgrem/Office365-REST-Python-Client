from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.management.userexperienceanalytics.healthstate import (
        UserExperienceAnalyticsHealthState,
    )
    from office365.intune.devices.management.userexperienceanalytics.operatingsystemupgradeeligibility import (
        OperatingSystemUpgradeEligibility,
    )


class UserExperienceAnalyticsWorkFromAnywhereDevice(Entity):
    @property
    def auto_pilot_profile_assigned(self) -> Optional[bool]:
        """Gets the autoPilotProfileAssigned property"""
        return self.properties.get("autoPilotProfileAssigned", None)

    @property
    def auto_pilot_registered(self) -> Optional[bool]:
        """Gets the autoPilotRegistered property"""
        return self.properties.get("autoPilotRegistered", None)

    @property
    def azure_ad_device_id(self) -> Optional[str]:
        """Gets the azureAdDeviceId property"""
        return self.properties.get("azureAdDeviceId", None)

    @property
    def azure_ad_join_type(self) -> Optional[str]:
        """Gets the azureAdJoinType property"""
        return self.properties.get("azureAdJoinType", None)

    @property
    def azure_ad_registered(self) -> Optional[bool]:
        """Gets the azureAdRegistered property"""
        return self.properties.get("azureAdRegistered", None)

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
    def compliance_policy_set_to_intune(self) -> Optional[bool]:
        """Gets the compliancePolicySetToIntune property"""
        return self.properties.get("compliancePolicySetToIntune", None)

    @property
    def device_id(self) -> Optional[str]:
        """Gets the deviceId property"""
        return self.properties.get("deviceId", None)

    @property
    def device_name(self) -> Optional[str]:
        """Gets the deviceName property"""
        return self.properties.get("deviceName", None)

    @property
    def health_status(self) -> UserExperienceAnalyticsHealthState:
        """Gets the healthStatus property"""
        from office365.intune.devices.management.userexperienceanalytics.healthstate import (
            UserExperienceAnalyticsHealthState,
        )

        return self.properties.get("healthStatus", UserExperienceAnalyticsHealthState.unknown)

    @property
    def is_cloud_managed_gateway_enabled(self) -> Optional[bool]:
        """Gets the isCloudManagedGatewayEnabled property"""
        return self.properties.get("isCloudManagedGatewayEnabled", None)

    @property
    def managed_by(self) -> Optional[str]:
        """Gets the managedBy property"""
        return self.properties.get("managedBy", None)

    @property
    def manufacturer(self) -> Optional[str]:
        """Gets the manufacturer property"""
        return self.properties.get("manufacturer", None)

    @property
    def model(self) -> Optional[str]:
        """Gets the model property"""
        return self.properties.get("model", None)

    @property
    def os_check_failed(self) -> Optional[bool]:
        """Gets the osCheckFailed property"""
        return self.properties.get("osCheckFailed", None)

    @property
    def os_description(self) -> Optional[str]:
        """Gets the osDescription property"""
        return self.properties.get("osDescription", None)

    @property
    def os_version(self) -> Optional[str]:
        """Gets the osVersion property"""
        return self.properties.get("osVersion", None)

    @property
    def other_workloads_set_to_intune(self) -> Optional[bool]:
        """Gets the otherWorkloadsSetToIntune property"""
        return self.properties.get("otherWorkloadsSetToIntune", None)

    @property
    def ownership(self) -> Optional[str]:
        """Gets the ownership property"""
        return self.properties.get("ownership", None)

    @property
    def processor64_bit_check_failed(self) -> Optional[bool]:
        """Gets the processor64BitCheckFailed property"""
        return self.properties.get("processor64BitCheckFailed", None)

    @property
    def processor_core_count_check_failed(self) -> Optional[bool]:
        """Gets the processorCoreCountCheckFailed property"""
        return self.properties.get("processorCoreCountCheckFailed", None)

    @property
    def processor_family_check_failed(self) -> Optional[bool]:
        """Gets the processorFamilyCheckFailed property"""
        return self.properties.get("processorFamilyCheckFailed", None)

    @property
    def processor_speed_check_failed(self) -> Optional[bool]:
        """Gets the processorSpeedCheckFailed property"""
        return self.properties.get("processorSpeedCheckFailed", None)

    @property
    def ram_check_failed(self) -> Optional[bool]:
        """Gets the ramCheckFailed property"""
        return self.properties.get("ramCheckFailed", None)

    @property
    def secure_boot_check_failed(self) -> Optional[bool]:
        """Gets the secureBootCheckFailed property"""
        return self.properties.get("secureBootCheckFailed", None)

    @property
    def serial_number(self) -> Optional[str]:
        """Gets the serialNumber property"""
        return self.properties.get("serialNumber", None)

    @property
    def storage_check_failed(self) -> Optional[bool]:
        """Gets the storageCheckFailed property"""
        return self.properties.get("storageCheckFailed", None)

    @property
    def tenant_attached(self) -> Optional[bool]:
        """Gets the tenantAttached property"""
        return self.properties.get("tenantAttached", None)

    @property
    def tpm_check_failed(self) -> Optional[bool]:
        """Gets the tpmCheckFailed property"""
        return self.properties.get("tpmCheckFailed", None)

    @property
    def upgrade_eligibility(self) -> OperatingSystemUpgradeEligibility:
        """Gets the upgradeEligibility property"""
        from office365.intune.devices.management.userexperienceanalytics.operatingsystemupgradeeligibility import (
            OperatingSystemUpgradeEligibility,
        )

        return self.properties.get("upgradeEligibility", OperatingSystemUpgradeEligibility.upgraded)

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
        return "microsoft.graph.UserExperienceAnalyticsWorkFromAnywhereDevice"
