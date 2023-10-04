import os

from office365.onedrive.driveitems.driveItem import DriveItem
from office365.onedrive.workbooks.tables.table import WorkbookTable
from tests.graph_case import GraphTestCase


def upload_excel(target_drive):
    """
    :type target_drive: office365.onedrive.drive.Drive
    """
    path = "{0}/../data/Financial Sample.xlsx".format(os.path.dirname(__file__))
    with open(path, "rb") as content_file:
        file_content = content_file.read()
    file_name = os.path.basename(path)
    return target_drive.root.upload(file_name, file_content).execute_query()


class TestExcelFunctions(GraphTestCase):
    """OneDrive specific test case base class"""

    target_item = None  # type: DriveItem
    table = None  # type: WorkbookTable

    @classmethod
    def setUpClass(cls):
        super(TestExcelFunctions, cls).setUpClass()
        cls.target_item = upload_excel(cls.client.me.drive)
        assert cls.target_item.resource_path is not None

    @classmethod
    def tearDownClass(cls):
        cls.target_item.delete_object().execute_query_retry()

    def test1_get_abs(self):
        result = self.__class__.target_item.workbook.functions.abs(-2).execute_query()
        self.assertEquals(result.value, 2)
