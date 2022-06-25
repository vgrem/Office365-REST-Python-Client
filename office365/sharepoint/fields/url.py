from office365.sharepoint.fields.field import Field


class FieldUrl(Field):
    """Specifies a fields that contains a URL."""

    @property
    def display_format(self):
        """
        Gets the number of decimal places to be used when displaying the field.

        :rtype: int or None
        """
        return self.properties.get('DisplayFormat', None)
