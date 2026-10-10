from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from office365.communications.onlinemeetings.online_meeting import OnlineMeeting
from office365.communications.onlinemeetings.participants import MeetingParticipants
from office365.communications.onlinemeetings.recordings.call import CallRecording
from office365.entity_collection import EntityCollection
from office365.runtime.client_value import ClientValue
from office365.runtime.queries.service_operation import ServiceOperationQuery


@dataclass
class ChatInfo(ClientValue):
    messageId: str | None = None

    replyChainMessageId: str | None = None

    threadId: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ChatInfo"


class OnlineMeetingCollection(EntityCollection[OnlineMeeting]):
    """ """

    def __init__(self, context, resource_path=None):
        super().__init__(context, OnlineMeeting, resource_path)

    def create(
        self,
        subject: str,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        **kwargs,
    ) -> OnlineMeeting:
        """Create an online meeting on behalf of a user by using the object ID (OID) in the user token.

        Args:
            start_datetime (datetime): The meeting start time in UTC.
            end_datetime (datetime): The meeting end time in UTC.
            subject (str): The subject of the online meeting.
        """
        return super().add(subject=subject, startDateTime=start_datetime, endDateTime=end_datetime, **kwargs)

    def create_or_get(
        self,
        external_id: str | None = None,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
        subject: str | None = None,
        participants: MeetingParticipants | None = None,
        chat_info: ChatInfo | None = None,
    ) -> OnlineMeeting:
        """Create an onlineMeeting object with a custom specified external ID. If the external ID already exists,
        this API will return the onlineMeeting object with that external ID.

        Args:
            external_id (str): The external ID. A custom ID. (Required)
            start_datetime (datetime.datetime): The meeting start time in UTC.
            end_datetime (datetime.datetime): The meeting end time in UTC.
            subject (str): The subject of the online meeting.
            participants (MeetingParticipants): The participants associated with the online meeting.
              This includes the organizer and the attendees.
            chat_info (ChatInfo):
        """
        return_type = OnlineMeeting(self.context)
        self.add_child(return_type)
        payload = {
            "externalId": external_id,
            "startDateTime": start_datetime,
            "endDateTime": end_datetime,
            "subject": subject,
            "chatInfo": chat_info,
            "participants": participants,
        }
        qry = ServiceOperationQuery(self, "createOrGet", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_all_recordings(
        self,
        meeting_organizer_user_id: str,
        start_datetime: datetime | None = None,
        end_datetime: datetime | None = None,
    ) -> EntityCollection[CallRecording]:
        """Get all recordings from scheduled onlineMeeting instances for which the specified user is the organizer.
        This API currently doesn't support getting call recordings from channel meetings.

        Args:
            meeting_organizer_user_id (str): The user identifier of the meeting organizer to filter for artifacts for
              meetings organized by the given user identifier.
            start_datetime (datetime.datetime): Optional parameter to filter for artifacts created after the given
              start date. The timestamp type represents date and time information using ISO 8601 format and is always
              in UTC
            end_datetime (datetime.datetime): Optional parameter to filter for artifacts created before the given end
              date. The timestamp type represents date and time information using ISO 8601 format and is always in UTC
        """
        return_type = EntityCollection(self.context, CallRecording)
        payload = {
            "meetingOrganizerUserId": meeting_organizer_user_id,
            "startDateTime": start_datetime,
            "endDateTime": end_datetime,
        }
        qry = ServiceOperationQuery(self, "getAllRecordings", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type
