from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.onedrive.workbooks.charts.fill import WorkbookChartFill
    from office365.onedrive.workbooks.charts.font import WorkbookChartFont


class WorkbookChartLegendFormat(Entity):
    """Encapsulates the format properties of a chart legend."""

    @property
    def fill(self) -> WorkbookChartFill:
        """Gets the fill property"""
        from office365.onedrive.workbooks.charts.fill import WorkbookChartFill

        return self.properties.get("fill", WorkbookChartFill(self.context, ResourcePath("fill", self.resource_path)))

    @property
    def font(self) -> WorkbookChartFont:
        """Gets the font property"""
        from office365.onedrive.workbooks.charts.font import WorkbookChartFont

        return self.properties.get("font", WorkbookChartFont(self.context, ResourcePath("font", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookChartLegendFormat"
