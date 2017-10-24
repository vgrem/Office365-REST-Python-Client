import os

from office365.sharepoint.file_creation_information import FileCreationInformation
from office365.sharepoint.list_creation_information import ListCreationInformation
from tests import random_seed
from tests.sharepoint_case import SPTestCase


class _File(SPTestCase):
    source_path = None
    library_name = None
    file_content = None
    updated_content = None
    server_relative_url = None

    @classmethod
    def setUpClass(cls):
        super(_File, cls).setUpClass()
        try:
            cls.target_library = cls.context.web.lists.add(ListCreationInformation(cls.library_name, None, 101))
            cls.context.execute_query()
        except ValueError as e:
            cls.context.pending_request.clear()
            cls.target_library = cls.context.web.lists.get_by_title(cls.library_name)
            cls.context.execute_query()

            cls.target_library.delete_object()
            cls.context.execute_query()

            cls.target_library = cls.context.web.lists.add(ListCreationInformation(cls.library_name, None, 101))
            cls.context.execute_query()

        cls.context.load(cls.target_library)
        cls.context.execute_query()

    @classmethod
    def tearDownClass(cls):
        cls.target_library.delete_object()
        cls.context.execute_query()

    def test_1_upload_file(self):
        info = FileCreationInformation()
        info.content = self.file_content
        info.url = os.path.basename(self.source_path)
        info.overwrite = True
        # upload file
        upload_file = self.target_library.root_folder.files.add(info)
        self.context.execute_query()
        self.assertEqual(upload_file.properties["Name"], info.url)
        self.assertEqual(upload_file.properties["ServerRelativeUrl"], self.server_relative_url)

    def test_2_list_files(self):
        files = self.target_library.root_folder.files

        self.context.load(files)
        self.context.execute_query()
        files_items = list(files)

        self.assertEqual(len(files_items), 1)

        file = files_items[0]
        self.context.load(file)
        self.context.execute_query()
        self.assertEqual(file.properties["Name"], os.path.basename(self.source_path))

    def test_3_update_file(self):
        """Test file upload operation"""
        file = self.target_library.root_folder.files.get_by_url(self.server_relative_url)
        self.context.load(file)
        self.context.execute_query()

        file.write(self.updated_content)

    def test_4_download_file(self):
        """Test file upload operation"""
        file = self.target_library.root_folder.files.get_by_url(self.server_relative_url)
        self.context.load(file)
        self.context.execute_query()
        content = file.read()
        self.assertEqual(content, self.updated_content)

    def test_5_delete_file(self):
        file = self.target_library.root_folder.files.get_by_url(self.server_relative_url)
        file.delete_object()
        self.context.execute_query()

        files = self.target_library.root_folder.files

        self.context.load(files)
        self.context.execute_query()
        files_items = list(files)

        self.assertEqual(len(files_items), 0)


class TestTextFile(_File):
    source_path = "{}/data/text".format(os.path.dirname(__file__))
    library_name = "TestTextFile_%s" % random_seed
    with open(source_path, 'r') as content_file:
        file_content = content_file.read()
    updated_content = b'Updated Content'
    server_relative_url = '/sites/contoso/TestTextFile_%s/text' % random_seed


class TestBinaryFile(_File):
    source_path = "{}/data/binary".format(os.path.dirname(__file__))
    library_name = "TestBinaryFile_%s" % random_seed
    with open(source_path, 'rb') as content_file:
        file_content = content_file.read()
    updated_content = os.urandom(1024)
    server_relative_url = '/sites/contoso/TestBinaryFile_%s/binary' % random_seed
