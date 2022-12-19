from office365.sharepoint.base_entity import BaseEntity


class FieldLink(BaseEntity):
    """Specifies a reference to a field or field definition for a content type."""

    @property
    def id(self):
        """
        Gets a value that specifies the GUID of the FieldLink.

        :rtype: str or None
        """
        return self.properties.get('Id', None)

    @property
    def field_internal_name(self):
        """Gets a value that specifies field internal name

        :rtype: str or None
        """
        return self.properties.get('FieldInternalName', None)

    @property
    def read_only(self):
        """
        :rtype: bool or None
        """
        return self.properties.get('ReadOnly', None)

    @property
    def required(self):
        """
        Gets a value that specifies whether the field (2) requires a value.

        :rtype: bool or None
        """
        return self.properties.get('Required', None)

    @property
    def hidden(self):
        """
        Gets a value that specifies whether the field is displayed in forms that can be edited.

        :rtype: bool or None
        """
        return self.properties.get('Hidden', None)
