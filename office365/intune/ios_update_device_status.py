from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.compliance.status import ComplianceStatus
    from office365.intune.devices.configurations.ios.iosupdatesinstallstatus import (
        IosUpdatesInstallStatus,
    )


class IosUpdateDeviceStatus(Entity):
    @property
    def compliance_grace_period_expiration_date_time(self) -> Optional[datetime]:
        """Gets the complianceGracePeriodExpirationDateTime property"""
        return self.properties.get("complianceGracePeriodExpirationDateTime", datetime.min)

    @property
    def device_display_name(self) -> Optional[str]:
        """Gets the deviceDisplayName property"""
        return self.properties.get("deviceDisplayName", None)

    @property
    def device_id(self) -> Optional[str]:
        """Gets the deviceId property"""
        return self.properties.get("deviceId", None)

    @property
    def device_model(self) -> Optional[str]:
        """Gets the deviceModel property"""
        return self.properties.get("deviceModel", None)

    @property
    def install_status(self) -> IosUpdatesInstallStatus:
        """Gets the installStatus property"""
        from office365.intune.devices.configurations.ios.iosupdatesinstallstatus import (
            IosUpdatesInstallStatus,
        )

        return self.properties.get("installStatus", IosUpdatesInstallStatus.deviceOsHigherThanDesiredOsVersion)

    @property
    def last_reported_date_time(self) -> Optional[datetime]:
        """Gets the lastReportedDateTime property"""
        return self.properties.get("lastReportedDateTime", datetime.min)

    @property
    def os_version(self) -> Optional[str]:
        """Gets the osVersion property"""
        return self.properties.get("osVersion", None)

    @property
    def status(self) -> ComplianceStatus:
        """Gets the status property"""
        from office365.intune.devices.compliance.status import ComplianceStatus

        return self.properties.get("status", ComplianceStatus.unknown)

    @property
    def user_id(self) -> Optional[str]:
        """Gets the userId property"""
        return self.properties.get("userId", None)

    @property
    def user_name(self) -> Optional[str]:
        """Gets the userName property"""
        return self.properties.get("userName", None)

    @property
    def user_principal_name(self) -> Optional[str]:
        """Gets the userPrincipalName property"""
        return self.properties.get("userPrincipalName", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IosUpdateDeviceStatus"
