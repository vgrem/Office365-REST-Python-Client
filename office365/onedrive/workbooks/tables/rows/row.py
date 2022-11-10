from office365.entity import Entity


class WorkbookTableRow(Entity):
    """Represents a row in a table."""

    @property
    def index(self):
        """Returns the index number of the row within the rows collection of the table. Zero-indexed."""
        return self.properties.get("index", None)

    @property
    def values(self):
        """
        Represents the raw values of the specified range. The data returned could be of type string, number,
        or a boolean. Cell that contain an error will return the error string.
        """
        return self.properties.get("values", None)

