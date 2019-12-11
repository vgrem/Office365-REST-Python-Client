import json
import os
import uuid
from unittest import TestCase

from settings import settings

from office365.graph_client import GraphClient


def get_token(auth_ctx):
    token = auth_ctx.acquire_token_with_username_password(
        'https://graph.microsoft.com',
        settings['user_credentials']['username'],
        settings['user_credentials']['password'],
        settings['client_credentials']['client_id'])
    return token


class TestDrive(TestCase):
    """OneDrive specific test case base class"""
    target_file = None

    @classmethod
    def setUpClass(cls):
        ci_tenant_name = settings['tenant']
        cls.client = GraphClient(ci_tenant_name, get_token)

    def test1_get_drives(self):
        drives = self.client.drives.top(2)
        self.client.load(drives)
        self.client.execute_query()
        self.assertLessEqual(len(drives), 2)
        for drive in drives:
            self.assertIsNotNone(drive.webUrl)

    def test2_get_drives_alt(self):
        resp = self.client.execute_request("/drives?$top=2")
        drives = json.loads(resp.content.decode('utf-8'))['value']
        self.assertLessEqual(len(drives), 2)
        for drive in drives:
            self.assertIsNotNone(drive['webUrl'])

    def test3_get_first_drive(self):
        drives = self.client.drives.top(1)
        self.client.load(drives)
        self.client.execute_query()
        self.assertLessEqual(len(drives), 1)
        target_drive_id = drives[0].id

        target_drive = self.client.drives.get_by_id(target_drive_id)
        self.client.load(target_drive)
        self.client.execute_query()
        self.assertEqual(target_drive.id, target_drive_id)

    def test4_create_folder(self):
        target_folder_name = "New_" + uuid.uuid4().hex
        folder = self.client.me.drive.root.create_folder(target_folder_name)
        self.client.execute_query()
        self.assertEqual(folder.properties["name"], target_folder_name)

    def test5_list_drive_items(self):
        items = self.client.me.drive.root.children
        self.client.load(items)
        self.client.execute_query()
        self.assertGreater(len(items), 0)
        self.assertIsNotNone(items[0].fileSystemInfo)

    def test6_drive_item_upload(self):
        path = "./data/SharePoint User Guide.docx"
        with open(path, 'rb') as content_file:
            file_content = content_file.read()
        file_name = os.path.basename(path)
        self.__class__.target_file = self.client.me.drive.root.upload(file_name, file_content)
        self.client.execute_query()
        self.assertIsNotNone(self.target_file.webUrl)

    def test7_drive_item_download(self):
        result = self.__class__.target_file.download()
        self.client.execute_query()
        self.assertIsNotNone(result.value)
