from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.management.mobileapps.mobilethreatpartnertenantstate import (
        MobileThreatPartnerTenantState,
    )


class MobileThreatDefenseConnector(Entity):
    @property
    def allow_partner_to_collect_ios_application_metadata(self) -> Optional[bool]:
        """Gets the allowPartnerToCollectIOSApplicationMetadata property"""
        return self.properties.get("allowPartnerToCollectIOSApplicationMetadata", None)

    @property
    def allow_partner_to_collect_ios_personal_application_metadata(self) -> Optional[bool]:
        """Gets the allowPartnerToCollectIOSPersonalApplicationMetadata property"""
        return self.properties.get("allowPartnerToCollectIOSPersonalApplicationMetadata", None)

    @property
    def android_device_blocked_on_missing_partner_data(self) -> Optional[bool]:
        """Gets the androidDeviceBlockedOnMissingPartnerData property"""
        return self.properties.get("androidDeviceBlockedOnMissingPartnerData", None)

    @property
    def android_enabled(self) -> Optional[bool]:
        """Gets the androidEnabled property"""
        return self.properties.get("androidEnabled", None)

    @property
    def android_mobile_application_management_enabled(self) -> Optional[bool]:
        """Gets the androidMobileApplicationManagementEnabled property"""
        return self.properties.get("androidMobileApplicationManagementEnabled", None)

    @property
    def ios_device_blocked_on_missing_partner_data(self) -> Optional[bool]:
        """Gets the iosDeviceBlockedOnMissingPartnerData property"""
        return self.properties.get("iosDeviceBlockedOnMissingPartnerData", None)

    @property
    def ios_enabled(self) -> Optional[bool]:
        """Gets the iosEnabled property"""
        return self.properties.get("iosEnabled", None)

    @property
    def ios_mobile_application_management_enabled(self) -> Optional[bool]:
        """Gets the iosMobileApplicationManagementEnabled property"""
        return self.properties.get("iosMobileApplicationManagementEnabled", None)

    @property
    def last_heartbeat_date_time(self) -> Optional[datetime]:
        """Gets the lastHeartbeatDateTime property"""
        return self.properties.get("lastHeartbeatDateTime", datetime.min)

    @property
    def microsoft_defender_for_endpoint_attach_enabled(self) -> Optional[bool]:
        """Gets the microsoftDefenderForEndpointAttachEnabled property"""
        return self.properties.get("microsoftDefenderForEndpointAttachEnabled", None)

    @property
    def partner_state(self) -> MobileThreatPartnerTenantState:
        """Gets the partnerState property"""
        from office365.intune.devices.management.mobileapps.mobilethreatpartnertenantstate import (
            MobileThreatPartnerTenantState,
        )

        return self.properties.get("partnerState", MobileThreatPartnerTenantState.unavailable)

    @property
    def partner_unresponsiveness_threshold_in_days(self) -> Optional[int]:
        """Gets the partnerUnresponsivenessThresholdInDays property"""
        return self.properties.get("partnerUnresponsivenessThresholdInDays", None)

    @property
    def partner_unsupported_os_version_blocked(self) -> Optional[bool]:
        """Gets the partnerUnsupportedOsVersionBlocked property"""
        return self.properties.get("partnerUnsupportedOsVersionBlocked", None)

    @property
    def windows_device_blocked_on_missing_partner_data(self) -> Optional[bool]:
        """Gets the windowsDeviceBlockedOnMissingPartnerData property"""
        return self.properties.get("windowsDeviceBlockedOnMissingPartnerData", None)

    @property
    def windows_enabled(self) -> Optional[bool]:
        """Gets the windowsEnabled property"""
        return self.properties.get("windowsEnabled", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.MobileThreatDefenseConnector"
