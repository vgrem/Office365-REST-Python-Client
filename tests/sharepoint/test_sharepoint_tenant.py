import os
from unittest import TestCase

from office365.runtime.auth.UserCredential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenantadministration.sharingCapabilities import SharingCapabilities
from office365.sharepoint.tenantadministration.siteProperties import SiteProperties
from office365.sharepoint.tenantadministration.tenant import Tenant
from settings import settings


class TestTenant(TestCase):
    target_site_props = None  # type: SiteProperties

    @classmethod
    def setUpClass(cls):
        tenant = os.environ.get('office365_python_sdk_tenant', 'mediadev8')
        admin_site_url = "https://{0}-admin.sharepoint.com/".format(tenant)
        cls.client = ClientContext.connect_with_credentials(admin_site_url,
                                                            UserCredential(settings['user_credentials']['username'],
                                                                           settings['user_credentials']['password']))
        cls.tenant = Tenant(cls.client)

    def test1_get_tenant(self):
        self.client.load(self.tenant)
        self.client.execute_query()
        self.assertIsNotNone(self.tenant.properties['RootSiteUrl'])

    def test2_get_site(self):
        site_props = self.tenant.get_site_properties_by_url(settings['url'], True)
        self.client.execute_query()
        self.assertIsNotNone(site_props.properties['SharingCapability'])
        self.__class__.target_site_props = site_props

    def test3_update_site(self):
        site_props_to_update = self.__class__.target_site_props
        site_props_to_update.set_property('SharingCapability', SharingCapabilities.ExternalUserAndGuestSharing)
        site_props_to_update.update()
        self.client.execute_query()
        self.assertTrue(site_props_to_update.properties['Status'], 'Active')
