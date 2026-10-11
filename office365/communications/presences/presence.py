from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from typing_extensions import Self

from office365.communications.presences.status_message import PresenceStatusMessage
from office365.communications.quotas import PRESENCE_QUOTAS
from office365.entity import Entity
from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
from office365.outlook.mail.item_body import ItemBody
from office365.runtime.limits import limit
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.duration import Duration

if TYPE_CHECKING:
    from office365.communications.out_of_office_settings import OutOfOfficeSettings
    from office365.communications.user_work_location import UserWorkLocation


@limit(*PRESENCE_QUOTAS)
class Presence(Entity):
    """Contains information about a user's presence, including their availability and user activity."""

    def clear_presence(self, session_id: str | None = None) -> Self:
        """Clear the application's presence session for a user. If it is the user's only presence session,
        the user's presence will change to Offline/Offline.

        Args:
            session_id (str): The ID of the application's presence session.
        """
        payload = {"sessionId": session_id}
        qry = ServiceOperationQuery(self, "clearPresence", None, payload)
        self.context.add_query(qry)
        return self

    def clear_user_preferred_presence(self) -> Self:
        """
        Clear the preferred availability and activity status for a user.
        """
        qry = ServiceOperationQuery(self, "clearUserPreferredPresence")
        self.context.add_query(qry)
        return self

    def set_presence(
        self,
        session_id: str,
        availability: Optional[str] = None,
        activity: Optional[str] = None,
        expiration_duration: Optional[str] = None,
    ):
        """Set the state of a user's presence session as an application.

        Args:
            session_id (str): The ID of the application's presence session.
            availability (str): The base presence information.
            activity (str): The supplemental information to availability.
            expiration_duration (str): The expiration of the app presence session. The value is represented in ISO
              8601 format for durations. If not provided, a default expiration of 5 minutes will be applied.
              The valid duration range is 5-240 minutes (PT5M to PT4H)
        """
        payload = {
            "sessionId": session_id,
            "availability": availability,
            "activity": activity,
            "expirationDuration": expiration_duration,
        }
        qry = ServiceOperationQuery(self, "setPresence", None, payload)
        self.context.add_query(qry)
        return self

    def set_status_message(self, message: str | ItemBody, expiry: Optional[datetime] = None):
        """Set a presence status message for a user. An optional expiration date and time can be supplied.

        Args:
            message (str or ItemBody): Status message item.
            expiry (datetime): Time in which the status message expires. If not provided, the status message
            doesn't expire.
        """
        if not isinstance(message, ItemBody):
            message = ItemBody(message)
        if expiry:
            status_message = PresenceStatusMessage(message=message, expiryDateTime=DateTimeTimeZone.parse(expiry))
        else:
            status_message = PresenceStatusMessage(message=message)
        payload = {"statusMessage": status_message}
        qry = ServiceOperationQuery(self, "setStatusMessage", None, payload)
        self.context.add_query(qry)
        return self

    def set_user_preferred_presence(
        self, availability="Available", activity="Available", expiration_duration: Duration | str | None = None
    ) -> Self:
        """Set the preferred availability and activity status for a user. If the preferred presence of a user is set,
        the user's presence shows as the preferred status.
        Preferred presence takes effect only when at least one presence session exists for the user. Otherwise,
        the user's presence shows as Offline.
        A presence session is created as a result of a successful setPresence operation, or if the user is signed in
        on a Microsoft Teams client.

        Args:
            availability (str): The base presence information.
            activity (str): The supplemental information to availability.
            expiration_duration (str): The expiration of the app presence session. The value is represented in ISO
              8601 format for durations. If not provided, a default expiration of 5 minutes will be applied.
              The valid duration range is 5-240 minutes (PT5M to PT4H)
        """
        payload = {"availability": availability, "activity": activity, "expirationDuration": expiration_duration}
        qry = ServiceOperationQuery(self, "setUserPreferredPresence", None, payload)
        self.context.add_query(qry)
        return self

    @property
    def activity(self) -> Optional[str]:
        """
        The supplemental information to a user's availability.
        Possible values are Available, Away, BeRightBack, Busy, DoNotDisturb, InACall, InAConferenceCall, Inactive,
        InAMeeting, Offline, OffWork, OutOfOffice, PresenceUnknown, Presenting, UrgentInterruptionsOnly.
        """
        return self.properties.get("activity", None)

    @property
    def availability(self) -> Optional[str]:
        """
        The base presence information for a user.
        Possible values are Available, AvailableIdle, Away, BeRightBack, Busy, BusyIdle, DoNotDisturb, Offline,
           PresenceUnknown
        """
        return self.properties.get("availability", None)

    @property
    def sequence_number(self) -> Optional[str]:
        """Gets the sequenceNumber property"""
        return self.properties.get("sequenceNumber", None)

    @property
    def status_message(self) -> PresenceStatusMessage:
        """Gets the statusMessage property"""
        return self.properties.get("statusMessage", PresenceStatusMessage())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Presence"

    @property
    def out_of_office_settings(self) -> OutOfOfficeSettings:
        """Gets the outOfOfficeSettings property"""
        from office365.communications.out_of_office_settings import OutOfOfficeSettings

        return self.properties.get("outOfOfficeSettings", OutOfOfficeSettings())

    @property
    def work_location(self) -> UserWorkLocation:
        """Gets the workLocation property"""
        from office365.communications.user_work_location import UserWorkLocation

        return self.properties.get("workLocation", UserWorkLocation())
