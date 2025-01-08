from office365.onedrive.driveitems.driveItem import DriveItem
from office365.onedrive.workbooks.names.named_item import WorkbookNamedItem
from office365.onedrive.workbooks.ranges.range import WorkbookRange
from tests import create_unique_name
from tests.graph_case import GraphTestCase
from tests.onedrive.test_excel import upload_excel


class TestExcelRanges(GraphTestCase):
    excel_file = None  # type: DriveItem
    named_item = None  # type: WorkbookNamedItem
    range = None  # type: WorkbookRange
    sheet_name = create_unique_name("Sheet")

    @classmethod
    def setUpClass(cls):
        super(TestExcelRanges, cls).setUpClass()
        cls.excel_file = upload_excel(cls.client.me.drive)
        assert cls.excel_file.resource_path is not None

    @classmethod
    def tearDownClass(cls):
        cls.excel_file.delete_object().execute_query_retry()

    def test1_name_create(self):
        result = self.__class__.excel_file.workbook.names.add(
            "test5", "=Sheet1!$F$15:$N$27", "Comment for the named item"
        ).execute_query()
        self.assertIsNotNone(result.resource_path)
        self.__class__.named_item = result

    def test2_names_get(self):
        result = self.__class__.named_item.get().execute_query_retry(2)
        self.assertIsNotNone(result.resource_path)

    def test3_list_range(self):
        result = self.__class__.named_item.range().execute_query()
        self.assertIsNotNone(result.address)
        self.__class__.range = result

    def test4_last_row(self):
        result = self.__class__.range.last_row().execute_query()
        self.assertIsNotNone(result.address)

    # def test4_insert_range(self):
    #    result = self.__class__.range.insert("Right").execute_query()
    #    self.assertIsNotNone(result.address)

    def test6_used_range(self):
        result = self.__class__.range.used_range().execute_query()
        self.assertIsNotNone(result.address)

    def test7_clear_range(self):
        result = self.__class__.range.clear().execute_query()
        self.assertIsNotNone(result.address)
