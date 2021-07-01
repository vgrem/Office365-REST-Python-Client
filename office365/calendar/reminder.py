from office365.runtime.client_value import ClientValue


class Reminder(ClientValue):
    """A reminder for an event in a user calendar."""

    def __init__(self, eventId=None):
        """

        :param str eventId: The unique ID of the event. Read only.
        """
        super(Reminder, self).__init__()
        self.eventId = eventId
