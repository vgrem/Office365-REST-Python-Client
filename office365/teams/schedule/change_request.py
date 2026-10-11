from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from typing_extensions import Self

from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.teams.schedule.change_tracked_entity import ChangeTrackedEntity

if TYPE_CHECKING:
    from office365.teams.schedule.changerequestactor import ScheduleChangeRequestActor
    from office365.teams.schedule.changestate import ScheduleChangeState


class ScheduleChangeRequest(ChangeTrackedEntity):
    """"""

    def approve(self, message: str) -> Self:
        """Approve an ScheduleChangeRequest object.

        Args:
            message (str): A custom approval message.
        """
        qry = ServiceOperationQuery(self, "approve", None, {"message": message})
        self.context.add_query(qry)
        return self

    def decline(self, message: str) -> Self:
        """Args:
        message (str): A custom approval message.
        """
        qry = ServiceOperationQuery(self, "decline", None, {"message": message})
        self.context.add_query(qry)
        return self

    @property
    def manager_action_datetime(self) -> datetime:
        """The date and time when the manager approved or declined the scheduleChangeRequest. The timestamp type
        represents date and time information using ISO 8601 format and is always in UTC.
        For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z."""
        return self.properties.get("managerActionDateTime", datetime.min)

    @property
    def manager_action_message(self) -> Optional[str]:
        """The message sent by the manager regarding the scheduleChangeRequest."""
        return self.properties.get("managerActionMessage", None)

    @property
    def assigned_to(self) -> ScheduleChangeRequestActor:
        """Gets the assignedTo property"""
        from office365.teams.schedule.changerequestactor import (
            ScheduleChangeRequestActor,
        )

        return self.properties.get("assignedTo", ScheduleChangeRequestActor.sender)

    @property
    def manager_user_id(self) -> Optional[str]:
        """Gets the managerUserId property"""
        return self.properties.get("managerUserId", None)

    @property
    def sender_date_time(self) -> Optional[datetime]:
        """Gets the senderDateTime property"""
        return self.properties.get("senderDateTime", datetime.min)

    @property
    def sender_message(self) -> Optional[str]:
        """Gets the senderMessage property"""
        return self.properties.get("senderMessage", None)

    @property
    def sender_user_id(self) -> Optional[str]:
        """Gets the senderUserId property"""
        return self.properties.get("senderUserId", None)

    @property
    def state(self) -> ScheduleChangeState:
        """Gets the state property"""
        from office365.teams.schedule.changestate import ScheduleChangeState

        return self.properties.get("state", ScheduleChangeState.pending)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ScheduleChangeRequest"
