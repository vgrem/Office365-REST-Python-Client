from office365.runtime.client_value import ClientValue


class RecurrenceRange(ClientValue):
    """
    Describes a date range over which a recurring event. This shared object is used to define the recurrence
    of access reviews, calendar events, and access package assignments in Azure AD.
    """

    def __init__(self, end_date=None):
        """
        :param str end_date:
        """
        self.endDate = end_date
