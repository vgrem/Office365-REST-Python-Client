from office365.communications.onlinemeetings.meeting_participant_info import MeetingParticipantInfo
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


class MeetingParticipants(ClientValue):
    """Participants in a meeting."""

    def __init__(self, organizer=None, attendees=None):
        """
        :param MeetingParticipantInfo organizer:
        :param ClientValueCollection attendees:
        """
        super(MeetingParticipants, self).__init__()
        if organizer is None:
            organizer = MeetingParticipantInfo()
        self.organizer = organizer
        if attendees is None:
            attendees = ClientValueCollection(MeetingParticipantInfo)
        self.attendees = attendees
