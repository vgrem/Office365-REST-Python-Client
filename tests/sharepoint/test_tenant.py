from random import randint
from unittest import TestCase

from settings import settings

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.site_properties import SiteProperties
from office365.sharepoint.tenant.administration.sitePropertiesCollection import SitePropertiesCollection
from office365.sharepoint.tenant.administration.tenant import Tenant
from office365.sharepoint.tenant.tenant_settings import TenantSettings


class TestTenant(TestCase):
    target_site_props = None  # type: SiteProperties
    target_site_url = "{base_url}sites/{site_name}".format(base_url=settings['url'],
                                                           site_name="Site_" + str(randint(0, 10000)))

    @classmethod
    def setUpClass(cls):
        credentials = UserCredential(settings['user_credentials']['username'],
                                     settings['user_credentials']['password'])

        cls.client = ClientContext(settings.get("admin_site_url")).with_credentials(credentials)
        cls.tenant = Tenant(cls.client)

    def test1_get_tenant(self):
        self.client.load(self.tenant)
        self.client.execute_query()
        self.assertIsNotNone(self.tenant.root_site_url)

    def test2_get_tenant_settings(self):
        tenant_settings = TenantSettings.current(self.client)
        self.client.execute_query()
        self.assertIsNotNone(tenant_settings.properties)

    def test3_list_sites(self):
        sites = self.tenant.get_site_properties_from_sharepoint_by_filters("", 0, False)
        self.client.execute_query()
        self.assertIsInstance(sites, SitePropertiesCollection)

    def test4_get_site_secondary_administrators(self):
        target_site = self.client.site.select(["Id"]).get().execute_query()
        result = self.tenant.get_site_secondary_administrators(target_site.id)
        self.client.execute_query()
        self.assertIsNotNone(result)

    #def test5_set_site_secondary_administrators(self):
    #    target_site = self.client.site.get()
    #    target_user = self.client.web.ensure_user("jdoe@mediadev8.onmicrosoft.com")
    #    self.client.execute_batch()
    #    #self.tenant.set_site_secondary_administrators(target_site.id, [target_user.login_name], [target_user.login_name])
    #    self.tenant.set_site_secondary_administrators(target_site.id, [target_user.user_principal_name])
    #    self.client.execute_query()

    # def test6_create_site(self):
    #    current_user = self.client.web.currentUser
    #    self.client.load(current_user)
    #    self.client.execute_query()

    #    props = SiteCreationProperties(self.__class__.target_site_url, current_user.properties['UserPrincipalName'])
    #    site_props = self.tenant.ensure_site(props)
    #    self.client.execute_query()
    #    self.assertIsNotNone(site_props)

    # def test7_get_site_by_url(self):
    #    site_props = self.tenant.get_site_properties_by_url(self.__class__.target_site_url, False)
    #    self.client.execute_query()
    #    self.assertIsNotNone(site_props.properties['SiteUrl'], self.__class__.target_site_url)
    #    self.__class__.target_site_props = site_props

    # def test8_update_site(self):
    #    site_props_to_update = self.__class__.target_site_props
    #    site_props_to_update.set_property('SharingCapability', SharingCapabilities.ExternalUserAndGuestSharing)
    #    site_props_to_update.update()
    #    self.client.execute_query()
    #    self.assertTrue(site_props_to_update.properties['Status'], 'Active')

    # def test9_delete_site(self):
    #    site_url = self.__class__.target_site_props.properties['SiteUrl']
    #    self.tenant.remove_site(site_url)
    #    self.client.execute_query()
