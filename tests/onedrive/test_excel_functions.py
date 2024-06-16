import os

from office365.onedrive.driveitems.driveItem import DriveItem
from office365.onedrive.workbooks.tables.table import WorkbookTable
from tests.graph_case import GraphTestCase


class TestExcelFunctions(GraphTestCase):
    """OneDrive specific test case base class"""

    target_item = None  # type: DriveItem
    table = None  # type: WorkbookTable

    @classmethod
    def setUpClass(cls):
        super(TestExcelFunctions, cls).setUpClass()
        path = "{0}/../data/Financial Sample.xlsx".format(os.path.dirname(__file__))
        cls.target_item = cls.client.me.drive.root.upload_file(path).execute_query()
        assert cls.target_item.resource_path is not None

    @classmethod
    def tearDownClass(cls):
        cls.target_item.delete_object().execute_query_retry()

    def test1_get_abs(self):
        result = self.__class__.target_item.workbook.functions.abs(-2).execute_query()
        self.assertEqual(result.value, 2)

    # def test2_get_days(self):
    #    start = datetime.now()
    #    end = start + timedelta(days=10)
    #    result = self.__class__.target_item.workbook.functions.days(
    #        start, end
    #    ).execute_query()
    #    self.assertGreater(result.value, 1)
