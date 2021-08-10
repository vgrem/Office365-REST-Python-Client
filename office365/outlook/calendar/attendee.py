from office365.outlook.calendar.attendee_base import AttendeeBase
from office365.outlook.calendar.email_address import EmailAddress


class Attendee(AttendeeBase):
    """An event attendee. This can be a person or resource such as a meeting room or equipment,
    that has been set up as a resource on the Exchange server for the tenant."""

    def __init__(self, emailAddress=EmailAddress(), attendee_type=None, proposedNewTime=None, status=None):
        """

        :param office365.mail.emailAddress.EmailAddress emailAddress emailAddress:
        :param office365.calendar.timeSlot.TimeSlot proposedNewTime:
        :param str status: The attendee's response (none, accepted, declined, etc.) for the event and date-time
            that the response was sent.
        """
        super(Attendee, self).__init__(emailAddress, attendee_type)
        self.proposedNewTime = proposedNewTime
        self.status = status
