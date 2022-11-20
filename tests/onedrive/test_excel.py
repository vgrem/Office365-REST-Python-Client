import os

from office365.onedrive.workbooks.tables.table import WorkbookTable
from tests.graph_case import GraphTestCase

from office365.onedrive.driveitems.driveItem import DriveItem


def upload_excel(target_drive):
    """
    :type target_drive: office365.onedrive.drive.Drive
    """
    path = "{0}/../data/Financial Sample.xlsx".format(os.path.dirname(__file__))
    with open(path, 'rb') as content_file:
        file_content = content_file.read()
    file_name = os.path.basename(path)
    return target_drive.root.upload(file_name, file_content).execute_query()


class TestExcel(GraphTestCase):
    """OneDrive specific test case base class"""
    target_item = None  # type: DriveItem
    table = None  # type: WorkbookTable

    @classmethod
    def setUpClass(cls):
        super(TestExcel, cls).setUpClass()
        cls.target_item = upload_excel(cls.client.me.drive)
        assert cls.target_item.resource_path is not None

    @classmethod
    def tearDownClass(cls):
        cls.target_item.delete_object().execute_query_retry()

    def test1_get_workbook(self):
        workbook = self.__class__.target_item.workbook.get().execute_query_retry()
        self.assertIsNotNone(workbook.resource_path)

    def test2_create_workbook_table(self):
        table = self.__class__.target_item.workbook.tables.add("A10000:C10002", True).execute_query()
        self.assertIsNotNone(table.resource_path)
        self.__class__.table = table

    def test3_list_workbook_tables(self):
        tables = self.__class__.target_item.workbook.tables.get().execute_query_retry()
        self.assertIsNotNone(tables.resource_path)
        self.assertGreater(len(tables), 0)

    def test4_data_body_range(self):
        result = self.__class__.table.data_body_range().execute_query()
        self.assertIsNotNone(result.address)

    def test5_get_table_rows(self):
        rows = self.__class__.table.rows.get().execute_query()
        self.assertIsNotNone(rows.resource_path)

    def test6_create_table_rows(self):
        rows = self.__class__.table.rows.add([["a", "b", "c"]]).execute_query()
        self.assertIsNotNone(rows.resource_path)

    def test7_delete_workbook_table(self):
        self.__class__.table.delete_object().execute_query()

    #def test8_workbook_create_session(self):
    #    result = self.__class__.target_item.workbook.create_session().execute_query()
    #    self.assertIsNotNone(result.value)

    #def test9_workbook_close_session(self):
    #    self.__class__.target_item.workbook.close_session().execute_query()




