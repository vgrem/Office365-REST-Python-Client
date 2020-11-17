import uuid
from unittest import TestCase

from office365.runtime.auth.user_credential import UserCredential
from settings import settings
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.portal.SiteStatus import SiteStatus
from office365.sharepoint.portal.SPSiteCreationRequest import SPSiteCreationRequest
from office365.sharepoint.portal.SPSiteManager import SPSiteManager


class TestCommunicationSite(TestCase):
    site_response = None

    @classmethod
    def setUpClass(cls):
        super(TestCommunicationSite, cls).setUpClass()
        cls.user_credentials = UserCredential(settings['user_credentials']['username'],
                                              settings['user_credentials']['password'])

        cls.client = ClientContext(settings['url']).with_credentials(cls.user_credentials)
        cls.site_manager = SPSiteManager(cls.client)

    def test1_create_site(self):
        current_user = self.client.web.currentUser.get().execute_query()
        site_url = "{0}sites/{1}".format(settings["url"], uuid.uuid4().hex)
        request = SPSiteCreationRequest("CommSite123", site_url, current_user.user_principal_name)
        response = self.site_manager.create(request)
        self.client.execute_query()
        self.assertIsNotNone(response.SiteStatus)
        self.__class__.site_response = response

    def test2_get_site_status(self):
        response = self.site_manager.get_status(self.__class__.site_response.SiteUrl)
        self.client.execute_query()
        self.assertIsNotNone(response.SiteStatus)
        self.assertTrue(response.SiteStatus != SiteStatus.Error)

    def test4_delete_site(self):
        self.site_manager.delete(self.__class__.site_response.SiteId).execute_query()
