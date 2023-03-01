from office365.outlook.calendar.time_zone_base import TimeZoneBase
from office365.runtime.client_value import ClientValue


class WorkingHours(ClientValue):
    """
    Represents the days of the week and hours in a specific time zone that the user works.
    """

    def __init__(self, timezone=TimeZoneBase()):
        """
        :param TimeZoneBase timezone: The time zone to which the working hours apply.
        """
        self.timeZone = timezone
