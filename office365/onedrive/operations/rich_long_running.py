from office365.onedrive.operations.long_running import LongRunningOperation


class RichLongRunningOperation(LongRunningOperation):
    """Represents the status of a long-running operation on a site or a list."""

    @property
    def resource_id(self):
        """The unique identifier for the result.
        :rtype: str or None
        """
        return self.properties.get('resourceId', None)
