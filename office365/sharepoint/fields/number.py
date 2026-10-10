from __future__ import annotations

from typing import Optional

from office365.sharepoint.fields.field import Field


class FieldNumber(Field):
    """Specifies a field that contains number values. To set properties, call the Update method
    (section 3.2.5.53.2.1.5)."""

    @property
    def display_format(self) -> Optional[int]:
        """Gets the number of decimal places to be used when displaying the field."""
        return self.properties.get("DisplayFormat", None)

    @property
    def comma_separator(self) -> Optional[str]:
        """Gets the separator used to format the value of the field."""
        return self.properties.get("CommaSeparator", None)

    @comma_separator.setter
    def comma_separator(self, value: str) -> None:
        """Sets the separator used to format the value of the field."""
        self.set_property("CommaSeparator", value)

    @property
    def show_as_percentage(self) -> Optional[bool]:
        """Gets a Boolean value that specifies whether to render the field as a percentage."""
        return self.properties.get("ShowAsPercentage", None)

    @show_as_percentage.setter
    def show_as_percentage(self, value: bool) -> None:
        """Sets a Boolean value that specifies whether to render the field as a percentage."""
        self.set_property("ShowAsPercentage", value)

    @property
    def custom_unit_name(self) -> Optional[str]:
        """Gets the CustomUnitName property"""
        return self.properties.get("CustomUnitName", None)

    @property
    def custom_unit_on_right(self) -> Optional[bool]:
        """Gets the CustomUnitOnRight property"""
        return self.properties.get("CustomUnitOnRight", None)

    @property
    def maximum_value(self) -> Optional[float]:
        """Gets the MaximumValue property"""
        return self.properties.get("MaximumValue", None)

    @property
    def minimum_value(self) -> Optional[float]:
        """Gets the MinimumValue property"""
        return self.properties.get("MinimumValue", None)

    @property
    def unit(self) -> Optional[str]:
        """Gets the Unit property"""
        return self.properties.get("Unit", None)
