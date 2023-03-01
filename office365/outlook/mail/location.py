from office365.runtime.client_value import ClientValue


class Location(ClientValue):
    """Represents location information of an event."""

    def __init__(self, display_name=None):
        """
        :param str display_name: The name associated with the location.
        """
        super(Location, self).__init__()
        self.displayName = display_name
