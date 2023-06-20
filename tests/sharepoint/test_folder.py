from office365.sharepoint.changes.collection import ChangeCollection
from office365.sharepoint.folders.folder import Folder
from tests import create_unique_name
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSharePointFolder(SPTestCase):
    folder_name = create_unique_name("New_")
    parent_folder = None  # type: Folder
    target_folder = None  # type: Folder
    deleted_folder_guid = None

    @classmethod
    def setUpClass(cls):
        super(TestSharePointFolder, cls).setUpClass()
        cls.parent_folder = cls.client.web.default_document_library().root_folder

    def test1_create_folder(self):
        folder = self.parent_folder.folders.add(self.folder_name).execute_query()
        self.assertTrue(folder.exists)
        self.__class__.target_folder = folder

    def test2_enum_folders(self):
        folders = self.parent_folder.folders.get().execute_query()
        self.assertGreater(len(folders), 1)
        for child_folder in folders:
            self.assertIsNotNone(child_folder.resource_path)

    def test4_get_folder_by_id(self):
        folder_id = self.__class__.target_folder.unique_id
        folder = self.client.web.get_folder_by_id(folder_id).get().execute_query()
        self.assertIsNotNone(folder.resource_path)
        self.assertTrue(folder.exists)

    def test5_get_by_path(self):
        folder = self.parent_folder.folders.get_by_path(self.folder_name).get().execute_query()
        self.assertIsNotNone(folder.unique_id)

    # def test6_get_by_path_with_props(self):
    #    folder = self.client.web.folders.get_by_path('Shared Documents')
    #    self.client.load(folder, ["Folders"]).execute_query()
    #    self.assertIsNotNone(folder.resource_path)

    def test7_update_folder_properties(self):
        list_item = self.__class__.target_folder.list_item_all_fields
        list_item.set_property("Title", "New folder title").update().execute_query()

    def test8_upload_file_into_folder(self):
        uploaded_file = self.__class__.target_folder.upload_file("sample.txt", "Some content goes here...")
        self.client.execute_query()
        self.assertIsNotNone(uploaded_file.serverRelativeUrl)

    def test9_list_files(self):
        folder = self.__class__.target_folder
        self.client.load(folder, ["Files"])
        self.client.execute_query()
        self.assertGreater(len(folder.files), 0)
        for file in folder.files:
            self.assertIsNotNone(file.resource_path)

    def test_10_copy_folder_to_same_parent(self):
        new_folder_name = create_unique_name("Copied_")
        folder_to = self.__class__.target_folder.copy_to(new_folder_name).execute_query()
        files_to = folder_to.files.get().execute_query()
        self.assertGreater(len(files_to), 0)

    def test_11_rename_folder(self):
        folder = self.__class__.target_folder
        new_folder_name = create_unique_name("Renamed_")
        folder_to = folder.rename(new_folder_name).get().execute_query()
        self.assertEqual(new_folder_name, folder_to.name)
        self.__class__.target_folder = folder_to

    def test_12_move_folder(self):
        folder = self.__class__.target_folder
        new_folder_name = create_unique_name("Moved_")
        folder_to = folder.move_to(new_folder_name).execute_query()
        self.assertIsNotNone(folder_to.serverRelativeUrl)
        self.__class__.target_folder = folder_to

    def test_13_recycle_folder(self):
        result = self.__class__.target_folder.recycle().execute_query()
        self.assertIsNotNone(result.value)
        self.__class__.deleted_folder_guid = result.value

    def test_14_restore_folder(self):
        recycle_item = self.client.web.recycle_bin.get_by_id(self.__class__.deleted_folder_guid)
        recycle_item.restore().execute_query()

    def test_15_get_folder_changes(self):
        changes = self.__class__.target_folder.get_changes().execute_query()
        self.assertIsInstance(changes, ChangeCollection)
        self.assertGreaterEqual(len(changes), 0)

    def test_17_add_using_path(self):
        folder = self.parent_folder.folders.add_using_path(self.folder_name, True).execute_query()
        self.assertIsNotNone(folder.resource_path)

    def test_16_delete_folders(self):
        folders = self.parent_folder.folders.get().execute_query()
        for f in folders:  # type: Folder
            if f.name != "Forms":
                f.delete_object().execute_query()
