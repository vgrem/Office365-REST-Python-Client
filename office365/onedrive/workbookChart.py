from office365.entity import Entity
from office365.runtime.client_object_collection import ClientObjectCollection


class WorkbookChart(Entity):
    pass


class WorkbookChartCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(WorkbookChartCollection, self).__init__(context, WorkbookChart, resource_path)


class WorkbookChartAxes(Entity):
    pass


class WorkbookChartDataLabels(Entity):
    pass


class WorkbookChartAreaFormat(Entity):
    pass


class WorkbookChartLegend(Entity):
    pass


class WorkbookChartSeries(Entity):
    pass
