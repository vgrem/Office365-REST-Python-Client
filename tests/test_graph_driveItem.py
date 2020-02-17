import os
import uuid
from office365.onedrive.file_upload import ResumableFileUpload
from tests.graph_case import GraphTestCase


def create_listDrive(client):
    list_info = {
        "displayName": "Lib_" + uuid.uuid4().hex,
        "list": {"template": "documentLibrary"}
    }
    new_list = client.sites.root.lists.add(list_info)
    client.execute_query()
    return new_list.drive


class TestDriveItem(GraphTestCase):
    """OneDrive specific test case base class"""
    target_drive = None
    target_file = None

    @classmethod
    def setUpClass(cls):
        super(TestDriveItem, cls).setUpClass()
        cls.target_drive = create_listDrive(cls.client)

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_create_folder(self):
        target_folder_name = "New_" + uuid.uuid4().hex
        folder = self.target_drive.root.create_folder(target_folder_name)
        self.client.execute_query()
        self.assertEqual(folder.properties["name"], target_folder_name)

    def test2_upload_file(self):
        file_name = "SharePoint User Guide.docx"
        path = "{0}/data/{1}".format(os.path.dirname(__file__), file_name)
        with open(path, 'rb') as content_file:
            file_content = content_file.read()
        file_name = os.path.basename(path)
        self.__class__.target_file = self.target_drive.root.upload(file_name, file_content)
        self.client.execute_query()
        self.assertIsNotNone(self.target_file.webUrl)

    def test3_upload_file_session(self):
        file_name = "big_buck_bunny.mp4"
        local_path = "{0}/data/{1}".format(os.path.dirname(__file__), file_name)
        uploader = ResumableFileUpload(self.target_drive.root, local_path, 1000000)
        uploader.execute()
        print("{0} bytes has been uploaded".format(0))

    def test4_download_file(self):
        result = self.__class__.target_file.download()
        self.client.execute_query()
        self.assertIsNotNone(result.value)

    def test5_convert_file(self):
        result = self.__class__.target_file.convert('pdf')
        self.client.execute_query()
        self.assertIsNotNone(result.value)

    def test6_copy_file(self):
        copy_file_name = "Copied_{0}_SharePoint User Guide.docx".format(uuid.uuid4().hex)
        result = self.__class__.target_file.copy(copy_file_name)
        self.client.execute_query()
        self.assertIsNotNone(result.value)

    def test7_delete_file(self):
        items = self.target_drive.root.children
        self.client.load(items)
        self.client.execute_query()
        before_count = len(items)

        items[0].delete_object()
        self.client.load(items)
        self.client.execute_query()
        self.assertEqual(before_count - 1, len(items))
