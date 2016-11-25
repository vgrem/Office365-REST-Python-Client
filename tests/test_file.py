import os
import shutil
import urllib
import requests

from client.office365.runtime.utilities.request_options import RequestOptions
from client.office365.sharepoint.file import File
from client.office365.sharepoint.file_creation_information import FileCreationInformation
from tests.sharepoint_case import SPTestCase


class TestFile(SPTestCase):
    source_path = "../examples/data/report.csv"
    target_library_name = "Documents"
    report_file_url = "/sites/contoso/documents/report.csv"
    report_content = "Report data"

    def setUp(self):
        self.target_library = self.context.web.lists.get_by_title(self.target_library_name)
        self.context.load(self.target_library)
        self.context.execute_query()

    def test_1_upload_file(self):
        info = FileCreationInformation()
        with open(self.source_path, 'r') as content_file:
            info.content = content_file.read()
        info.url = os.path.basename(self.source_path)
        info.overwrite = True
        #upload file
        upload_file = self.target_library.root_folder.files.add(info)
        self.context.execute_query()
        self.assertEquals(upload_file.properties["Name"], info.url)

    def test_2_update_file(self):
        """Test file upload operation"""
        File.save_binary(self.context, self.report_file_url, self.report_content)

    def test_3_download_file(self):
        """Test file upload operation"""
        response = File.open_binary(self.context, self.report_file_url)
        self.assertEqual(response.content, '"' + self.report_content + '"')

    def test_4_download_file_alt(self):
        """Test file download operation"""
        # file_url = "https://media18.sharepoint.com/sites/news/Documents/User Guide.docx"
        # options = RequestOptions(file_url)
        # self.context.authenticate_request(options)
        # options.headers["X-FORMS_BASED_AUTH_ACCEPTED"] = "f"
        # options.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0)"

        # http_proxy = "https://127.0.0.1:8888"
        # proxies = {
        #    "https": http_proxy
        # }

        # response = requests.get(file_url, headers=options.headers, proxies=proxies, verify=False, allow_redirects=True)
        # file_name = os.path.basename(file_url)
        # with open("data/" + file_name, 'wb') as out_file:
        #    shutil.copyfileobj(response.raw, out_file)
        # del response
