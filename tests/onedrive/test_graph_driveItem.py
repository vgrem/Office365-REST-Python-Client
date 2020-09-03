import os
import uuid

from tests.graph_case import GraphTestCase

from office365.graph.onedrive.drive import Drive
from office365.graph.onedrive.driveItem import DriveItem


def create_list_drive(client):
    list_info = {
        "displayName": "Lib_" + uuid.uuid4().hex,
        "list": {"template": "documentLibrary"}
    }
    new_list = client.sites.root.lists.add(list_info).execute_query()
    return new_list.drive


class TestDriveItem(GraphTestCase):
    """OneDrive specific test case base class"""
    target_drive = None  # type: Drive
    target_file = None   # type: DriveItem
    target_folder = None  # type: DriveItem

    @classmethod
    def setUpClass(cls):
        super(TestDriveItem, cls).setUpClass()
        cls.target_drive = create_list_drive(cls.client)

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_create_folder(self):
        target_folder_name = "New_" + uuid.uuid4().hex
        folder = self.target_drive.root.create_folder(target_folder_name).execute_query()
        self.assertEqual(folder.properties["name"], target_folder_name)
        self.__class__.target_folder = folder

    def test2_get_folder_permissions(self):
        folder_perms = self.__class__.target_folder.permissions.get().execute_query()
        self.assertIsNotNone(folder_perms.resource_path)

    def test3_upload_file(self):
        file_name = "SharePoint User Guide.docx"
        path = "{0}/../data/{1}".format(os.path.dirname(__file__), file_name)
        with open(path, 'rb') as content_file:
            file_content = content_file.read()
        file_name = os.path.basename(path)
        self.__class__.target_file = self.target_drive.root.upload(file_name, file_content).execute_query()
        self.assertIsNotNone(self.target_file.web_url)

    def test4_upload_file_session(self):
        file_name = "big_buck_bunny.mp4"
        local_path = "{0}/../data/{1}".format(os.path.dirname(__file__), file_name)
        target_file = self.target_drive.root.resumable_upload(local_path)
        self.client.execute_query()
        self.assertIsNotNone(target_file.web_url)

    def test5_download_file(self):
        result = self.__class__.target_file.get_content()
        self.client.execute_query()
        self.assertIsNotNone(result.value)

    def test6_convert_file(self):
        result = self.__class__.target_file.convert('pdf')
        self.client.execute_query()
        self.assertIsNotNone(result.value)

    def test7_copy_file(self):
        file_name = "Copied_{0}_SharePoint User Guide.docx".format(uuid.uuid4().hex)
        result = self.__class__.target_file.copy(file_name)
        self.client.execute_query()
        self.assertIsNotNone(result.value)

    #def test8_move_file(self):
    #    target_folder = self.__class__.target_folder.parentReference
    #
    #    file_name = "Moved_{0}_SharePoint User Guide.docx".format(uuid.uuid4().hex)
    #    result = self.__class__.target_file.move(file_name, target_folder)
    #    self.client.execute_query()
    #    self.assertIsNotNone(result.value)

    def test9_delete_file(self):
        items = self.target_drive.root.children.top(1).get().execute_query()
        items[0].delete_object().execute_query()
