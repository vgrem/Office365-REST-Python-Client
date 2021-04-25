from random import randint
from unittest import TestCase

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.site_properties import SiteProperties
from office365.sharepoint.tenant.administration.site_properties_collection import SitePropertiesCollection
from office365.sharepoint.tenant.administration.tenant import Tenant
from office365.sharepoint.tenant.tenant_settings import TenantSettings
from tests import test_site_url, test_admin_site_url, test_user_credentials, test_team_site_url


class TestTenant(TestCase):
    target_site_props = None  # type: SiteProperties
    target_site_url = "{base_url}sites/{site_name}".format(base_url=test_site_url,
                                                           site_name="Site_" + str(randint(0, 10000)))

    @classmethod
    def setUpClass(cls):
        cls.client = ClientContext(test_admin_site_url).with_credentials(test_user_credentials)
        cls.tenant = Tenant(cls.client)

    def test1_get_tenant(self):
        self.client.load(self.tenant)
        self.client.execute_query()
        self.assertIsNotNone(self.tenant.root_site_url)

    def test2_get_tenant_settings(self):
        tenant_settings = TenantSettings.current(self.client).execute_query()
        self.assertIsNotNone(tenant_settings.properties)

    # def test3_check_tenant_licenses(self):
    #    result = self.tenant.check_tenant_licenses(["SharePoint"])
    #    self.tenant.execute_query()
    #    self.assertIsNotNone(result.value)

    def test4_get_site_health_status(self):
        result = self.tenant.get_site_health_status(test_team_site_url)
        self.tenant.execute_query()
        self.assertIsNotNone(result.value)
        # self.assertIsInstance(result.value, PortalHealthStatus)

    def test5_get_site_state(self):
        target_site = self.client.site.select(["Id"]).get().execute_query()
        result = self.tenant.get_lock_state_by_id(target_site.id)
        self.tenant.execute_query()
        self.assertIsNotNone(result.value)

    def test6_list_sites(self):
        sites = self.tenant.get_site_properties_from_sharepoint_by_filters("", 0, False).execute_query()
        self.assertIsInstance(sites, SitePropertiesCollection)

    def test7_get_site_secondary_administrators(self):
        target_site = self.client.site.select(["Id"]).get().execute_query()
        result = self.tenant.get_site_secondary_administrators(target_site.id).execute_query()
        self.assertIsNotNone(result.value)

    # def test8_set_site_secondary_administrators(self):
    #    target_site = self.client.site.get()
    #    target_user = self.client.web.ensure_user("jdoe@mediadev8.onmicrosoft.com")
    #    self.client.execute_batch()
    #    #self.tenant.set_site_secondary_administrators(target_site.id, [target_user.login_name], [target_user.login_name])
    #    self.tenant.set_site_secondary_administrators(target_site.id, [target_user.user_principal_name])
    #    self.client.execute_query()

    # def test9_create_site(self):
    #    current_user = self.client.web.currentUser
    #    self.client.load(current_user)
    #    self.client.execute_query()

    #    props = SiteCreationProperties(self.__class__.target_site_url, current_user.properties['UserPrincipalName'])
    #    site_props = self.tenant.ensure_site(props)
    #    self.client.execute_query()
    #    self.assertIsNotNone(site_props)

    def test_10_get_site_by_url(self):
        site_props = self.tenant.get_site_properties_by_url(test_site_url, True).execute_query()
        self.assertIsNotNone(site_props.url)
    #    self.__class__.target_site_props = site_props

    # def test_11_update_site(self):
    #    site_props_to_update = self.__class__.target_site_props
    #    site_props_to_update.set_property('SharingCapability', SharingCapabilities.ExternalUserAndGuestSharing)
    #    site_props_to_update.update()
    #    self.client.execute_query()
    #    self.assertTrue(site_props_to_update.properties['Status'], 'Active')

    # def test_12_delete_site(self):
    #    site_url = self.__class__.target_site_props.properties['SiteUrl']
    #    self.tenant.remove_site(site_url)
    #    self.client.execute_query()
