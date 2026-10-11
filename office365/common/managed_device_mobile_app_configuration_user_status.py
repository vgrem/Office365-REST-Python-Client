from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.compliance.status import ComplianceStatus


class ManagedDeviceMobileAppConfigurationUserStatus(Entity):
    @property
    def devices_count(self) -> Optional[int]:
        """Gets the devicesCount property"""
        return self.properties.get("devicesCount", None)

    @property
    def last_reported_date_time(self) -> Optional[datetime]:
        """Gets the lastReportedDateTime property"""
        return self.properties.get("lastReportedDateTime", datetime.min)

    @property
    def status(self) -> ComplianceStatus:
        """Gets the status property"""
        from office365.intune.devices.compliance.status import ComplianceStatus

        return self.properties.get("status", ComplianceStatus.unknown)

    @property
    def user_display_name(self) -> Optional[str]:
        """Gets the userDisplayName property"""
        return self.properties.get("userDisplayName", None)

    @property
    def user_principal_name(self) -> Optional[str]:
        """Gets the userPrincipalName property"""
        return self.properties.get("userPrincipalName", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ManagedDeviceMobileAppConfigurationUserStatus"
