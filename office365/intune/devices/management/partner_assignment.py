from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.policies.conditionalaccess.device_and_app_management_assignment_target import (
    DeviceAndAppManagementAssignmentTarget,
)
from office365.runtime.client_value import ClientValue


@dataclass
class DeviceManagementPartnerAssignment(ClientValue):
    target: DeviceAndAppManagementAssignmentTarget = field(default_factory=DeviceAndAppManagementAssignmentTarget)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceManagementPartnerAssignment"
