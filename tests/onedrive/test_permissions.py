import uuid

from tests.graph_case import GraphTestCase

from office365.directory.permission import Permission
from office365.onedrive.driveItem import DriveItem


class TestPermissions(GraphTestCase):
    target_drive_item = None  # type: DriveItem
    target_permission = None  # type: Permission

    @classmethod
    def setUpClass(cls):
        super(TestPermissions, cls).setUpClass()
        folder_name = "New_" + uuid.uuid4().hex
        cls.target_drive_item = cls.client.sites.root.drive.root.create_folder(folder_name).execute_query()

    @classmethod
    def tearDownClass(cls):
        item_to_delete = cls.target_drive_item.get().execute_query()
        item_to_delete.delete_object().execute_query()

    def test1_create_anonymous_link(self):
        permission = self.__class__.target_drive_item \
            .create_link("view", "anonymous").execute_query()
        self.assertIsNotNone(permission.id)
        self.assertIsNotNone(permission.roles[0], "read")

    def test2_create_company_link(self):
        permission = self.__class__.target_drive_item \
            .create_link("edit", "organization").execute_query()
        self.assertIsNotNone(permission.id)
        self.assertIsNotNone(permission.roles[0], "write")

    def test4_list_permissions(self):
        permissions = self.__class__.target_drive_item.permissions.get().execute_query()
        self.assertIsNotNone(permissions.resource_path)
        self.assertGreater(len(permissions), 0)

    def test5_get_permission(self):
        result = self.__class__.target_drive_item.permissions.get().top(1).execute_query()
        self.assertEqual(len(result), 1)
        perm_id = result[0].id
        perm = self.__class__.target_drive_item.permissions[perm_id].get().execute_query()
        self.assertIsNotNone(perm.resource_path)
        self.__class__.target_permission = result[0]

    # def test6_update_permission(self):
    #    perm_to_update = self.__class__.target_permission
    #    perm_to_update.set_property("roles", ["read"]).update().execute_query()

    def test7_delete_permission(self):
        perm_to_delete = self.__class__.target_permission
        perm_to_delete.delete_object().execute_query()
