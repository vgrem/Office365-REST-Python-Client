from random import randint

from tests.sharepoint.sharepoint_case import SPTestCase

from office365.sharepoint.list_creation_information import ListCreationInformation
from office365.sharepoint.list_template_type import ListTemplateType


class TestSPList(SPTestCase):
    target_list_id = None
    target_list_title = "Tasks" + str(randint(0, 10000))

    def test1_create_list(self):
        list_properties = ListCreationInformation()
        list_properties.AllowContentTypes = True
        list_properties.BaseTemplate = ListTemplateType.TasksWithTimelineAndHierarchy
        list_properties.Title = self.target_list_title
        list_to_create = self.client.web.lists.add(list_properties)
        self.client.execute_query()
        self.assertEqual(list_properties.Title, list_to_create.properties['Title'])
        self.__class__.target_list_id = list_to_create.properties['Id']

    def test2_read_list(self):
        list_to_read = self.client.web.lists.get_by_title(self.target_list_title)
        self.client.load(list_to_read)
        self.client.execute_query()
        self.assertEqual(self.target_list_title, list_to_read.properties['Title'])

    def test3_read_list_by_id(self):
        list_to_read = self.client.web.lists.get_by_id(self.__class__.target_list_id)
        self.client.load(list_to_read)
        self.client.execute_query()
        self.assertEqual(self.target_list_id, list_to_read.properties['Id'])

    def test4_update_list(self):
        list_to_update = self.client.web.lists.get_by_title(self.target_list_title)
        self.target_list_title += "_updated"
        list_to_update.set_property('Title', self.target_list_title)
        list_to_update.update()
        self.client.execute_query()

        result = self.client.web.lists.filter("Title eq '{0}'".format(self.target_list_title))
        self.client.load(result)
        self.client.execute_query()
        self.assertEqual(len(result), 1)

    def test5_delete_list(self):
        list_title = self.target_list_title + "_updated"
        list_to_delete = self.client.web.lists.get_by_title(list_title)
        list_to_delete.delete_object()
        self.client.execute_query()

        result = self.client.web.lists.filter("Title eq '{0}'".format(list_title))
        self.client.load(result)
        self.client.execute_query()
        self.assertEqual(len(result), 0)
