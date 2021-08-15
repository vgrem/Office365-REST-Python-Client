from office365.onenote.entity_base_model import OnenoteEntityBaseModel


class OnenoteEntitySchemaObjectModel(OnenoteEntityBaseModel):
    """This is a base type for OneNote entities."""

    @property
    def created_datetime(self):
        """
        The date and time when the page was created. The timestamp represents date and time information using
        ISO 8601 format and is always in UTC time. For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z.

        :rtype: str or None
        """
        return self.properties("createdDateTime", None)
