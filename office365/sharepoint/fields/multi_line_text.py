from __future__ import annotations

from typing import Optional

from office365.sharepoint.fields.field import Field


class FieldMultiLineText(Field):
    """Represents a text field that can contain multiple lines."""

    @property
    def allow_hyperlink(self) -> Optional[bool]:
        """Gets a value that specifies whether a hyperlink is allowed as a value of the field."""
        return self.properties.get("AllowHyperlink", None)

    @allow_hyperlink.setter
    def allow_hyperlink(self, val: bool) -> None:
        """Sets a value that specifies whether a hyperlink is allowed as a value of the field."""
        self.set_property("AllowHyperlink", val)

    @property
    def number_of_lines(self) -> Optional[int]:
        """Gets the number of lines to display in the field."""
        return self.properties.get("NumberOfLines", None)

    @number_of_lines.setter
    def number_of_lines(self, val: int) -> None:
        """Set the number of lines to display in the field."""
        self.set_property("NumberOfLines", val)

    @property
    def restricted_mode(self) -> Optional[bool]:
        """Specifies whether the field supports a subset of rich text formatting."""
        return self.properties.get("RestrictedMode", None)

    @property
    def rich_text(self) -> Optional[bool]:
        """Specifies whether the field supports rich text formatting."""
        return self.properties.get("RichText", None)

    @property
    def unlimited_length_in_document_library(self) -> Optional[bool]:
        """Gets a Boolean value that specifies whether to allow unlimited field length in document libraries."""
        return self.properties.get("UnlimitedLengthInDocumentLibrary", None)

    @property
    def wiki_linking(self) -> Optional[bool]:
        """Specifies whether an implementation-specific mechanism for linking wiki pages is supported.
        It MUST be "false" if RichText is "false"."""
        return self.properties.get("WikiLinking", None)

    @property
    def append_only(self) -> Optional[bool]:
        """Gets the AppendOnly property"""
        return self.properties.get("AppendOnly", None)

    @property
    def is_long_hyperlink(self) -> Optional[bool]:
        """Gets the IsLongHyperlink property"""
        return self.properties.get("IsLongHyperlink", None)
