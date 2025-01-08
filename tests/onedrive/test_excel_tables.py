from examples.sharepoint.lists.assessment.broken_tax_field_value import fields
from office365.onedrive.driveitems.driveItem import DriveItem
from office365.onedrive.workbooks.sort_field import WorkbookSortField
from office365.onedrive.workbooks.tables.table import WorkbookTable
from office365.onedrive.workbooks.worksheets.worksheet import WorkbookWorksheet
from tests.graph_case import GraphTestCase


class TestExcelTables(GraphTestCase):
    excel_file = None  # type: DriveItem
    worksheet = None  # type: WorkbookWorksheet
    table = None  # type: WorkbookTable

    @classmethod
    def setUpClass(cls):
        super(TestExcelTables, cls).setUpClass()
        path = "../data/Financial Sample.xlsx"
        cls.excel_file = cls.client.me.drive.root.upload_file(path).execute_query()
        assert cls.excel_file.resource_path is not None
        cls.worksheet = (
            cls.excel_file.workbook.worksheets["Sheet1"].get().execute_query()
        )
        assert cls.worksheet.resource_path is not None
        cls.table = cls.worksheet.tables["financials"].get().execute_query()
        assert cls.table.resource_path is not None

    @classmethod
    def tearDownClass(cls):
        cls.excel_file.delete_object().execute_query_retry()

    def test1_sort_apply(self):
        sort_fields = [WorkbookSortField()]
        result = self.__class__.table.sort.apply(sort_fields).execute_query()
        self.assertIsNotNone(result.resource_path)
