from office365.onenote.sections.section import OnenoteSection
from tests.graph_case import GraphTestCase


class TestSection(GraphTestCase):
    target_section = None  # type: OnenoteSection

    @classmethod
    def setUpClass(cls):
        super(TestSection, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test2_list_sections(self):
        my_sections = self.client.me.onenote.sections.get().execute_query()
        self.assertIsNotNone(my_sections.resource_path)
