from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.enrollment.failurereason import (
        DeviceEnrollmentFailureReason,
    )
    from office365.intune.devices.enrollment.type import DeviceEnrollmentType


class EnrollmentTroubleshootingEvent(Entity):
    @property
    def device_id(self) -> Optional[str]:
        """Gets the deviceId property"""
        return self.properties.get("deviceId", None)

    @property
    def enrollment_type(self) -> DeviceEnrollmentType:
        """Gets the enrollmentType property"""
        from office365.intune.devices.enrollment.type import DeviceEnrollmentType

        return self.properties.get("enrollmentType", DeviceEnrollmentType.unknown)

    @property
    def failure_category(self) -> DeviceEnrollmentFailureReason:
        """Gets the failureCategory property"""
        from office365.intune.devices.enrollment.failurereason import (
            DeviceEnrollmentFailureReason,
        )

        return self.properties.get("failureCategory", DeviceEnrollmentFailureReason.unknown)

    @property
    def failure_reason(self) -> Optional[str]:
        """Gets the failureReason property"""
        return self.properties.get("failureReason", None)

    @property
    def managed_device_identifier(self) -> Optional[str]:
        """Gets the managedDeviceIdentifier property"""
        return self.properties.get("managedDeviceIdentifier", None)

    @property
    def operating_system(self) -> Optional[str]:
        """Gets the operatingSystem property"""
        return self.properties.get("operatingSystem", None)

    @property
    def os_version(self) -> Optional[str]:
        """Gets the osVersion property"""
        return self.properties.get("osVersion", None)

    @property
    def user_id(self) -> Optional[str]:
        """Gets the userId property"""
        return self.properties.get("userId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.EnrollmentTroubleshootingEvent"
