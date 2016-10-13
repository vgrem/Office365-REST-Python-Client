import os
import shutil
import urllib
import requests

from client.office365.runtime.utilities.request_options import RequestOptions
from client.office365.sharepoint.file import File
from tests.sharepoint_case import SPTestCase


class TestFile(SPTestCase):

    def test_upload_file(self):
        """Test file upload operation"""
        file_url = "/sites/contoso/documents/report.csv"
        File.save_binary(self.context, file_url, "Report data")

    def test_download_file(self):
        """Test file download operation"""
        #file_url = "https://media18.sharepoint.com/sites/news/Documents/User Guide.docx"
        #options = RequestOptions(file_url)
        #self.context.authenticate_request(options)
        #options.headers["X-FORMS_BASED_AUTH_ACCEPTED"] = "f"
        #options.headers["User-Agent"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:39.0)"

        #http_proxy = "https://127.0.0.1:8888"
        #proxies = {
        #    "https": http_proxy
        #}

        #response = requests.get(file_url, headers=options.headers, proxies=proxies, verify=False, allow_redirects=True)
        #file_name = os.path.basename(file_url)
        #with open("data/" + file_name, 'wb') as out_file:
        #    shutil.copyfileobj(response.raw, out_file)
        #del response
