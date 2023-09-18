from office365.outlook.calendar.timezones.base import TimeZoneBase


class CustomTimeZone(TimeZoneBase):
    """
    Represents a time zone where the transition from standard to daylight saving time, or vice versa is not standard.
    """
