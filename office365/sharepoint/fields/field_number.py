from office365.sharepoint.fields.field import Field


class FieldNumber(Field):
    """Specifies a field (2) that contains number values. To set properties, call the Update method
    (section 3.2.5.53.2.1.5)."""

    @property
    def comma_separator(self):
        """
        Gets the separator used to format the value of the field.

        :rtype: str or None
        """
        return self.properties.get('CommaSeparator', None)

    @comma_separator.setter
    def comma_separator(self, value):
        """
        Sets the separator used to format the value of the field.

        :type value: str
        """
        self.set_property('CommaSeparator', value)
