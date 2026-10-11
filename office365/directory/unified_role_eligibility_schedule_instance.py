from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.entity import Entity


class UnifiedRoleEligibilityScheduleInstance(Entity):
    @property
    def end_date_time(self) -> Optional[datetime]:
        """Gets the endDateTime property"""
        return self.properties.get("endDateTime", datetime.min)

    @property
    def member_type(self) -> Optional[str]:
        """Gets the memberType property"""
        return self.properties.get("memberType", None)

    @property
    def role_eligibility_schedule_id(self) -> Optional[str]:
        """Gets the roleEligibilityScheduleId property"""
        return self.properties.get("roleEligibilityScheduleId", None)

    @property
    def start_date_time(self) -> Optional[datetime]:
        """Gets the startDateTime property"""
        return self.properties.get("startDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRoleEligibilityScheduleInstance"
