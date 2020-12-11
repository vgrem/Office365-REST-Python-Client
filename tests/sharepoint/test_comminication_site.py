import uuid
from unittest import TestCase

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.tenant.administration.tenant import Tenant
from settings import settings
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.portal.site_status import SiteStatus
from office365.sharepoint.portal.site_creation_request import SPSiteCreationRequest
from office365.sharepoint.portal.site_manager import SPSiteManager


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
        current_user = self.client.web.current_user.get().execute_query()
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

    def test3_register_hub_site(self):
        admin_site_url = settings.get('admin_site_url')
        client_admin = ClientContext(admin_site_url).with_credentials(self.user_credentials)
        tenant = Tenant(client_admin)
        props = tenant.register_hub_site(self.__class__.site_response.SiteUrl).execute_query()
        self.assertIsNotNone(props)

    def test4_unregister_hub_site(self):
        admin_site_url = settings.get('admin_site_url')
        client_admin = ClientContext(admin_site_url).with_credentials(self.user_credentials)
        tenant = Tenant(client_admin)
        tenant.unregister_hub_site(self.__class__.site_response.SiteUrl).execute_query()

    def test5_delete_site(self):
        self.site_manager.delete(self.__class__.site_response.SiteId).execute_query()
