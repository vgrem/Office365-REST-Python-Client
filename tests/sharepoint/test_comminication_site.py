import uuid
from unittest import TestCase

from office365.sharepoint.tenant.administration.tenant import Tenant
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.portal.site_status import SiteStatus
from office365.sharepoint.portal.site_creation_request import SPSiteCreationRequest
from office365.sharepoint.portal.site_manager import SPSiteManager
from tests import test_user_credentials, test_site_url, test_admin_site_url


class TestCommunicationSite(TestCase):
    site_response = None

    @classmethod
    def setUpClass(cls):
        super(TestCommunicationSite, cls).setUpClass()
        ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)
        cls.site_manager = SPSiteManager(ctx)
        cls.client = ctx

    def test1_create_site(self):
        current_user = self.client.web.current_user.get().execute_query()
        site_url = "{0}sites/{1}".format(test_site_url, uuid.uuid4().hex)
        request = SPSiteCreationRequest("CommSite123", site_url, current_user.user_principal_name)
        result = self.site_manager.create(request).execute_query()
        self.assertIsNotNone(result.value.SiteStatus)
        self.__class__.site_response = result.value

    def test2_get_site_status(self):
        result = self.site_manager.get_status(self.__class__.site_response.SiteUrl).execute_query()
        self.assertIsNotNone(result.value.SiteStatus)
        self.assertTrue(result.value.SiteStatus != SiteStatus.Error)

    def test3_register_hub_site(self):
        client_admin = ClientContext(test_admin_site_url).with_credentials(test_user_credentials)
        tenant = Tenant(client_admin)
        props = tenant.register_hub_site(self.__class__.site_response.SiteUrl).execute_query()
        self.assertIsNotNone(props)

    def test4_unregister_hub_site(self):
        client_admin = ClientContext(test_admin_site_url).with_credentials(test_user_credentials)
        tenant = Tenant(client_admin)
        tenant.unregister_hub_site(self.__class__.site_response.SiteUrl).execute_query()

    def test5_delete_site(self):
        self.site_manager.delete(self.__class__.site_response.SiteId).execute_query()
