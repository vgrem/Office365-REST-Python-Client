from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.intune.devices.management.partner_assignment import (
        DeviceManagementPartnerAssignment,
    )
    from office365.intune.devices.management.partnerapptype import (
        DeviceManagementPartnerAppType,
    )
    from office365.intune.devices.management.partnertenantstate import (
        DeviceManagementPartnerTenantState,
    )


class DeviceManagementPartner(Entity):
    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def groups_requiring_partner_enrollment(self) -> ClientValueCollection[DeviceManagementPartnerAssignment]:
        """Gets the groupsRequiringPartnerEnrollment property"""
        from office365.intune.devices.management.partner_assignment import (
            DeviceManagementPartnerAssignment,
        )

        return self.properties.get(
            "groupsRequiringPartnerEnrollment",
            ClientValueCollection[DeviceManagementPartnerAssignment](DeviceManagementPartnerAssignment),
        )

    @property
    def is_configured(self) -> Optional[bool]:
        """Gets the isConfigured property"""
        return self.properties.get("isConfigured", None)

    @property
    def last_heartbeat_date_time(self) -> Optional[datetime]:
        """Gets the lastHeartbeatDateTime property"""
        return self.properties.get("lastHeartbeatDateTime", datetime.min)

    @property
    def partner_app_type(self) -> DeviceManagementPartnerAppType:
        """Gets the partnerAppType property"""
        from office365.intune.devices.management.partnerapptype import (
            DeviceManagementPartnerAppType,
        )

        return self.properties.get("partnerAppType", DeviceManagementPartnerAppType.unknown)

    @property
    def partner_state(self) -> DeviceManagementPartnerTenantState:
        """Gets the partnerState property"""
        from office365.intune.devices.management.partnertenantstate import (
            DeviceManagementPartnerTenantState,
        )

        return self.properties.get("partnerState", DeviceManagementPartnerTenantState.unknown)

    @property
    def single_tenant_app_id(self) -> Optional[str]:
        """Gets the singleTenantAppId property"""
        return self.properties.get("singleTenantAppId", None)

    @property
    def when_partner_devices_will_be_marked_as_non_compliant_date_time(self) -> Optional[datetime]:
        """Gets the whenPartnerDevicesWillBeMarkedAsNonCompliantDateTime property"""
        return self.properties.get("whenPartnerDevicesWillBeMarkedAsNonCompliantDateTime", datetime.min)

    @property
    def when_partner_devices_will_be_removed_date_time(self) -> Optional[datetime]:
        """Gets the whenPartnerDevicesWillBeRemovedDateTime property"""
        return self.properties.get("whenPartnerDevicesWillBeRemovedDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceManagementPartner"
