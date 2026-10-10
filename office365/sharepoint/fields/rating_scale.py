from __future__ import annotations

from typing import Optional

from office365.sharepoint.fields.multi_choice import FieldMultiChoice


class FieldRatingScale(FieldMultiChoice):
    """Specifies a field (2) that contains rating scale values for a survey list.
    To set properties, call the Update method (section 3.2.5.54.2.1.5)."""

    @property
    def grid_start_number(self) -> Optional[int]:
        """Gets the start number for the rating scale."""
        return self.properties.get("GridStartNumber", None)

    @grid_start_number.setter
    def grid_start_number(self, value: int) -> None:
        """Gets the start number for the rating scale."""
        self.set_property("GridStartNumber", value)

    @property
    def range_count(self) -> Optional[int]:
        """Specifies the number of options in the rating scale."""
        return self.properties.get("RangeCount", None)

    @property
    def grid_end_number(self) -> Optional[int]:
        """Gets the GridEndNumber property"""
        return self.properties.get("GridEndNumber", None)

    @property
    def grid_na_option_text(self) -> Optional[str]:
        """Gets the GridNAOptionText property"""
        return self.properties.get("GridNAOptionText", None)

    @property
    def grid_text_range_average(self) -> Optional[str]:
        """Gets the GridTextRangeAverage property"""
        return self.properties.get("GridTextRangeAverage", None)

    @property
    def grid_text_range_high(self) -> Optional[str]:
        """Gets the GridTextRangeHigh property"""
        return self.properties.get("GridTextRangeHigh", None)

    @property
    def grid_text_range_low(self) -> Optional[str]:
        """Gets the GridTextRangeLow property"""
        return self.properties.get("GridTextRangeLow", None)
