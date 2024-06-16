from office365.entity import Entity
from office365.onedrive.workbooks.charts.axes import WorkbookChartAxes
from office365.onedrive.workbooks.charts.data_labels import WorkbookChartDataLabels
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery


class WorkbookChart(Entity):
    """Represents a chart object in a workbook."""

    def set_position(self, startCell, endCell):
        """Positions the chart relative to cells on the worksheet.
        :param str startCell: The start cell. It is where the chart is moved to. The start cell is the top-left or
             top-right cell, depending on the user's right-to-left display settings.
        :param str endCell: The end cell. If specified, the chart's width and height is set to fully cover up
             this cell/range.
        """
        payload = {"startCell": startCell, "endCell": endCell}
        qry = ServiceOperationQuery(self, "setPosition", None, payload)
        self.context.add_query(qry)
        return self

    @property
    def axes(self):
        """Represents chart axes."""
        return self.properties.get(
            "protection",
            WorkbookChartAxes(self.context, ResourcePath("axes", self.resource_path)),
        )

    @property
    def data_labels(self):
        """Represents the datalabels on the chart."""
        return self.properties.get(
            "dataLabels",
            WorkbookChartDataLabels(
                self.context, ResourcePath("dataLabels", self.resource_path)
            ),
        )

    @property
    def worksheet(self):
        """The worksheet containing the current chart."""
        from office365.onedrive.workbooks.worksheets.worksheet import WorkbookWorksheet

        return self.properties.get(
            "worksheet",
            WorkbookWorksheet(
                self.context, ResourcePath("worksheet", self.resource_path)
            ),
        )

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "dataLabels": self.data_labels,
            }
            default_value = property_mapping.get(name, None)
        return super(WorkbookChart, self).get_property(name, default_value)
