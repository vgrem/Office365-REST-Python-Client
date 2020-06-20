from office365.sharepoint.contenttypes.content_type_collection import ContentTypeCollection
from tests.sharepoint.sharepoint_case import SPTestCase


class TestContentType(SPTestCase):

    def test_1_list_site_content_types(self):
        web_cts = self.client.site.rootWeb.contentTypes
        self.client.load(web_cts)
        self.client.execute_query()
        self.assertIsInstance(web_cts, ContentTypeCollection)


