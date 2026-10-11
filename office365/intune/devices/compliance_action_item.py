from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.intune.devices.compliance.actiontype import (
        DeviceComplianceActionType,
    )


class DeviceComplianceActionItem(Entity):
    @property
    def action_type(self) -> DeviceComplianceActionType:
        """Gets the actionType property"""
        from office365.intune.devices.compliance.actiontype import (
            DeviceComplianceActionType,
        )

        return self.properties.get("actionType", DeviceComplianceActionType.noAction)

    @property
    def grace_period_hours(self) -> Optional[int]:
        """Gets the gracePeriodHours property"""
        return self.properties.get("gracePeriodHours", None)

    @property
    def notification_message_cc_list(self) -> StringCollection:
        """Gets the notificationMessageCCList property"""
        return self.properties.get("notificationMessageCCList", StringCollection())

    @property
    def notification_template_id(self) -> Optional[str]:
        """Gets the notificationTemplateId property"""
        return self.properties.get("notificationTemplateId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceComplianceActionItem"
