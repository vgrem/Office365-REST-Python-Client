from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.compliance.status import ComplianceStatus


class DeviceComplianceSettingState(Entity):
    @property
    def compliance_grace_period_expiration_date_time(self) -> Optional[datetime]:
        """Gets the complianceGracePeriodExpirationDateTime property"""
        return self.properties.get("complianceGracePeriodExpirationDateTime", datetime.min)

    @property
    def device_id(self) -> Optional[str]:
        """Gets the deviceId property"""
        return self.properties.get("deviceId", None)

    @property
    def device_model(self) -> Optional[str]:
        """Gets the deviceModel property"""
        return self.properties.get("deviceModel", None)

    @property
    def device_name(self) -> Optional[str]:
        """Gets the deviceName property"""
        return self.properties.get("deviceName", None)

    @property
    def setting(self) -> Optional[str]:
        """Gets the setting property"""
        return self.properties.get("setting", None)

    @property
    def setting_name(self) -> Optional[str]:
        """Gets the settingName property"""
        return self.properties.get("settingName", None)

    @property
    def state(self) -> ComplianceStatus:
        """Gets the state property"""
        from office365.intune.devices.compliance.status import ComplianceStatus

        return self.properties.get("state", ComplianceStatus.unknown)

    @property
    def user_email(self) -> Optional[str]:
        """Gets the userEmail property"""
        return self.properties.get("userEmail", None)

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
        return "microsoft.graph.DeviceComplianceSettingState"
