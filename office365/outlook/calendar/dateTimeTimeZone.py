import pytz
from office365.runtime.client_value import ClientValue


class DateTimeTimeZone(ClientValue):
    """Describes the date, time, and time zone of a point in time."""

    def __init__(self, dateTime, timeZone=None):
        """

        :param str timeZone: Represents a time zone, for example, "Pacific Standard Time".
        :param str dateTime: A single point of time in a combined date and time representation ({date}T{time};
            for example, 2017-08-29T04:00:00.0000000).
        """
        super(DateTimeTimeZone, self).__init__()
        self.dateTime = dateTime
        self.timeZone = timeZone

    @staticmethod
    def parse(dt):
        """
        :type dt: datetime.datetime
        """
        local_dt = dt.replace(tzinfo=pytz.utc)
        return DateTimeTimeZone(dateTime=local_dt.isoformat(), timeZone=local_dt.strftime('%Z'))
