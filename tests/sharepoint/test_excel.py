import os

from office365.sharepoint.files.file import File
from tests.sharepoint.sharepoint_case import SPTestCase


def upload_excel_file(context):
    """

    :type context: office365.sharepoint.client_context.ClientContext
    """
    path = "{0}/../data/Financial Sample.xlsx".format(os.path.dirname(__file__))
    with open(path, 'rb') as content_file:
        file_content = content_file.read()
    file_name = os.path.basename(path)
    target_folder = context.web.lists.get_by_title("Documents").root_folder
    uploaded_file = target_folder.upload_file(file_name, file_content)
    return uploaded_file


class TestSharePointExcel(SPTestCase):
    target_file = None  # type: File

    @classmethod
    def setUpClass(cls):
        super(TestSharePointExcel, cls).setUpClass()
        cls.target_file = upload_excel_file(cls.client)

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_get_workbook(self):
        #excel_client = ExcelService(self.client)
        #file = self.__class__.target_file.get().execute_query()

        #workbook = excel_client.get_workbook("Documents", file.name).execute_query()
        #self.assertIsNotNone(workbook)
        pass
