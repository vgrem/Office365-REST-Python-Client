from office365.runtime.client_value import ClientValue


class RecurrencePattern(ClientValue):
    """Describes the frequency by which a recurring event repeats."""

    def __init__(self, day_of_month=None):
        """
        :param int day_of_month: The day of the month on which the event occurs. Required if type is absoluteMonthly
            or absoluteYearly.
        """
        self.dayOfMonth = day_of_month

