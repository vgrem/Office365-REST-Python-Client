from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.onedrive.workbooks.charts.fill import WorkbookChartFill
    from office365.onedrive.workbooks.charts.line_format import WorkbookChartLineFormat


class WorkbookChartSeriesFormat(Entity):
    """Encapsulates the format properties for the chart series"""

    @property
    def fill(self) -> WorkbookChartFill:
        """Gets the fill property"""
        from office365.onedrive.workbooks.charts.fill import WorkbookChartFill

        return self.properties.get("fill", WorkbookChartFill(self.context, ResourcePath("fill", self.resource_path)))

    @property
    def line(self) -> WorkbookChartLineFormat:
        """Gets the line property"""
        from office365.onedrive.workbooks.charts.line_format import WorkbookChartLineFormat

        return self.properties.get(
            "line", WorkbookChartLineFormat(self.context, ResourcePath("line", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookChartSeriesFormat"
