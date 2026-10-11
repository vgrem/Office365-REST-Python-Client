from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.directory.identitygovernance.privilegedaccess.schedule.requestactions import (
    ScheduleRequestActions,
)
from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.request_schedule import RequestSchedule
    from office365.directory.ticket_info import TicketInfo


class PrivilegedAccessScheduleRequest(Entity):
    @property
    def action(self) -> ScheduleRequestActions:
        """Gets the action property"""
        return self.properties.get("action", ScheduleRequestActions.adminAssign)

    @property
    def is_validation_only(self) -> Optional[bool]:
        """Gets the isValidationOnly property"""
        return self.properties.get("isValidationOnly", None)

    @property
    def justification(self) -> Optional[str]:
        """Gets the justification property"""
        return self.properties.get("justification", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.PrivilegedAccessScheduleRequest"

    @property
    def schedule_info(self) -> RequestSchedule:
        """Gets the scheduleInfo property"""
        from office365.directory.request_schedule import RequestSchedule

        return self.properties.get("scheduleInfo", RequestSchedule())

    @property
    def ticket_info(self) -> TicketInfo:
        """Gets the ticketInfo property"""
        from office365.directory.ticket_info import TicketInfo

        return self.properties.get("ticketInfo", TicketInfo())
