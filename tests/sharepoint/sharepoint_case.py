from unittest import TestCase

from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, test_client_credentials, test_team_site_url


class SPTestCase(TestCase):
    """SharePoint specific test case base class"""

    client = None  # type: ClientContext

    @classmethod
    def setUpClass(cls):
        cls.client = ClientContext(test_team_site_url).with_credentials(test_client_credentials)

    @staticmethod
    def ensure_list(web, list_properties):
        """

        :type web: office365.sharepoint.webs.web.Web
        :type list_properties: office365.sharepoint.lists.list_creation_information.ListCreationInformation
        """
        lists = web.lists.filter("Title eq '{0}'".format(list_properties.Title)).get().execute_query()
        return lists[0] if len(lists) == 1 else web.lists.add(list_properties).execute_query()

    @staticmethod
    def read_file_as_text(path):
        with open(path, 'r') as content_file:
            file_content = content_file.read()
        return file_content

    @staticmethod
    def read_file_as_binary(path):
        with open(path, 'rb') as content_file:
            file_content = content_file.read()
        return file_content
