from office365.sharepoint.entity import Entity


class PrimaryCityTime(Entity):
    """Represents the date and time, in UTC, of the geographic location."""

    @property
    def location(self):
        """
        :rtype: str or None
        """
        return self.properties.get("Location", None)

    @property
    def time(self):
        """
        :rtype: str or None
        """
        return self.properties.get("Time", None)

    @property
    def utc_offset(self):
        """
        :rtype: str or None
        """
        return self.properties.get("UtcOffset", None)
