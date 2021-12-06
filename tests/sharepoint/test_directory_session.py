from unittest import TestCase

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.directory.SPHelper import SPHelper
from office365.sharepoint.directory.directory_session import DirectorySession
from tests import test_user_credentials, test_site_url


class TestDirectorySession(TestCase):
    session = None  # type: DirectorySession

    @classmethod
    def setUpClass(cls):
        super(TestDirectorySession, cls).setUpClass()
        cls.client = ClientContext(test_site_url).with_credentials(test_user_credentials)
        cls.session = DirectorySession(cls.client)

    def test_1_init_session(self):
        session = self.__class__.session.get().execute_query()
        self.assertIsInstance(session, DirectorySession)

    def test_2_get_me(self):
        me = self.__class__.session.me.get().execute_query()
        self.assertIsNotNone(me.resource_path)

    #def test_3_get_my_groups(self):
    #    result = self.__class__.session.me.get_my_groups().execute_query()
    #    self.assertIsNotNone(result.value)

    def test_4_check_site_availability(self):
        result = SPHelper.check_site_availability(self.client, test_site_url).execute_query()
        self.assertIsNotNone(result.value)
