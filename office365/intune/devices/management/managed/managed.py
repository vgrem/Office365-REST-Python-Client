from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from typing_extensions import Self

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.intune.devices.category import DeviceCategory
from office365.intune.devices.compliance.policy_state import DeviceCompliancePolicyState
from office365.intune.devices.enrollment.type import DeviceEnrollmentType
from office365.intune.devices.management.exchangeaccessstate import (
    DeviceManagementExchangeAccessState,
)
from office365.intune.devices.management.exchangeaccessstatereason import (
    DeviceManagementExchangeAccessStateReason,
)
from office365.intune.devices.management.managed.compliancestate import ComplianceState
from office365.intune.devices.management.managed.managementagenttype import (
    ManagementAgentType,
)
from office365.intune.devices.management.managed.managementstate import ManagementState
from office365.intune.devices.management.managed.ownertype import ManagedDeviceOwnerType
from office365.intune.devices.management.managed.partnerreportedhealthstate import (
    ManagedDevicePartnerReportedHealthState,
)
from office365.intune.devices.registrationstate import DeviceRegistrationState
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.directory.users.collection import UserCollection
    from office365.intune.devices.configuration_state import DeviceConfigurationState
    from office365.intune.devices.log_collection_response import (
        DeviceLogCollectionResponse,
    )
    from office365.intune.devices.management.action_result import DeviceActionResult
    from office365.intune.devices.management.configuration_manager_client_enabled_features import (
        ConfigurationManagerClientEnabledFeatures,
    )
    from office365.intune.devices.management.health_attestation_state import (
        DeviceHealthAttestationState,
    )
    from office365.intune.devices.management.windows_protection_state import WindowsProtectionState


class ManagedDevice(Entity):
    """Devices that are managed or pre-enrolled through Intune"""

    def locate_device(self) -> Self:
        """Locate a device"""
        qry = ServiceOperationQuery(self, "locateDevice")
        self.context.add_query(qry)
        return self

    def wipe(self) -> Self:
        """Wipe a device (factory reset — removes all data).

        https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-wipe
        """
        qry = ServiceOperationQuery(self, "wipe")
        self.context.add_query(qry)
        return self

    def retire(self) -> Self:
        """Retire a device (removes company data only).

        https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-retire
        """
        qry = ServiceOperationQuery(self, "retire")
        self.context.add_query(qry)
        return self

    def sync_device(self) -> Self:
        """Sync a device (force it to check in with Intune).

        https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-syncdevice
        """
        qry = ServiceOperationQuery(self, "syncDevice")
        self.context.add_query(qry)
        return self

    def reboot_now(self) -> Self:
        """Reboot a device.

        https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-rebootnow
        """
        qry = ServiceOperationQuery(self, "rebootNow")
        self.context.add_query(qry)
        return self

    def remote_lock(self) -> Self:
        """Lock a device remotely.

        https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-remotelock
        """
        qry = ServiceOperationQuery(self, "remoteLock")
        self.context.add_query(qry)
        return self

    def shut_down(self) -> Self:
        """Shut down a device.

        https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-shutdown
        """
        qry = ServiceOperationQuery(self, "shutDown")
        self.context.add_query(qry)
        return self

    def set_primary_user(self, user_id: str) -> Self:
        """Set the primary user of a device.

        Args:
            user_id: ID of the user to assign as primary user

        https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-users
        """
        payload = {"@odata.id": f"https://graph.microsoft.com/v1.0/users/{user_id}"}
        qry = ServiceOperationQuery(self.users, "$ref", None, payload)
        self.context.add_query(qry)
        return self

    def remove_primary_user(self, user_id: str) -> Self:
        """Remove a user from a device.

        Args:
            user_id: ID of the user to remove

        https://learn.microsoft.com/en-us/graph/api/intune-devices-manageddevice-users
        """
        qry = ServiceOperationQuery(self.users, f"{user_id}/$ref")
        self.context.add_query(qry)
        return self

    @property
    def activation_lock_bypass_code(self) -> Optional[str]:
        """
        The code that allows the Activation Lock on managed device to be bypassed. Default,
        is Null (Non-Default property) for this property when returned as part of managedDevice entity in LIST call.
        To retrieve actual values GET call needs to be made, with device id and included in select parameter.
        Supports: $select. $Search is not supported. Read-only. This property is read-only.
        """
        return self.properties.get("activationLockBypassCode", None)

    @property
    def device_category(self) -> DeviceCategory:
        """Device category"""
        return self.properties.get(
            "deviceCategory", DeviceCategory(self.context, ResourcePath("deviceCategory", self.resource_path))
        )

    @property
    def manufacturer(self) -> Optional[str]:
        """Manufacturer of the device."""
        return self.properties.get("manufacturer", None)

    @property
    def operating_system(self) -> Optional[str]:
        """Manufacturer of the device."""
        return self.properties.get("operatingSystem", None)

    @property
    def device_compliance_policy_states(self) -> EntityCollection[DeviceCompliancePolicyState]:
        """Device compliance policy states for this device"""
        return self.properties.get(
            "deviceCompliancePolicyStates",
            EntityCollection(
                self.context,
                DeviceCompliancePolicyState,
                ResourcePath("deviceCompliancePolicyStates", self.resource_path),
            ),
        )

    @property
    def users(self) -> UserCollection:
        """The primary users associated with the managed device."""
        from office365.directory.users.collection import UserCollection

        return self.properties.get("users", UserCollection(self.context, ResourcePath("users", self.resource_path)))

    @property
    def android_security_patch_level(self) -> Optional[str]:
        """Gets the androidSecurityPatchLevel property"""
        return self.properties.get("androidSecurityPatchLevel", None)

    @property
    def azure_ad_device_id(self) -> Optional[str]:
        """Gets the azureADDeviceId property"""
        return self.properties.get("azureADDeviceId", None)

    @property
    def azure_ad_registered(self) -> Optional[bool]:
        """Gets the azureADRegistered property"""
        return self.properties.get("azureADRegistered", None)

    @property
    def compliance_grace_period_expiration_date_time(self) -> datetime:
        """Gets the complianceGracePeriodExpirationDateTime property"""
        return self.properties.get("complianceGracePeriodExpirationDateTime", datetime.min)

    @property
    def compliance_state(self) -> ComplianceState:
        """Gets the complianceState property"""
        return self.properties.get("complianceState", ComplianceState.unknown)

    @property
    def device_category_display_name(self) -> Optional[str]:
        """Gets the deviceCategoryDisplayName property"""
        return self.properties.get("deviceCategoryDisplayName", None)

    @property
    def device_enrollment_type(self) -> DeviceEnrollmentType:
        """Gets the deviceEnrollmentType property"""
        return self.properties.get("deviceEnrollmentType", DeviceEnrollmentType.unknown)

    @property
    def device_name(self) -> Optional[str]:
        """Gets the deviceName property"""
        return self.properties.get("deviceName", None)

    @property
    def device_registration_state(self) -> DeviceRegistrationState:
        """Gets the deviceRegistrationState property"""
        return self.properties.get("deviceRegistrationState", DeviceRegistrationState.notRegistered)

    @property
    def eas_activated(self) -> Optional[bool]:
        """Gets the easActivated property"""
        return self.properties.get("easActivated", None)

    @property
    def eas_activation_date_time(self) -> datetime:
        """Gets the easActivationDateTime property"""
        return self.properties.get("easActivationDateTime", datetime.min)

    @property
    def eas_device_id(self) -> Optional[str]:
        """Gets the easDeviceId property"""
        return self.properties.get("easDeviceId", None)

    @property
    def email_address(self) -> Optional[str]:
        """Gets the emailAddress property"""
        return self.properties.get("emailAddress", None)

    @property
    def enrolled_date_time(self) -> datetime:
        """Gets the enrolledDateTime property"""
        return self.properties.get("enrolledDateTime", datetime.min)

    @property
    def enrollment_profile_name(self) -> Optional[str]:
        """Gets the enrollmentProfileName property"""
        return self.properties.get("enrollmentProfileName", None)

    @property
    def ethernet_mac_address(self) -> Optional[str]:
        """Gets the ethernetMacAddress property"""
        return self.properties.get("ethernetMacAddress", None)

    @odata(name="exchangeAccessState")
    @property
    def exchange_access_state(self) -> DeviceManagementExchangeAccessState:
        """Gets the exchangeAccessState property"""
        return self.properties.get("exchangeAccessState", DeviceManagementExchangeAccessState.none)

    @odata(name="exchangeAccessStateReason")
    @property
    def exchange_access_state_reason(self) -> DeviceManagementExchangeAccessStateReason:
        """Gets the exchangeAccessStateReason property"""
        return self.properties.get("exchangeAccessStateReason", DeviceManagementExchangeAccessStateReason.none)

    @odata(name="exchangeLastSuccessfulSyncDateTime")
    @property
    def exchange_last_successful_sync_date_time(self) -> datetime:
        """Gets the exchangeLastSuccessfulSyncDateTime property"""
        return self.properties.get("exchangeLastSuccessfulSyncDateTime", datetime.min)

    @property
    def free_storage_space_in_bytes(self) -> Optional[int]:
        """Gets the freeStorageSpaceInBytes property"""
        return self.properties.get("freeStorageSpaceInBytes", None)

    @property
    def iccid(self) -> Optional[str]:
        """Gets the iccid property"""
        return self.properties.get("iccid", None)

    @property
    def imei(self) -> Optional[str]:
        """Gets the imei property"""
        return self.properties.get("imei", None)

    @property
    def is_encrypted(self) -> Optional[bool]:
        """Gets the isEncrypted property"""
        return self.properties.get("isEncrypted", None)

    @property
    def is_supervised(self) -> Optional[bool]:
        """Gets the isSupervised property"""
        return self.properties.get("isSupervised", None)

    @property
    def jail_broken(self) -> Optional[str]:
        """Gets the jailBroken property"""
        return self.properties.get("jailBroken", None)

    @odata(name="lastSyncDateTime")
    @property
    def last_sync_date_time(self) -> datetime:
        """Gets the lastSyncDateTime property"""
        return self.properties.get("lastSyncDateTime", datetime.min)

    @property
    def managed_device_name(self) -> Optional[str]:
        """Gets the managedDeviceName property"""
        return self.properties.get("managedDeviceName", None)

    @odata(name="managedDeviceOwnerType")
    @property
    def managed_device_owner_type(self) -> ManagedDeviceOwnerType:
        """Gets the managedDeviceOwnerType property"""
        return self.properties.get("managedDeviceOwnerType", ManagedDeviceOwnerType.unknown)

    @odata(name="managementAgent")
    @property
    def management_agent(self) -> ManagementAgentType:
        """Gets the managementAgent property"""
        return self.properties.get("managementAgent", ManagementAgentType.eas)

    @odata(name="managementCertificateExpirationDate")
    @property
    def management_certificate_expiration_date(self) -> datetime:
        """Gets the managementCertificateExpirationDate property"""
        return self.properties.get("managementCertificateExpirationDate", datetime.min)

    @odata(name="managementState")
    @property
    def management_state(self) -> ManagementState:
        """Gets the managementState property"""
        return self.properties.get("managementState", ManagementState.managed)

    @property
    def meid(self) -> Optional[str]:
        """Gets the meid property"""
        return self.properties.get("meid", None)

    @property
    def model(self) -> Optional[str]:
        """Gets the model property"""
        return self.properties.get("model", None)

    @property
    def notes(self) -> Optional[str]:
        """Gets the notes property"""
        return self.properties.get("notes", None)

    @property
    def os_version(self) -> Optional[str]:
        """Gets the osVersion property"""
        return self.properties.get("osVersion", None)

    @odata(name="partnerReportedThreatState")
    @property
    def partner_reported_threat_state(self) -> ManagedDevicePartnerReportedHealthState:
        """Gets the partnerReportedThreatState property"""
        return self.properties.get("partnerReportedThreatState", ManagedDevicePartnerReportedHealthState.unknown)

    @property
    def phone_number(self) -> Optional[str]:
        """Gets the phoneNumber property"""
        return self.properties.get("phoneNumber", None)

    @property
    def physical_memory_in_bytes(self) -> Optional[int]:
        """Gets the physicalMemoryInBytes property"""
        return self.properties.get("physicalMemoryInBytes", None)

    @property
    def remote_assistance_session_error_details(self) -> Optional[str]:
        """Gets the remoteAssistanceSessionErrorDetails property"""
        return self.properties.get("remoteAssistanceSessionErrorDetails", None)

    @property
    def remote_assistance_session_url(self) -> Optional[str]:
        """Gets the remoteAssistanceSessionUrl property"""
        return self.properties.get("remoteAssistanceSessionUrl", None)

    @property
    def require_user_enrollment_approval(self) -> Optional[bool]:
        """Gets the requireUserEnrollmentApproval property"""
        return self.properties.get("requireUserEnrollmentApproval", None)

    @property
    def serial_number(self) -> Optional[str]:
        """Gets the serialNumber property"""
        return self.properties.get("serialNumber", None)

    @property
    def subscriber_carrier(self) -> Optional[str]:
        """Gets the subscriberCarrier property"""
        return self.properties.get("subscriberCarrier", None)

    @property
    def total_storage_space_in_bytes(self) -> Optional[int]:
        """Gets the totalStorageSpaceInBytes property"""
        return self.properties.get("totalStorageSpaceInBytes", None)

    @property
    def udid(self) -> Optional[str]:
        """Gets the udid property"""
        return self.properties.get("udid", None)

    @property
    def user_display_name(self) -> Optional[str]:
        """Gets the userDisplayName property"""
        return self.properties.get("userDisplayName", None)

    @property
    def user_id(self) -> Optional[str]:
        """Gets the userId property"""
        return self.properties.get("userId", None)

    @property
    def user_principal_name(self) -> Optional[str]:
        """Gets the userPrincipalName property"""
        return self.properties.get("userPrincipalName", None)

    @property
    def wi_fi_mac_address(self) -> Optional[str]:
        """Gets the wiFiMacAddress property"""
        return self.properties.get("wiFiMacAddress", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ManagedDevice"

    @property
    def configuration_manager_client_enabled_features(self) -> ConfigurationManagerClientEnabledFeatures:
        """Gets the configurationManagerClientEnabledFeatures property"""
        from office365.intune.devices.management.configuration_manager_client_enabled_features import (
            ConfigurationManagerClientEnabledFeatures,
        )

        return self.properties.get(
            "configurationManagerClientEnabledFeatures", ConfigurationManagerClientEnabledFeatures()
        )

    @property
    def device_action_results(self) -> ClientValueCollection[DeviceActionResult]:
        """Gets the deviceActionResults property"""
        from office365.intune.devices.management.action_result import DeviceActionResult

        return self.properties.get("deviceActionResults", ClientValueCollection[DeviceActionResult](DeviceActionResult))

    @property
    def device_health_attestation_state(self) -> DeviceHealthAttestationState:
        """Gets the deviceHealthAttestationState property"""
        from office365.intune.devices.management.health_attestation_state import (
            DeviceHealthAttestationState,
        )

        return self.properties.get("deviceHealthAttestationState", DeviceHealthAttestationState())

    @property
    def device_configuration_states(self) -> EntityCollection[DeviceConfigurationState]:
        """Gets the deviceConfigurationStates property"""
        from office365.intune.devices.configuration_state import (
            DeviceConfigurationState,
        )

        return self.properties.get(
            "deviceConfigurationStates",
            EntityCollection[DeviceConfigurationState](
                self.context, DeviceConfigurationState, ResourcePath("deviceConfigurationStates", self.resource_path)
            ),
        )

    @property
    def log_collection_requests(self) -> EntityCollection[DeviceLogCollectionResponse]:
        """Gets the logCollectionRequests property"""
        from office365.intune.devices.log_collection_response import (
            DeviceLogCollectionResponse,
        )

        return self.properties.get(
            "logCollectionRequests",
            EntityCollection[DeviceLogCollectionResponse](
                self.context, DeviceLogCollectionResponse, ResourcePath("logCollectionRequests", self.resource_path)
            ),
        )

    @property
    def windows_protection_state(self) -> WindowsProtectionState:
        """Gets the windowsProtectionState property"""
        from office365.intune.devices.management.windows_protection_state import WindowsProtectionState

        return self.properties.get(
            "windowsProtectionState",
            WindowsProtectionState(self.context, ResourcePath("windowsProtectionState", self.resource_path)),
        )
