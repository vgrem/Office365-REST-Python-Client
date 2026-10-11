from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.enrollment.configuration_assignment import (
        EnrollmentConfigurationAssignment,
    )


class DeviceEnrollmentConfiguration(Entity):
    """The Base Class of Device Enrollment Configuration"""

    def __str__(self):
        return self.display_name or self.entity_type_name

    @property
    def created_datetime(self) -> datetime:
        """
        Created date time in UTC of the device enrollment configuration
        """
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def display_name(self) -> Optional[str]:
        """The display name of the device enrollment configuration"""
        return self.properties.get("displayName", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def last_modified_date_time(self) -> Optional[datetime]:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def priority(self) -> Optional[int]:
        """Gets the priority property"""
        return self.properties.get("priority", None)

    @property
    def version(self) -> Optional[int]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def assignments(self) -> EntityCollection[EnrollmentConfigurationAssignment]:
        """Gets the assignments property"""
        from office365.intune.devices.enrollment.configuration_assignment import (
            EnrollmentConfigurationAssignment,
        )

        return self.properties.get(
            "assignments",
            EntityCollection[EnrollmentConfigurationAssignment](
                self.context, EnrollmentConfigurationAssignment, ResourcePath("assignments", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceEnrollmentConfiguration"
