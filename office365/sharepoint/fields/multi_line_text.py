from typing import Optional

from office365.sharepoint.fields.field import Field


class FieldMultiLineText(Field):
    def __init__(self, context):
        """Represents a text field that can contain multiple lines."""
        super(FieldMultiLineText, self).__init__(context)

    @property
    def allow_hyperlink(self):
        # type: () -> Optional[bool]
        """Gets a value that specifies whether a hyperlink is allowed as a value of the field."""
        return self.properties.get("AllowHyperlink", None)

    @allow_hyperlink.setter
    def allow_hyperlink(self, val):
        # type: (bool) -> None
        """Sets a value that specifies whether a hyperlink is allowed as a value of the field."""
        self.set_property("AllowHyperlink", val)

    @property
    def number_of_lines(self):
        # type: () -> Optional[int]
        """Gets the number of lines to display in the field."""
        return self.properties.get("NumberOfLines", None)

    @number_of_lines.setter
    def number_of_lines(self, val):
        # type: (int) -> None
        """Set the number of lines to display in the field."""
        self.set_property("NumberOfLines", val)
