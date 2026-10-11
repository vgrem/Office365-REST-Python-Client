from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.onedrive.workbooks.charts.axis_format import WorkbookChartAxisFormat
    from office365.onedrive.workbooks.charts.axis_title import WorkbookChartAxisTitle
    from office365.onedrive.workbooks.charts.gridlines import WorkbookChartGridlines
    from office365.runtime.types.json import Json


class WorkbookChartAxis(Entity):
    """Represents a single axis in a chart."""

    @property
    def major_unit(self) -> Json:
        """Gets the majorUnit property"""
        from office365.runtime.types.json import Json

        return self.properties.get("majorUnit", Json())

    @property
    def maximum(self) -> Json:
        """Gets the maximum property"""
        from office365.runtime.types.json import Json

        return self.properties.get("maximum", Json())

    @property
    def minimum(self) -> Json:
        """Gets the minimum property"""
        from office365.runtime.types.json import Json

        return self.properties.get("minimum", Json())

    @property
    def minor_unit(self) -> Json:
        """Gets the minorUnit property"""
        from office365.runtime.types.json import Json

        return self.properties.get("minorUnit", Json())

    @property
    def format(self) -> WorkbookChartAxisFormat:
        """Gets the format property"""
        from office365.onedrive.workbooks.charts.axis_format import WorkbookChartAxisFormat

        return self.properties.get(
            "format", WorkbookChartAxisFormat(self.context, ResourcePath("format", self.resource_path))
        )

    @property
    def major_gridlines(self) -> WorkbookChartGridlines:
        """Gets the majorGridlines property"""
        from office365.onedrive.workbooks.charts.gridlines import WorkbookChartGridlines

        return self.properties.get(
            "majorGridlines", WorkbookChartGridlines(self.context, ResourcePath("majorGridlines", self.resource_path))
        )

    @property
    def minor_gridlines(self) -> WorkbookChartGridlines:
        """Gets the minorGridlines property"""
        from office365.onedrive.workbooks.charts.gridlines import WorkbookChartGridlines

        return self.properties.get(
            "minorGridlines", WorkbookChartGridlines(self.context, ResourcePath("minorGridlines", self.resource_path))
        )

    @property
    def title(self) -> WorkbookChartAxisTitle:
        """Gets the title property"""
        from office365.onedrive.workbooks.charts.axis_title import WorkbookChartAxisTitle

        return self.properties.get(
            "title", WorkbookChartAxisTitle(self.context, ResourcePath("title", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookChartAxis"
