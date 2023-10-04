from tests.sharepoint.sharepoint_case import SPTestCase


class TestWebPart(SPTestCase):
    def test_1_list_web_parts(self):
        page_url = "/sites/team/SitePages/Home.aspx"
        file = self.client.web.get_file_by_server_relative_url(page_url)
        web_parts = file.get_limited_webpart_manager().web_parts().get().execute_query()
        self.assertIsNotNone(web_parts.resource_path)
