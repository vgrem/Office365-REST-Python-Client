import os
import shutil
import urllib
import requests

from office365.runtime.utilities.request_options import RequestOptions
from office365.sharepoint.file import File
from office365.sharepoint.file_creation_information import FileCreationInformation
from tests.sharepoint_case import SPTestCase


class TestTextFile(SPTestCase):
    source_path = "{}/../examples/data/report.csv".format(os.path.dirname(__file__))
    library_name = "Documents"
    file_url = "/sites/contoso/documents/report.csv"
    with open(source_path, 'r') as content_file:
        file_content = content_file.read()
    updated_content = "Report data"

    def setUp(self):
        self.target_library = self.context.web.lists.get_by_title(self.library_name)
        self.context.load(self.target_library)
        self.context.execute_query()

    def test_1_upload_file(self):
        info = FileCreationInformation()
        info.content = self.file_content
        info.url = os.path.basename(self.source_path)
        info.overwrite = True
        #upload file
        upload_file = self.target_library.root_folder.files.add(info)
        self.context.execute_query()
        self.assertEquals(upload_file.properties["Name"], info.url)

    def test_2_update_file(self):
        """Test file upload operation"""
        File.save_binary(self.context, self.file_url, self.updated_content)

    def test_3_download_file(self):
        """Test file upload operation"""
        response = File.open_binary(self.context, self.file_url)
        str_output_content = response.content.decode("utf-8")
        self.assertEqual(str_output_content, '"{0}"'.format(self.updated_content))


class TestBinaryFile(SPTestCase):
    source_path = "{}/../examples/data/binary".format(os.path.dirname(__file__))
    library_name = "Documents"
    file_url = "/sites/contoso/documents/binary"
    with open(source_path, 'rb') as content_file:
        file_content = content_file.read()
    updated_content = os.urandom(1024)

    def setUp(self):
        self.target_library = self.context.web.lists.get_by_title(self.library_name)
        self.context.load(self.target_library)
        self.context.execute_query()

    def test_1_upload_file(self):
        info = FileCreationInformation()
        info.content = self.file_content
        info.url = os.path.basename(self.source_path)
        info.overwrite = True
        #upload file
        upload_file = self.target_library.root_folder.files.add(info)
        self.context.execute_query()
        self.assertEquals(upload_file.properties["Name"], info.url)

    def test_2_update_file(self):
        """Test file upload operation"""
        File.save_binary(self.context, self.file_url, self.updated_content)

    def test_3_download_file(self):
        """Test file upload operation"""
        response = File.open_binary(self.context, self.file_url)
        output_content = response.content
        self.assertEqual(output_content, self.updated_content)
