from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Optional

from typing_extensions import Self

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.onedrive.workbooks.charts.axes import WorkbookChartAxes
from office365.onedrive.workbooks.charts.data_labels import WorkbookChartDataLabels
from office365.onedrive.workbooks.charts.legend.legend import WorkbookChartLegend
from office365.onedrive.workbooks.charts.series.series import WorkbookChartSeries
from office365.onedrive.workbooks.charts.title import WorkbookChartTitle
from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.onedrive.workbooks.charts.area_format import WorkbookChartAreaFormat


class WorkbookChart(Entity):
    """Represents a chart object in a workbook."""

    def image(self, width: int | None = None, height: int | None = None) -> ClientResult[str]:
        """Renders the chart as a base64-encoded image by scaling the chart to fit the specified dimensions.

        Args:
            width (int): Specifies the width of the rendered image in pixels.
            height (int): Specifies the height of the rendered image [ pixels.
        """
        return_type = ClientResult[str](self.context)
        params = {"width": width, "height": height}
        qry = FunctionQuery(self, "image", params, return_type)
        self.context.add_query(qry)
        return return_type

    def set_data(self, source_data: Dict, series_by: str) -> Self:
        """Updates the data source of a chart

        Args:
            source_data (dict):
            series_by (str):
        """
        payload = {"sourceData": source_data, "seriesBy": series_by}
        qry = ServiceOperationQuery(self, "setData", None, payload)
        self.context.add_query(qry)
        return self

    def set_position(self, start_cell: str, end_cell: str) -> Self:
        """Positions the chart relative to cells on the worksheet.

        Args:
            start_cell (str): The start cell. It is where the chart is moved to. The start cell is the top-left or
              top-right cell, depending on the user's right-to-left display settings.
            end_cell (str): The end cell. If specified, the chart's width and height is set to fully cover up this
              cell/range.
        """
        payload = {"startCell": start_cell, "endCell": end_cell}
        qry = ServiceOperationQuery(self, "setPosition", None, payload)
        self.context.add_query(qry)
        return self

    @property
    def axes(self) -> WorkbookChartAxes:
        """Represents chart axes."""
        return self.properties.get(
            "protection",
            WorkbookChartAxes(self.context, ResourcePath("axes", self.resource_path)),
        )

    @odata(name="dataLabels")
    @property
    def data_labels(self) -> WorkbookChartDataLabels:
        """Represents the data labels on the chart."""
        return self.properties.get(
            "dataLabels",
            WorkbookChartDataLabels(self.context, ResourcePath("dataLabels", self.resource_path)),
        )

    @property
    def legend(self) -> WorkbookChartLegend:
        """Represents the legend on the chart."""
        return self.properties.get(
            "legend",
            WorkbookChartLegend(self.context, ResourcePath("legend", self.resource_path)),
        )

    @property
    def series(self) -> EntityCollection[WorkbookChartSeries]:
        """Represents chart series."""
        return self.properties.get(
            "series",
            EntityCollection(
                self.context,
                WorkbookChartSeries,
                ResourcePath("series", self.resource_path),
            ),
        )

    @property
    def title(self) -> WorkbookChartTitle:
        """Represents the title on the chart."""
        return self.properties.get(
            "title",
            WorkbookChartTitle(self.context, ResourcePath("title", self.resource_path)),
        )

    @property
    def worksheet(self):
        """The worksheet containing the current chart."""
        from office365.onedrive.workbooks.worksheets.worksheet import WorkbookWorksheet

        return self.properties.get(
            "worksheet",
            WorkbookWorksheet(self.context, ResourcePath("worksheet", self.resource_path)),
        )

    @property
    def height(self) -> Optional[float]:
        """Gets the height property"""
        return self.properties.get("height", None)

    @property
    def left(self) -> Optional[float]:
        """Gets the left property"""
        return self.properties.get("left", None)

    @property
    def name(self) -> Optional[str]:
        """Gets the name property"""
        return self.properties.get("name", None)

    @property
    def top(self) -> Optional[float]:
        """Gets the top property"""
        return self.properties.get("top", None)

    @property
    def width(self) -> Optional[float]:
        """Gets the width property"""
        return self.properties.get("width", None)

    @property
    def format(self) -> WorkbookChartAreaFormat:
        """Gets the format property"""
        from office365.onedrive.workbooks.charts.area_format import (
            WorkbookChartAreaFormat,
        )

        return self.properties.get(
            "format", WorkbookChartAreaFormat(self.context, ResourcePath("format", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WorkbookChart"
