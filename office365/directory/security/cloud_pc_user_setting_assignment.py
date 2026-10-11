from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.intune.devices.management.virtualendpoint.cloudpcs.managementassignmenttarget import (
        CloudPcManagementAssignmentTarget,
    )


class CloudPcUserSettingAssignment(Entity):
    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def target(self) -> CloudPcManagementAssignmentTarget:
        """Gets the target property"""
        from office365.intune.devices.management.virtualendpoint.cloudpcs.managementassignmenttarget import (
            CloudPcManagementAssignmentTarget,
        )

        return self.properties.get("target", CloudPcManagementAssignmentTarget())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CloudPcUserSettingAssignment"
