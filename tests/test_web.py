import unittest
from random import randint

from tests.sharepoint_case import SPTestCase


class TestWeb(SPTestCase):
    target_web_name = "workspace_" + str(randint(0, 10000))

    def test_can_create_web(self):
        self.context.execute_query()  # force to clear pending queue
        creation_info = {'Url': self.target_web_name, 'Title': self.target_web_name}
        target_web = self.context.web.webs.add(creation_info)
        self.context.execute_query()

        results = self.context.web.webs.filter("Title eq '{0}'".format(self.target_web_name))
        self.context.load(results)
        self.context.execute_query()
        self.assertEquals(len(results), 1)

    def test_if_web_updated(self):
        """Test to update Web resource"""
        # properties_to_update = {'Title': "New web site"}
        # self.target_web.update(properties_to_update)
        # self.context.execute_query()

        # self.context.load(self.target_web)
        # self.context.execute_query()
        # self.assertEquals(properties_to_update['Title'], self.target_web.properties['Title'], "Web site update error")

    def test_if_web_deleted(self):
        """Test to delete Web resource"""


if __name__ == '__main__':
    unittest.main()
