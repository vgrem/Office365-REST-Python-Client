from office365.communications.onlinemeetings.online_meeting import OnlineMeeting
from office365.entity_collection import EntityCollection
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


class OnlineMeetingCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(OnlineMeetingCollection, self).__init__(context, OnlineMeeting, resource_path)

    def create_or_get(self, externalId=None, startDateTime=None, endDateTime=None, subject=None, participants=None,
                      chatInfo=None):
        """Create an onlineMeeting object with a custom specified external ID. If the external ID already exists,
        this API will return the onlineMeeting object with that external ID.

        :param str externalId: The external ID. A custom ID. (Required)
        :param datetime.datetime startDateTime: The meeting start time in UTC.
        :param datetime.datetime endDateTime: The meeting end time in UTC.
        :param str subject: The subject of the online meeting.
        :param list[MeetingParticipant] participants: The participants associated with the online meeting.
             This includes the organizer and the attendees.

        :param ChatInfo chatInfo:
        """
        return_type = OnlineMeeting(self.context)
        payload = {
            "externalId": externalId,
            "startDateTime": startDateTime,
            "endDateTime": endDateTime,
            "subject": subject,
            "chatInfo": chatInfo,
            "participants": participants
        }
        qry = ServiceOperationQuery(self, "createOrGet", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type
