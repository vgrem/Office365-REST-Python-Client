from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.onedrive.workbooks.charts.legend.format import (
        WorkbookChartLegendFormat,
    )


class WorkbookChartLegend(Entity):
    """Represents the legend in a chart."""

    @property
    def overlay(self) -> Optional[bool]:
        """Indicates whether the chart legend should overlap with the main body of the chart."""
        return self.properties.get("overlay", None)

    @property
    def position(self) -> Optional[str]:
        """Represents the position of the legend on the chart.
        The possible values are: Top, Bottom, Left, Right, Corner, Custom."""
        return self.properties.get("position", None)

    @property
    def visible(self) -> Optional[bool]:
        """Indicates whether the chart legend is visible."""
        return self.properties.get("visible", None)

    @property
    def format(self) -> WorkbookChartLegendFormat:
        """Gets the format property"""
        from office365.onedrive.workbooks.charts.legend.format import (
            WorkbookChartLegendFormat,
        )

        return self.properties.get(
            "format", WorkbookChartLegendFormat(self.context, ResourcePath("format", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookChartLegend"
