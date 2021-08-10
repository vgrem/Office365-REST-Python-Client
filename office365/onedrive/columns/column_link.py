from office365.entity import Entity


class ColumnLink(Entity):
    """A columnLink on a contentType attaches a site columnDefinition to that content type."""

    @property
    def name(self):
        """The name of the column in this content type.

        :rtype: str or None
        """
        return self.properties.get("name", None)
