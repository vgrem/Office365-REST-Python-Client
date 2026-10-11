from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.request_schedule import RequestSchedule


class UnifiedRoleEligibilitySchedule(Entity):
    @property
    def member_type(self) -> Optional[str]:
        """Gets the memberType property"""
        return self.properties.get("memberType", None)

    @property
    def schedule_info(self) -> RequestSchedule:
        """Gets the scheduleInfo property"""
        from office365.directory.request_schedule import RequestSchedule

        return self.properties.get("scheduleInfo", RequestSchedule())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.UnifiedRoleEligibilitySchedule"
