import os

from office365.onedrive.driveitems.driveItem import DriveItem
from office365.onedrive.workbooks.charts.chart import WorkbookChart
from office365.onedrive.workbooks.worksheets.worksheet import WorkbookWorksheet
from tests.graph_case import GraphTestCase


class TestExcelCharts(GraphTestCase):
    excel_file = None  # type: DriveItem
    worksheet = None  # type: WorkbookWorksheet
    chart = None  # type: WorkbookChart

    @classmethod
    def setUpClass(cls):
        super(TestExcelCharts, cls).setUpClass()
        path = "{0}/../../examples/data/templates/Weight loss tracker.xlsx".format(
            os.path.dirname(__file__)
        )
        cls.excel_file = cls.client.me.drive.root.upload_file(path).execute_query()
        assert cls.excel_file.resource_path is not None
        cls.worksheet = (
            cls.excel_file.workbook.worksheets["Weight loss tracker"]
            .get()
            .execute_query()
        )
        assert cls.worksheet.resource_path is not None

    @classmethod
    def tearDownClass(cls):
        cls.excel_file.delete_object().execute_query_retry()

    def test1_list_charts(self):
        result = self.__class__.worksheet.charts.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test2_get_chart_by_name(self):
        result = self.__class__.worksheet.charts["Weight Tracker"].get().execute_query()
        self.assertIsNotNone(result.resource_path)
        self.__class__.chart = result

    def test3_get_image(self):
        result = self.__class__.chart.image().execute_query()
        self.assertIsNotNone(result.value)
