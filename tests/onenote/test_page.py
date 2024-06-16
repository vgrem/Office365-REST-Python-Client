from office365.onenote.pages.page import OnenotePage
from tests.graph_case import GraphTestCase


class TestPage(GraphTestCase):
    target_page = None  # type: OnenotePage

    @classmethod
    def setUpClass(cls):
        super(TestPage, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_create_page(self):
        pass

    def test2_list_pages(self):
        sections = self.client.me.onenote.sections.top(1).get().execute_query()
        my_pages = sections[0].pages.get().top(10).execute_query()
        self.assertIsNotNone(my_pages.resource_path)
