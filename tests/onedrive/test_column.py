from office365.onedrive.columns.definition import ColumnDefinition
from office365.onedrive.lists.list import List
from tests import create_unique_name
from tests.graph_case import GraphTestCase


class TestColumn(GraphTestCase):
    target_column = None  # type: ColumnDefinition

    @classmethod
    def setUpClass(cls):
        super(TestColumn, cls).setUpClass()
        cls.doclib = cls.client.sites.root.lists["Documents"]  # type: List

    def test1_get_list_columns(self):
        columns = self.doclib.columns.get().execute_query()
        self.assertGreater(len(columns), 0)

    def test2_create_column(self):
        column_name = create_unique_name("TextColumn")
        column = self.doclib.columns.add_text(column_name).execute_query()
        self.assertIsNotNone(column.resource_path)
        self.__class__.target_column = column

    def test3_delete_column(self):
        col_to_del = self.__class__.target_column
        col_to_del.delete_object().execute_query()


