from unittest import TestCase

from settings import settings

from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext


class SPTestCase(TestCase):
    """SharePoint specific test case base class"""

    client = None  # type: ClientContext
    client_id = settings.get('client_credentials').get('client_id')
    client_secret = settings.get('client_credentials').get('client_secret')
    client_credentials = ClientCredential(client_id, client_secret)
    site_url = settings.get('url')
    test_user_names = settings.get('test_accounts')

    @classmethod
    def setUpClass(cls):
        cls.client = ClientContext(settings['url']).with_credentials(cls.client_credentials)

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
