from office365.runtime.client_value import ClientValue


class TimeSlot(ClientValue):
    """Represents a time slot for a meeting."""

    def __init__(self, start, end):
        """

        :param datetime.datetime start: The date, time, and time zone that a period begins.
        :param datetime.datetime end: The date, time, and time zone that a period ends.
        """
        super(TimeSlot, self).__init__()
        self.start = start
        self.end = end
