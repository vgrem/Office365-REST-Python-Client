from office365.sharepoint.fields.field import Field


class FieldText(Field):

    def __init__(self, context):
        super(FieldText, self).__init__(context)

    @property
    def max_length(self):
        """Gets a value that specifies the maximum number of characters allowed in the value of the field."""
        return self.properties.get('MaxLength', None)

    @max_length.setter
    def max_length(self, val):
        """Sets a value that specifies the maximum number of characters allowed in the value of the field."""
        self.set_property("MaxLength", val, True)
