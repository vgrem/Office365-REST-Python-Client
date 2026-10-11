from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.management.enrollment_state import EnrollmentState


class WindowsAutopilotDeviceIdentity(Entity):
    @property
    def addressable_user_name(self) -> Optional[str]:
        """Gets the addressableUserName property"""
        return self.properties.get("addressableUserName", None)

    @property
    def azure_active_directory_device_id(self) -> Optional[str]:
        """Gets the azureActiveDirectoryDeviceId property"""
        return self.properties.get("azureActiveDirectoryDeviceId", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def enrollment_state(self) -> EnrollmentState:
        """Gets the enrollmentState property"""
        from office365.intune.devices.management.enrollment_state import EnrollmentState

        return self.properties.get("enrollmentState", EnrollmentState.unknown)

    @property
    def group_tag(self) -> Optional[str]:
        """Gets the groupTag property"""
        return self.properties.get("groupTag", None)

    @property
    def last_contacted_date_time(self) -> Optional[datetime]:
        """Gets the lastContactedDateTime property"""
        return self.properties.get("lastContactedDateTime", datetime.min)

    @property
    def managed_device_id(self) -> Optional[str]:
        """Gets the managedDeviceId property"""
        return self.properties.get("managedDeviceId", None)

    @property
    def manufacturer(self) -> Optional[str]:
        """Gets the manufacturer property"""
        return self.properties.get("manufacturer", None)

    @property
    def model(self) -> Optional[str]:
        """Gets the model property"""
        return self.properties.get("model", None)

    @property
    def product_key(self) -> Optional[str]:
        """Gets the productKey property"""
        return self.properties.get("productKey", None)

    @property
    def purchase_order_identifier(self) -> Optional[str]:
        """Gets the purchaseOrderIdentifier property"""
        return self.properties.get("purchaseOrderIdentifier", None)

    @property
    def resource_name(self) -> Optional[str]:
        """Gets the resourceName property"""
        return self.properties.get("resourceName", None)

    @property
    def serial_number(self) -> Optional[str]:
        """Gets the serialNumber property"""
        return self.properties.get("serialNumber", None)

    @property
    def sku_number(self) -> Optional[str]:
        """Gets the skuNumber property"""
        return self.properties.get("skuNumber", None)

    @property
    def system_family(self) -> Optional[str]:
        """Gets the systemFamily property"""
        return self.properties.get("systemFamily", None)

    @property
    def user_principal_name(self) -> Optional[str]:
        """Gets the userPrincipalName property"""
        return self.properties.get("userPrincipalName", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WindowsAutopilotDeviceIdentity"
