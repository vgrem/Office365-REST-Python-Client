from office365.sharepoint.entity import Entity


class FieldLink(Entity):
    """Specifies a reference to a field or field definition for a content type."""

    @property
    def id(self):
        """
        Gets a value that specifies the GUID of the FieldLink.
        :rtype: str or None
        """
        return self.properties.get("Id", None)

    @property
    def field_internal_name(self):
        """Gets a value that specifies field internal name
        :rtype: str or None
        """
        return self.properties.get("FieldInternalName", None)

    @property
    def read_only(self):
        """
        :rtype: bool or None
        """
        return self.properties.get("ReadOnly", None)

    @property
    def hidden(self):
        """
        Gets a value that specifies whether the field is displayed in forms that can be edited.
        :rtype: bool or None
        """
        return self.properties.get("Hidden", None)

    @property
    def required(self):
        """
        Gets a value that specifies whether the field (2) requires a value.
        :rtype: bool or None
        """
        return self.properties.get("Required", None)

    @property
    def show_in_display_form(self):
        """
        A Boolean value that indicates whether this field is shown in the display form.
        :rtype: bool or None
        """
        return self.properties.get("ShowInDisplayForm", None)
