import unittest
from random import randint

from client.office365.sharepoint.web_creation_information import WebCreationInformation
from tests.sharepoint_case import SPTestCase


class TestWeb(SPTestCase):
    target_web = None

    def setUp(self):
        pass

    def test_1_can_create_web(self):
        self.context.execute_query()  # force to clear the pending queue
        target_web_name = "workspace_" + str(randint(0, 100000))
        creation_info = WebCreationInformation()
        creation_info.Url = target_web_name
        creation_info.Title = target_web_name
        self.__class__.target_web = self.context.web.webs.add(creation_info)
        self.context.execute_query()

        results = self.context.web.webs.filter("Title eq '{0}'".format(target_web_name))
        self.context.load(results)
        self.context.execute_query()
        self.assertEquals(len(results), 1)
        self.assertIsNotNone(results[0].url)

    def test_2_if_web_updated(self):
        """Test to update Web resource"""
        web_title_updated = self.__class__.target_web.properties["Title"] + "_updated"
        self.__class__.target_web.set_property("Title", web_title_updated)
        self.__class__.target_web.update()
        self.context.execute_query()

        self.context.load(self.__class__.target_web)
        self.context.execute_query()
        self.assertEquals(web_title_updated, self.__class__.target_web.properties['Title'])

    def test_3_if_web_deleted(self):
        """Test to delete Web resource"""
        title = self.__class__.target_web.properties['Title']
        self.__class__.target_web.delete_object()
        self.context.execute_query()

        results = self.context.web.webs.filter("Title eq '{0}'".format(title))
        self.context.load(results)
        self.context.execute_query()
        self.assertEquals(len(results), 0)


if __name__ == '__main__':
    unittest.main()
