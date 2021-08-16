from office365.onenote.notebooks.notebook import Notebook
from tests import create_unique_name
from tests.graph_case import GraphTestCase


class TestNotebook(GraphTestCase):
    target_notebook = None  # type: Notebook

    @classmethod
    def setUpClass(cls):
        super(TestNotebook, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_create_notebook(self):
        notebook_name = create_unique_name("My Private notebook")
        new_notebook = self.client.me.onenote.notebooks.add(displayName=notebook_name).execute_query()
        self.assertIsNotNone(new_notebook.resource_path)
        self.__class__.target_notebook = new_notebook

    def test2_list_notebooks(self):
        my_notebooks = self.client.me.onenote.notebooks.get().execute_query()
        self.assertIsNotNone(my_notebooks.resource_path)

    def test3_get_recent_notebooks(self):
        result = self.client.me.onenote.notebooks.get_recent_notebooks().execute_query()
        self.assertIsNotNone(result.value)

    def test4_create_section(self):
        name = create_unique_name("Section name")
        new_section = self.__class__.target_notebook.sections.add(displayName=name).execute_query()
        self.assertIsNotNone(new_section.resource_path)
        self.__class__.target_section = new_section

