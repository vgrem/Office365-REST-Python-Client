from tests import create_unique_name
from tests.graph_case import GraphTestCase


class TestColumn(GraphTestCase):
    list_columns = []  # type: list[ColumnDefinition]

    @classmethod
    def setUpClass(cls):
        super(TestColumn, cls).setUpClass()
        cls.doclib = cls.client.sites.root.lists["Documents"]

    def test1_get_list_columns(self):
        columns = self.doclib.columns.get().execute_query()
        self.assertGreater(len(columns), 0)

    def test2_create_text_column(self):
        column_name = create_unique_name("TextColumn")
        column = self.doclib.columns.add_text(column_name).execute_query()
        self.assertIsNotNone(column.resource_path)
        self.__class__.list_columns.append(column)

    def test3_create_lookup_column(self):
        column_name = create_unique_name("LookupColumn")
        column = self.doclib.columns.add_lookup(
            column_name, self.doclib
        ).execute_query()
        self.assertIsNotNone(column.resource_path)
        self.__class__.list_columns.append(column)

    def test3_delete_list_columns(self):
        for col_to_del in self.__class__.list_columns:
            col_to_del.delete_object().execute_query()
