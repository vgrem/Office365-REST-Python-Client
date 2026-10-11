from __future__ import annotations

from datetime import time
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.outlook.calendar.dayofweek import DayOfWeek


class IosUpdateConfiguration(Entity):
    @property
    def active_hours_end(self) -> Optional[time]:
        """Gets the activeHoursEnd property"""
        return self.properties.get("activeHoursEnd", None)

    @property
    def active_hours_start(self) -> Optional[time]:
        """Gets the activeHoursStart property"""
        return self.properties.get("activeHoursStart", None)

    @property
    def scheduled_install_days(self) -> ClientValueCollection[DayOfWeek]:
        """Gets the scheduledInstallDays property"""
        from office365.outlook.calendar.dayofweek import DayOfWeek

        return self.properties.get("scheduledInstallDays", ClientValueCollection[DayOfWeek](DayOfWeek))

    @property
    def utc_time_offset_in_minutes(self) -> Optional[int]:
        """Gets the utcTimeOffsetInMinutes property"""
        return self.properties.get("utcTimeOffsetInMinutes", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.IosUpdateConfiguration"
