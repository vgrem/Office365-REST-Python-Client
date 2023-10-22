from unittest import TestCase

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.lists.creation_information import ListCreationInformation
from office365.sharepoint.lists.list import List
from office365.sharepoint.webs.web import Web
from tests import test_client_credentials, test_team_site_url


class SPTestCase(TestCase):
    """SharePoint specific test case base class"""

    client = None  # type: ClientContext

    @classmethod
    def setUpClass(cls):
        cls.client = ClientContext(test_team_site_url).with_credentials(
            test_client_credentials
        )

    @staticmethod
    def ensure_list(web, list_properties):
        # type: (Web, ListCreationInformation) -> List
        lists = (
            web.lists.filter("Title eq '{0}'".format(list_properties.Title))
            .get()
            .execute_query()
        )
        return (
            lists[0]
            if len(lists) == 1
            else web.lists.add(list_properties).execute_query()
        )

    @staticmethod
    def read_file_as_text(path):
        with open(path, "r") as content_file:
            file_content = content_file.read()
        return file_content

    @staticmethod
    def read_file_as_binary(path):
        with open(path, "rb") as content_file:
            file_content = content_file.read()
        return file_content
