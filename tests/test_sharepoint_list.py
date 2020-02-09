from random import randint

from tests.sharepoint_case import SPTestCase

from office365.sharepoint.list_creation_information import ListCreationInformation
from office365.sharepoint.list_template_type import ListTemplateType


class TestSPList(SPTestCase):
    list_title = "Tasks" + str(randint(0, 10000))

    def test1_create_list(self):
        list_properties = ListCreationInformation()
        list_properties.AllowContentTypes = True
        list_properties.BaseTemplate = ListTemplateType.TasksWithTimelineAndHierarchy
        list_properties.Title = self.list_title
        list_to_create = self.client.web.lists.add(list_properties)
        self.client.execute_query()
        self.assertEqual(list_properties.Title, list_to_create.properties['Title'])

    def test2_read_list(self):
        list_to_read = self.client.web.lists.get_by_title(self.list_title)
        self.client.load(list_to_read)
        self.client.execute_query()
        self.assertEqual(self.list_title, list_to_read.properties['Title'])

    def test3_update_list(self):
        list_to_update = self.client.web.lists.get_by_title(self.list_title)
        self.list_title += "_updated"
        list_to_update.set_property('Title', self.list_title)
        list_to_update.update()
        self.client.execute_query()

        result = self.client.web.lists.filter("Title eq '{0}'".format(self.list_title))
        self.client.load(result)
        self.client.execute_query()
        self.assertEqual(len(result), 1)

    def test4_delete_list(self):
        list_title = self.list_title + "_updated"
        list_to_delete = self.client.web.lists.get_by_title(list_title)
        list_to_delete.delete_object()
        self.client.execute_query()

        result = self.client.web.lists.filter("Title eq '{0}'".format(list_title))
        self.client.load(result)
        self.client.execute_query()
        self.assertEqual(len(result), 0)
