from random import randint

from client.office365.sharepoint.list_creation_information import ListCreationInformation
from tests.sharepoint_case import SPTestCase


class TestList(SPTestCase):
    list_title = "Tasks" + str(randint(0, 10000))

    def test_1_create_list(self):
        list_properties = ListCreationInformation()
        list_properties.AllowContentTypes = True
        list_properties.BaseTemplate = 171
        list_properties.Title = self.list_title
        list_to_create = self.context.web.lists.add(list_properties)
        self.context.execute_query()
        self.assertEqual(list_properties.Title, list_to_create.properties['Title'])

    def test_2_read_list(self):
        list_to_read = self.context.web.lists.get_by_title(self.list_title)
        self.context.load(list_to_read)
        self.context.execute_query()
        self.assertEqual(self.list_title, list_to_read.properties['Title'])

    def test_3_update_list(self):
        list_to_update = self.context.web.lists.get_by_title(self.list_title)
        self.list_title += "_updated"
        list_to_update.set_property('Title', self.list_title)
        list_to_update.update()
        self.context.execute_query()

        result = self.context.web.lists.filter("Title eq '{0}'".format(self.list_title))
        self.context.load(result)
        self.context.execute_query()
        self.assertEquals(len(result), 1)

    def test_4_delete_list(self):
        list_title = self.list_title + "_updated"
        list_to_delete = self.context.web.lists.get_by_title(list_title)
        list_to_delete.delete_object()
        self.context.execute_query()

        result = self.context.web.lists.filter("Title eq '{0}'".format(list_title))
        self.context.load(result)
        self.context.execute_query()
        self.assertEquals(len(result), 0)
