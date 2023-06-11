from office365.entity import Entity


class LongRunningOperation(Entity):
    """The status of a long-running operation."""

    @property
    def resource_location(self):
        """URI of the resource that the operation is performed on.
        :rtype: str or None
        """
        return self.properties.get('resourceLocation', None)
