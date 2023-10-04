from datetime import datetime

from office365.communications.onlinemeetings.participants import MeetingParticipants
from office365.entity import Entity
from office365.outlook.mail.item_body import ItemBody
from office365.runtime.types.collections import StringCollection


class OnlineMeeting(Entity):
    """
    Contains information about a meeting, including the URL used to join a meeting,
    the attendees list, and the description.
    """

    @property
    def allow_attendee_to_enable_camera(self):
        """
        Indicates whether attendees can turn on their camera.
        :rtype: str
        """
        return self.properties.get("allowAttendeeToEnableCamera", None)

    @property
    def allow_attendee_to_enable_mic(self):
        """
        Indicates whether attendees can turn on their microphone.
        :rtype: str
        """
        return self.properties.get("allowAttendeeToEnableMic", None)

    @property
    def allowed_presenters(self):
        """
        Specifies who can be a presenter in a meeting. Possible values are listed in the following table.
        """
        return self.properties.get("allowedPresenters", StringCollection())

    @property
    def allow_meeting_chat(self):
        """
        Specifies the mode of meeting chat.
        :rtype: str or None
        """
        return self.properties.get("allowMeetingChat", None)

    @property
    def allow_participants_to_change_name(self):
        """
        Specifies if participants are allowed to rename themselves in an instance of the meeting.
        :rtype: bool or None
        """
        return self.properties.get("allowParticipantsToChangeName", None)

    @property
    def attendee_report(self):
        """
        The content stream of the attendee report of a Microsoft Teams live event.
        :rtype: bytes or None
        """
        return self.properties.get("attendeeReport", None)

    @property
    def participants(self):
        """
        The participants associated with the online meeting. This includes the organizer and the attendees.
        """
        return self.properties.get("participants", MeetingParticipants())

    @property
    def subject(self):
        """
        The subject of the online meeting.
        :rtype: str or None
        """
        return self.properties.get("subject", None)

    @subject.setter
    def subject(self, value):
        """
        :type value: str
        """
        self.set_property("subject", value)

    @property
    def start_datetime(self):
        """Gets the meeting start time in UTC."""
        return self.properties.get("startDateTime", datetime.min)

    @start_datetime.setter
    def start_datetime(self, value):
        """
        Sets the meeting start time in UTC.
        :type value: datetime.datetime
        """
        self.set_property("startDateTime", value.isoformat())

    @property
    def end_datetime(self):
        """Gets the meeting end time in UTC."""
        return self.properties.get("endDateTime", datetime.min)

    @end_datetime.setter
    def end_datetime(self, value):
        """
        Sets the meeting end time in UTC.
        :type value: datetime.datetime
        """
        self.set_property("endDateTime", value.isoformat())

    @property
    def join_information(self):
        """The join URL of the online meeting. Read-only."""
        return self.properties.get("joinInformation", ItemBody())

    @property
    def join_web_url(self):
        """The join URL of the online meeting. Read-only."""
        return self.properties.get("joinWebUrl", None)

    @property
    def video_teleconference_id(self):
        """The video teleconferencing ID."""
        return self.properties.get("videoTeleconferenceId", None)

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "endDateTime": self.end_datetime,
                "joinInformation": self.join_information,
                "startDateTime": self.start_datetime,
            }
            default_value = property_mapping.get(name, None)
        return super(OnlineMeeting, self).get_property(name, default_value)
