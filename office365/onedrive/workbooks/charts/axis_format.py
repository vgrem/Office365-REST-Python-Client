from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.onedrive.workbooks.charts.font import WorkbookChartFont
    from office365.onedrive.workbooks.charts.line_format import WorkbookChartLineFormat


class WorkbookChartAxisFormat(Entity):
    @property
    def font(self) -> WorkbookChartFont:
        """Gets the font property"""
        from office365.onedrive.workbooks.charts.font import WorkbookChartFont

        return self.properties.get("font", WorkbookChartFont(self.context, ResourcePath("font", self.resource_path)))

    @property
    def line(self) -> WorkbookChartLineFormat:
        """Gets the line property"""
        from office365.onedrive.workbooks.charts.line_format import WorkbookChartLineFormat

        return self.properties.get(
            "line", WorkbookChartLineFormat(self.context, ResourcePath("line", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookChartAxisFormat"
