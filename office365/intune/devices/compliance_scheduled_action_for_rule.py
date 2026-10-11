from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.devices.compliance_action_item import (
        DeviceComplianceActionItem,
    )


class DeviceComplianceScheduledActionForRule(Entity):
    @property
    def rule_name(self) -> Optional[str]:
        """Gets the ruleName property"""
        return self.properties.get("ruleName", None)

    @property
    def scheduled_action_configurations(self) -> EntityCollection[DeviceComplianceActionItem]:
        """Gets the scheduledActionConfigurations property"""
        from office365.intune.devices.compliance_action_item import (
            DeviceComplianceActionItem,
        )

        return self.properties.get(
            "scheduledActionConfigurations",
            EntityCollection[DeviceComplianceActionItem](
                self.context,
                DeviceComplianceActionItem,
                ResourcePath("scheduledActionConfigurations", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceComplianceScheduledActionForRule"
