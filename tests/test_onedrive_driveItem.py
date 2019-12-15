import os
import uuid
from unittest import TestCase

from settings import settings

from office365.graphClient import GraphClient


def get_token(auth_ctx):
    token = auth_ctx.acquire_token_with_username_password(
        'https://graph.microsoft.com',
        settings['user_credentials']['username'],
        settings['user_credentials']['password'],
        settings['client_credentials']['client_id'])
    return token


class TestDriveItem(TestCase):
    """OneDrive specific test case base class"""
    target_file = None

    @classmethod
    def setUpClass(cls):
        ci_tenant_name = settings['tenant']
        cls.client = GraphClient(ci_tenant_name, get_token)

    def test1_create_folder(self):
        target_folder_name = "New_" + uuid.uuid4().hex
        folder = self.client.me.drive.root.create_folder(target_folder_name)
        self.client.execute_query()
        self.assertEqual(folder.properties["name"], target_folder_name)

    def test2_upload_file(self):
        path = "./data/SharePoint User Guide.docx"
        with open(path, 'rb') as content_file:
            file_content = content_file.read()
        file_name = os.path.basename(path)
        self.__class__.target_file = self.client.me.drive.root.upload(file_name, file_content)
        self.client.execute_query()
        self.assertIsNotNone(self.target_file.webUrl)

    def test3_download_file(self):
        result = self.__class__.target_file.download()
        self.client.execute_query()
        self.assertIsNotNone(result.value)

    def test4_convert_file(self):
        result = self.__class__.target_file.convert('pdf')
        self.client.execute_query()
        self.assertIsNotNone(result.value)

    def test5_copy_file(self):
        copy_file_name = "Copied_{0}_SharePoint User Guide.docx".format(uuid.uuid4().hex)
        result = self.__class__.target_file.copy(copy_file_name)
        self.client.execute_query()
        self.assertIsNotNone(result.value)

    def test6_delete_file(self):
        items = self.client.me.drive.root.children
        self.client.load(items)
        self.client.execute_query()
        count_before = len(items)

        self.__class__.target_file.delete_object()
        self.client.load(items)
        self.client.execute_query()
        self.assertEqual(count_before, len(items) + 1)
