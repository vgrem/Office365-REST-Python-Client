import os
from random import randint
from unittest import TestCase
from office365.runtime.auth.userCredential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.siteProperties import SiteProperties
from office365.sharepoint.tenant.administration.sitePropertiesCollection import SitePropertiesCollection
from office365.sharepoint.tenant.administration.tenant import Tenant
from settings import settings


class TestTenant(TestCase):
    target_site_props = None  # type: SiteProperties
    target_site_url = "{base_url}sites/{site_name}".format(base_url=settings['url'],
                                                           site_name="Site_" + str(randint(0, 10000)))

    @classmethod
    def setUpClass(cls):
        tenant = os.environ.get('office365_python_sdk_tenant', 'mediadev8')
        admin_site_url = "https://{0}-admin.sharepoint.com/".format(tenant)
        credentials = UserCredential(settings['user_credentials']['username'],
                                     settings['user_credentials']['password'])

        cls.client = ClientContext(admin_site_url).with_credentials(credentials)
        cls.tenant = Tenant(cls.client)

    def test1_get_tenant(self):
        self.client.load(self.tenant)
        self.client.execute_query()
        self.assertIsNotNone(self.tenant.properties['RootSiteUrl'])

    def test3_list_sites(self):
        sites = self.tenant.get_site_properties_from_sharepoint_by_filters("", 0, False)
        self.client.execute_query()
        self.assertIsInstance(sites, SitePropertiesCollection)

    #def test4_create_site(self):
    #    current_user = self.client.web.currentUser
    #    self.client.load(current_user)
    #    self.client.execute_query()

    #    props = SiteCreationProperties(self.__class__.target_site_url, current_user.properties['UserPrincipalName'])
    #    site_props = self.tenant.ensure_site(props)
    #    self.client.execute_query()
    #    self.assertIsNotNone(site_props)

    # def test4_get_site_by_url(self):
    #    site_props = self.tenant.get_site_properties_by_url(self.__class__.target_site_url, False)
    #    self.client.execute_query()
    #    self.assertIsNotNone(site_props.properties['SiteUrl'], self.__class__.target_site_url)
    #    self.__class__.target_site_props = site_props

    # def test5_update_site(self):
    #    site_props_to_update = self.__class__.target_site_props
    #    site_props_to_update.set_property('SharingCapability', SharingCapabilities.ExternalUserAndGuestSharing)
    #    site_props_to_update.update()
    #    self.client.execute_query()
    #    self.assertTrue(site_props_to_update.properties['Status'], 'Active')

    # def test6_delete_site(self):
    #    site_url = self.__class__.target_site_props.properties['SiteUrl']
    #    self.tenant.remove_site(site_url)
    #    self.client.execute_query()
