from office365.runtime.client_value import ClientValue


class TimeZoneInformation(ClientValue):
    """Provides information used to define a time zone."""

    def __init__(self, Bias=None, StandardBias=None, DaylightBias=None):
        """

        :param int Bias: Gets the bias in the number of minutes that the time zone differs from
            Coordinated Universal Time (UTC).
        :param DaylightBias: Gets the bias in the number of minutes that daylight time for the time zone
            differs from Coordinated Universal Time (UTC).
        :param StandardBias: Gets the bias in the number of minutes that standard time for the time zone differs
             from coordinated universal time (UTC).
        """
        super(TimeZoneInformation, self).__init__()
        self.Bias = Bias
        self.DaylightBias = DaylightBias
        self.StandardBias = StandardBias
