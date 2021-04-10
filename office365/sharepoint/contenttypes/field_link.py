from office365.sharepoint.base_entity import BaseEntity


class FieldLink(BaseEntity):
    """Specifies a reference to a field or field definition for a content type."""

    @property
    def id(self):
        """Gets a value that specifies the GUID of the FieldLink.

        :rtype: str or None
        """
        return self.properties.get('Id', None)
