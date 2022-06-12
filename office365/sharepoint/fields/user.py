from office365.sharepoint.fields.lookup import FieldLookup


class FieldUser(FieldLookup):
    """Specifies a field that contains a user."""

    @property
    def presence(self):
        """Gets a value that specifies whether presence is enabled on the field.

        :rtype: bool or None
        """
        return self.properties.get('Presence', None)

    @presence.setter
    def presence(self, val):
        """Sets a value that specifies whether presence is enabled on the field.
        """
        self.properties.get('Presence', val)

    @property
    def allow_display(self):
        """Gets a value that specifies whether to display the name of the user in a survey list.

        :rtype: bool or None
        """
        return self.properties.get('AllowDisplay', None)

    @allow_display.setter
    def allow_display(self, val):
        """Sets a value that specifies whether to display the name of the user in a survey list.
        """
        self.properties.get('AllowDisplay', val)

    @property
    def selection_group(self):
        """Gets a value that specifies the identifier of the SharePoint group whose members can be selected
            as values of the field.

        :rtype: int or None
        """
        return self.properties.get('SelectionGroup', None)

    @selection_group.setter
    def selection_group(self, val):
        """Sets a value that specifies the identifier of the SharePoint group whose members can be selected as
            values of the field.
        """
        self.properties.get('SelectionGroup', val)
