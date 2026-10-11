from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.outlook.check_in_method import CheckInMethod


class CheckInClaim(Entity):
    @property
    def calendar_event_id(self) -> Optional[str]:
        """Gets the calendarEventId property"""
        return self.properties.get("calendarEventId", None)

    @property
    def check_in_method(self) -> CheckInMethod:
        """Gets the checkInMethod property"""
        from office365.outlook.check_in_method import CheckInMethod

        return self.properties.get("checkInMethod", CheckInMethod.unspecified)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CheckInClaim"
