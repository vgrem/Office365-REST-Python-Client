from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.onedrive.workbooks.charts.data_label_format import (
        WorkbookChartDataLabelFormat,
    )


class WorkbookChartDataLabels(Entity):
    """Represents a collection of all the data labels on a chart point."""

    @property
    def position(self) -> Optional[str]:
        """DataLabelPosition value that represents the position of the data label."""
        return self.properties.get("position", None)

    @property
    def separator(self) -> Optional[str]:
        """String representing the separator used for the data labels on a chart."""
        return self.properties.get("separator", None)

    @property
    def show_bubble_size(self) -> Optional[bool]:
        """Gets the showBubbleSize property"""
        return self.properties.get("showBubbleSize", None)

    @property
    def show_category_name(self) -> Optional[bool]:
        """Gets the showCategoryName property"""
        return self.properties.get("showCategoryName", None)

    @property
    def show_legend_key(self) -> Optional[bool]:
        """Gets the showLegendKey property"""
        return self.properties.get("showLegendKey", None)

    @property
    def show_percentage(self) -> Optional[bool]:
        """Gets the showPercentage property"""
        return self.properties.get("showPercentage", None)

    @property
    def show_series_name(self) -> Optional[bool]:
        """Gets the showSeriesName property"""
        return self.properties.get("showSeriesName", None)

    @property
    def show_value(self) -> Optional[bool]:
        """Gets the showValue property"""
        return self.properties.get("showValue", None)

    @property
    def format(self) -> WorkbookChartDataLabelFormat:
        """Gets the format property"""
        from office365.onedrive.workbooks.charts.data_label_format import (
            WorkbookChartDataLabelFormat,
        )

        return self.properties.get(
            "format", WorkbookChartDataLabelFormat(self.context, ResourcePath("format", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookChartDataLabels"
