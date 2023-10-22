from unittest import TestCase

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.directory.helper import SPHelper
from office365.sharepoint.directory.session import DirectorySession
from tests import test_site_url, test_user_credentials, test_user_principal_name


class TestDirectorySession(TestCase):
    client = None  # type: ClientContext

    @classmethod
    def setUpClass(cls):
        super(TestDirectorySession, cls).setUpClass()
        client = ClientContext(test_site_url).with_credentials(test_user_credentials)
        cls.client = client

    def test_1_init_session(self):
        session = self.client.directory_session.get().execute_query()
        self.assertIsInstance(session, DirectorySession)

    def test_2_get_me(self):
        me = self.client.directory_session.me.get().execute_query()
        self.assertIsNotNone(me.resource_path)

    def test_3_get_my_groups(self):
        result = self.client.directory_session.me.get_my_groups().execute_query()
        self.assertIsNotNone(result)
        # self.assertGreater(len(result.value), 0)

    # def test_4_user_member_of(self):
    #    result = self.__class__.session.me.is_member_of("").execute_query()
    #    self.assertIsNotNone(result.value)

    def test_5_check_site_availability(self):
        result = SPHelper.check_site_availability(
            self.client, test_site_url
        ).execute_query()
        self.assertIsNotNone(result.value)

    # def test_6_get_graph_user(self):
    #    result = self.client.directory_session.get_graph_user(test_user_principal_name).execute_query()
    #    self.assertIsNotNone(result.resource_path)
