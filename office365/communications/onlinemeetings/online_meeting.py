from office365.communications.onlinemeetings.meeting_participants import MeetingParticipants
from office365.entity import Entity
from office365.outlook.mail.item_body import ItemBody


class OnlineMeeting(Entity):
    """
    Contains information about a meeting, including the URL used to join a meeting,
    the attendees list, and the description.
    """

    @property
    def participants(self):
        """
        The participants associated with the online meeting. This includes the organizer and the attendees.

        """
        return self.properties.get('participants', MeetingParticipants())

    @property
    def subject(self):
        """The subject of the online meeting."""
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
        return self.properties.get("startDateTime", None)

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
        return self.properties.get("endDateTime", None)

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
