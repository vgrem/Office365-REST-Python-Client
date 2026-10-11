from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity


class DeviceManagementTroubleshootingEvent(Entity):
    @property
    def correlation_id(self) -> Optional[str]:
        """Gets the correlationId property"""
        return self.properties.get("correlationId", None)

    @property
    def event_date_time(self) -> Optional[datetime]:
        """Gets the eventDateTime property"""
        return self.properties.get("eventDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DeviceManagementTroubleshootingEvent"
