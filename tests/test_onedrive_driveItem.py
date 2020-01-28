import os
import uuid
from unittest import TestCase
from office365.onedrive.driveItemUploadableProperties import DriveItemUploadableProperties
from office365.runtime.utilities.http_method import HttpMethod
from office365.runtime.utilities.request_options import RequestOptions
from settings import settings

from office365.graphClient import GraphClient


def get_token(auth_ctx):
    token = auth_ctx.acquire_token_with_username_password(
        'https://graph.microsoft.com',
        settings['user_credentials']['username'],
        settings['user_credentials']['password'],
        settings['client_credentials']['client_id'])
    return token


def read_in_chunks(file_object, chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def create_listDrive(client):
    list_info = {
        "displayName": "Lib_" + uuid.uuid4().hex,
        "list": {"template": "documentLibrary"}
    }
    new_list = client.sites.root.lists.add(list_info)
    client.execute_query()
    return new_list.drive


class TestDriveItem(TestCase):
    """OneDrive specific test case base class"""
    client = None
    target_drive = None
    target_file = None

    @classmethod
    def setUpClass(cls):
        ci_tenant_name = settings['tenant']
        cls.client = GraphClient(ci_tenant_name, get_token)
        cls.target_drive = create_listDrive(cls.client)  # cls.client.me.drive

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
        items = self.target_drive.root.children
        self.client.load(items)
        self.client.execute_query()
        before_count = len(items)

        items[0].delete_object()
        self.client.load(items)
        self.client.execute_query()

        self.assertEqual(before_count - 1, len(items))

    def test7_upload_file_session(self):
        file_name = "big_buck_bunny.mp4"
        path = "{0}/data/{1}".format(os.path.dirname(__file__), file_name)
        # 1. create a file
        target_item = self.target_drive.root.upload(file_name, None)
        self.client.execute_query()
        self.assertIsNotNone(target_item.properties['id'])
        # 2. create upload session
        item = DriveItemUploadableProperties()
        item.name = file_name
        session_result = target_item.create_upload_session(item)
        self.client.execute_query()
        self.assertIsNotNone(session_result.value)
        # 3. start upload
        f = open(path, 'rb')
        st = os.stat(path)
        f_pos = 0
        for piece in read_in_chunks(f, chunk_size=1000000):
            req = RequestOptions(session_result.value.uploadUrl)
            req.method = HttpMethod.Put
            req.set_header('Content-Length', str(len(piece)))
            req.set_header('Content-Range', 'bytes {0}-{1}/{2}'.format(f_pos, (f_pos + len(piece) - 1), st.st_size))
            req.set_header('Accept', '*/*')
            req.data = piece
            resp = self.client.execute_request_direct(req)
            self.assertTrue(resp.ok)
            f_pos += len(piece)
