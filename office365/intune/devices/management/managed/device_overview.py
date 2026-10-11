from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.management.exchange_access_state_summary import (
        DeviceExchangeAccessStateSummary,
    )
    from office365.intune.devices.management.operating_system_summary import (
        DeviceOperatingSystemSummary,
    )


class ManagedDeviceOverview(Entity):
    @property
    def device_exchange_access_state_summary(self) -> DeviceExchangeAccessStateSummary:
        """Gets the deviceExchangeAccessStateSummary property"""
        from office365.intune.devices.management.exchange_access_state_summary import (
            DeviceExchangeAccessStateSummary,
        )

        return self.properties.get("deviceExchangeAccessStateSummary", DeviceExchangeAccessStateSummary())

    @property
    def device_operating_system_summary(self) -> DeviceOperatingSystemSummary:
        """Gets the deviceOperatingSystemSummary property"""
        from office365.intune.devices.management.operating_system_summary import (
            DeviceOperatingSystemSummary,
        )

        return self.properties.get("deviceOperatingSystemSummary", DeviceOperatingSystemSummary())

    @property
    def dual_enrolled_device_count(self) -> Optional[int]:
        """Gets the dualEnrolledDeviceCount property"""
        return self.properties.get("dualEnrolledDeviceCount", None)

    @property
    def enrolled_device_count(self) -> Optional[int]:
        """Gets the enrolledDeviceCount property"""
        return self.properties.get("enrolledDeviceCount", None)

    @property
    def mdm_enrolled_count(self) -> Optional[int]:
        """Gets the mdmEnrolledCount property"""
        return self.properties.get("mdmEnrolledCount", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ManagedDeviceOverview"
