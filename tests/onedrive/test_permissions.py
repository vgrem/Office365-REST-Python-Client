import uuid
from unittest import TestCase

from office365.graph_client import GraphClient
from office365.onedrive.driveitems.driveItem import DriveItem
from office365.onedrive.permissions.permission import Permission
from tests import (
    test_client_credentials,
    test_team_site_url,
    test_user_principal_name_alt,
)
from tests.graph_case import acquire_token_by_client_credentials


class TestPermissions(TestCase):
    target_drive_item = None  # type: DriveItem
    target_permission = None  # type: Permission

    @classmethod
    def setUpClass(cls):
        super(TestPermissions, cls).setUpClass()
        client = GraphClient(acquire_token_by_client_credentials)
        folder_name = "New_" + uuid.uuid4().hex
        cls.target_drive_item = client.sites.root.drive.root.create_folder(
            folder_name
        ).execute_query()
        cls.client = client

    @classmethod
    def tearDownClass(cls):
        item_to_delete = cls.target_drive_item.get().execute_query()
        item_to_delete.delete_object().execute_query()

    def test1_create_anonymous_link(self):
        permission = self.__class__.target_drive_item.create_link(
            "view", "anonymous"
        ).execute_query()
        self.assertIsNotNone(permission.id)
        self.assertIsNotNone(permission.roles[0], "read")

    def test2_create_company_link(self):
        permission = self.__class__.target_drive_item.create_link(
            "edit", "organization"
        ).execute_query()
        self.assertIsNotNone(permission.id)
        self.assertIsNotNone(permission.roles[0], "write")

    def test4_driveitem_list_permissions(self):
        permissions = self.__class__.target_drive_item.permissions.get().execute_query()
        self.assertIsNotNone(permissions.resource_path)
        self.assertGreater(len(permissions), 0)

    def test5_driveitem_get_permission(self):
        result = (
            self.__class__.target_drive_item.permissions.get().top(1).execute_query()
        )
        self.assertEqual(len(result), 1)
        perm_id = result[0].id
        perm = (
            self.__class__.target_drive_item.permissions[perm_id].get().execute_query()
        )
        self.assertIsNotNone(perm.resource_path)
        self.__class__.target_permission = result[0]

    def test6_driveitem_update_permission(self):
        # perm_to_update = self.__class__.target_permission
        # perm_to_update.roles = ["read"]
        # perm_to_update.update().execute_query()
        pass

    def test7_driveitem_delete_permission(self):
        perm_to_delete = self.__class__.target_permission
        perm_to_delete.delete_object().execute_query()

    def test8_driveitem_grant_access(self):
        file_abs_url = "{0}/Shared Documents/Financial Sample.xlsx".format(
            test_team_site_url
        )
        permissions = (
            self.client.shares.by_url(file_abs_url)
            .permission.grant(recipients=[test_user_principal_name_alt], roles=["read"])
            .execute_query()
        )
        self.assertIsNotNone(permissions.resource_path)

    def test9_create_site_permission(self):
        app = self.client.applications.get_by_app_id(test_client_credentials.clientId)
        new_site_permission = self.client.sites.root.permissions.add(
            ["write"], app
        ).execute_query()
        self.assertIsNotNone(new_site_permission.resource_path)
        self.target_permission = new_site_permission

    def test_10_list_site_permissions(self):
        site_permissions = self.client.sites.root.permissions.get().execute_query()
        self.assertIsNotNone(site_permissions.resource_path)

    def test_11_delete_site_permission(self):
        self.target_permission.delete_object().execute_query()
