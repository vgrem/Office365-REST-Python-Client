from office365.runtime.client_value import ClientValue


class Reminder(ClientValue):
    """A reminder for an event in a user calendar."""

    def __init__(self, event_id=None, event_location=None):
        """

        :param str event_id: The unique ID of the event. Read only.
        :param str event_location:
        """
        super(Reminder, self).__init__()
        self.eventId = event_id
        self.eventLocation = event_location
