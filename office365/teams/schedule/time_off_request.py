from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity


class TimeOffRequest(Entity):
    @property
    def end_date_time(self) -> Optional[datetime]:
        """Gets the endDateTime property"""
        return self.properties.get("endDateTime", datetime.min)

    @property
    def start_date_time(self) -> Optional[datetime]:
        """Gets the startDateTime property"""
        return self.properties.get("startDateTime", datetime.min)

    @property
    def time_off_reason_id(self) -> Optional[str]:
        """Gets the timeOffReasonId property"""
        return self.properties.get("timeOffReasonId", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.TimeOffRequest"
