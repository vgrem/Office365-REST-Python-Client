from office365.sharepoint.files.file import File
from office365.sharepoint.lists.list import List
from tests.sharepoint.sharepoint_case import SPTestCase


class TestPages(SPTestCase):
    pages_list = None  # type: List
    target_file = None  # type: File

    @classmethod
    def setUpClass(cls):
        super(TestPages, cls).setUpClass()

    def test1_ensure_site_pages_library(self):
        pages_list = self.client.web.lists.ensure_site_pages_library().execute_query()
        self.assertIsNotNone(pages_list.resource_path)
        self.__class__.pages_list = pages_list

    def test2_create_wiki_page(self):
        page_name = "WelcomeWikiPage.aspx"
        result = self.__class__.pages_list.create_wiki_page(page_name, "Wiki content").execute_query()
        self.assertIsNotNone(result.value)
        self.__class__.target_file = result.value

    def test3_delete_page(self):
        self.__class__.target_file.delete_object().execute_query()
