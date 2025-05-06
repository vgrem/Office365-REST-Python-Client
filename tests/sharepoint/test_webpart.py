from unittest import TestCase

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.webparts.definition import WebPartDefinition
from tests import test_client_credentials, test_site_url


class TestWebPart(TestCase):

    client = None  # type: ClientContext
    target_web_part = None  # type: WebPartDefinition

    @classmethod
    def setUpClass(cls):
        cls.client = ClientContext(test_site_url).with_credentials(
            test_client_credentials
        )
        page_url = "/SitePages/Home.aspx"
        cls.file = cls.client.web.get_file_by_server_relative_url(page_url)
        # cls.file.checkout().execute_query()

    @classmethod
    def tearDownClass(cls):
        pass
        # cls.file.checkin("Added web part").execute_query()

    def test_2_add_web_part(self):
        xml_content = """<?xml version="1.0" encoding="utf-16" standalone="no"?>
<WebPart xmlns="http://schemas.microsoft.com/WebPart/v2" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">

    <Title>Web Part Page Title Bar</Title>
    <Assembly>Microsoft.SharePoint, Version=16.0.0.0, Culture=neutral, PublicKeyToken=71e9bce111e9429c</Assembly>
    <TypeName>Microsoft.SharePoint.WebPartPages.TitleBarWebPart</TypeName>
    <HeaderTitle xmlns="http://schemas.microsoft.com/WebPart/v2/TitleBar">Home</HeaderTitle>
</WebPart>"""

        result = (
            self.file.get_limited_webpart_manager()
            .import_web_part(xml_content)
            .execute_query()
        )
        self.assertIsNotNone(result.resource_path)
        self.__class__.target_web_part = result

    # def test_3_save_web_part_changes(self):
    #    web_part_def = self.__class__.target_web_part
    #    web_part_def.save_web_part_changes().execute_query()

    def test_4_list_web_parts(self):
        web_parts = (
            self.file.get_limited_webpart_manager()
            .web_parts.expand(["WebPart"])
            .get()
            .execute_query()
        )
        self.assertIsNotNone(web_parts.resource_path)
        self.assertGreater(len(web_parts), 0)

    # def test_5_export_web_part(self):
    #    web_part = self.__class__.target_web_part
    #    result = (
    #        self.file.get_limited_webpart_manager()
    #        .export_web_part(web_part)
    #        .execute_query()
    #    )
    #    self.assertIsNotNone(result.value)

    # def test_6_delete_web_part(self):
    #    pass
