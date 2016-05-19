from random import randint

from tests.sharepoint_case import SPTestCase


class TestList(SPTestCase):
    list_title = "Tasks" + str(randint(0, 1000))

    def test_1_create_list(self):
        list_properties = {'__metadata': {'type': 'SP.List'}, 'AllowContentTypes': True, 'BaseTemplate': 171,
                           'Title': self.list_title}
        list_to_create = self.context.web.lists.add(list_properties)
        self.context.execute_query()
        self.assertEqual(list_properties['Title'], list_to_create.properties['Title'])

    def test_2_read_list(self):
        list_to_read = self.context.web.lists.get_by_title(self.list_title)
        self.context.load(list_to_read)
        self.context.execute_query()
        self.assertEqual(self.list_title, list_to_read.properties['Title'])

    def test_3_update_list(self):
        list_to_update = self.context.web.lists.get_by_title(self.list_title)
        list_properties = {'__metadata': {'type': 'SP.List'}, 'Title': self.list_title}
        list_to_update.update(list_properties)
        self.context.execute_query()

    def test_4_delete_list(self):
        list_to_delete = self.context.web.lists.get_by_title(self.list_title)
        list_to_delete.delete_object()
        self.context.execute_query()
