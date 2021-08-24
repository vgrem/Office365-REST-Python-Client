from office365.entity import Entity


class Presence(Entity):
    """Contains information about a user's presence, including their availability and user activity."""

    @property
    def activity(self):
        """
        :rtype: str or None
        """
        return self.properties.get("activity", None)

    @property
    def availability(self):
        """
        :rtype: str or None
        """
        return self.properties.get("availability", None)
