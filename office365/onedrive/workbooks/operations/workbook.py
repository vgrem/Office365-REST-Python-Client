from office365.entity import Entity


class WorkbookOperation(Entity):
    """Represents the status of a long-running workbook operation"""

    @property
    def resource_location(self):
        """The resource URI for the result.

        :rtype: str or None
        """
        return self.properties.get("resourceLocation", None)
