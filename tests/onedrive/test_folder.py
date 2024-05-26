import uuid

from office365.onedrive.driveitems.driveItem import DriveItem
from office365.onedrive.drives.drive import Drive
from office365.runtime.paths.v4.entity import EntityPath
from tests import create_unique_name
from tests.graph_case import GraphTestCase


class TestFolder(GraphTestCase):
    """OneDrive test case for a Folder"""

    target_drive = None  # type: Drive
    target_folder = None  # type: DriveItem
    target_folder_name = "Archive_" + uuid.uuid4().hex

    @classmethod
    def setUpClass(cls):
        super(TestFolder, cls).setUpClass()
        lib_name = create_unique_name("Lib")
        lib = cls.client.sites.root.lists.add(
            lib_name, "documentLibrary"
        ).execute_query()
        cls.target_drive = lib.drive

    @classmethod
    def tearDownClass(cls):
        cls.target_drive.list.delete_object().execute_query()

    def test1_create_root_folder(self):
        folder = self.target_drive.root.create_folder(
            self.target_folder_name
        ).execute_query()
        self.assertEqual(folder.name, self.target_folder_name)
        self.__class__.target_folder = folder

    def test2_create_child_folder(self):
        target_folder_name = "2018"
        folder = self.__class__.target_folder.create_folder(
            target_folder_name
        ).execute_query()
        self.assertEqual(folder.name, target_folder_name)

    def test3_get_folder_by_path(self):
        root_folder = (
            self.target_drive.root.get_by_path(self.target_folder_name)
            .get()
            .execute_query()
        )
        folder = root_folder.get_by_path("2018").get().execute_query()
        self.assertEqual(
            folder.resource_path,
            EntityPath(folder.id, self.target_drive.items.resource_path),
        )

    def test4_get_folder_permissions(self):
        folder_perms = self.__class__.target_folder.permissions.get().execute_query()
        self.assertIsNotNone(folder_perms.resource_path)

    def test5_get_analytics(self):
        result = self.__class__.target_folder.analytics.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test6_delete_folder(self):
        self.__class__.target_folder.delete_object().execute_query()
