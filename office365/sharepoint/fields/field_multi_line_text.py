from office365.sharepoint.fields.field import Field


class FieldMultiLineText(Field):

    def __init__(self, context):
        """Represents a text field that can contain multiple lines."""
        super().__init__(context)

    @property
    def number_of_lines(self):
        """
        Gets the number of lines to display in the field.
        :return:
        """
        return self.properties.get("NumberOfLines", None)

    @number_of_lines.setter
    def number_of_lines(self, val):
        """
        Set the number of lines to display in the field.
        """
        self.set_property("NumberOfLines", val)
