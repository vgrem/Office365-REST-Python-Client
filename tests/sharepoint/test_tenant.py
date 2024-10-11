from unittest import TestCase

from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.publishing.portal_health_status import PortalHealthStatus
from office365.sharepoint.tenant.administration.sharing_capabilities import (
    SharingCapabilities,
)
from office365.sharepoint.tenant.administration.sites.properties import SiteProperties
from office365.sharepoint.tenant.administration.sites.properties_collection import (
    SitePropertiesCollection,
)
from office365.sharepoint.tenant.administration.tenant import Tenant
from office365.sharepoint.tenant.management.office365_tenant import Office365Tenant
from office365.sharepoint.tenant.settings import TenantSettings
from tests import (
    test_admin_credentials,
    test_admin_site_url,
    test_site_url,
    test_team_site_url,
)


class TestTenant(TestCase):
    target_site_props = None  # type: SiteProperties

    @classmethod
    def setUpClass(cls):
        client = ClientContext(test_admin_site_url).with_credentials(
            test_admin_credentials
        )
        cls.tenant = Tenant(client)
        cls.client = client

    def test1_get_tenant(self):
        self.client.load(self.tenant)
        self.client.execute_query()
        self.assertIsNotNone(self.tenant.root_site_url)

    def test2_get_tenant_settings(self):
        tenant_settings = TenantSettings.current(self.client).get().execute_query()
        self.assertIsNotNone(tenant_settings.resource_path)

    def test3_get_migration_center(self):
        result = self.tenant.migration_center.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    # def test3_check_tenant_licenses(self):
    #    result = self.tenant.check_tenant_licenses(["SharePoint"])
    #    self.tenant.execute_query()
    #    self.assertIsNotNone(result.value)

    def test4_get_site_health_status(self):
        result = self.tenant.get_site_health_status(test_team_site_url).execute_query()
        self.assertIsNotNone(result.value)
        self.assertIsInstance(result.value, PortalHealthStatus)

    def test5_get_site_state(self):
        target_site = self.client.site.select(["Id"]).get().execute_query()
        result = self.tenant.get_lock_state_by_id(target_site.id)
        self.tenant.execute_query()
        self.assertIsNotNone(result.value)

    def test6_list_sites(self):
        sites = (
            self.tenant.get_site_properties_from_sharepoint_by_filters().execute_query()
        )
        self.assertIsInstance(sites, SitePropertiesCollection)

    def test7_get_site_secondary_administrators(self):
        target_site = self.client.site.select(["Id"]).get().execute_query()
        result = self.tenant.get_site_secondary_administrators(
            target_site.id
        ).execute_query()
        self.assertIsNotNone(result.value)

    # def test8_set_site_secondary_administrators(self):
    #    target_site = self.client.site.get()
    #    target_user = self.client.web.ensure_user("jdoe@mediadev8.onmicrosoft.com")
    #    self.client.execute_batch()
    #    #self.tenant.set_site_secondary_administrators(
    #         target_site.id, [target_user.login_name], [target_user.login_name]
    #    )
    #    self.tenant.set_site_secondary_administrators(target_site.id, [target_user.user_principal_name])
    #    self.client.execute_query()

    def test9_create_site(self):
        pass
        # current_user = self.client.web.currentUser
        # self.client.load(current_user)
        # self.client.execute_query()

    #    props = SiteCreationProperties(self.__class__.target_site_url, current_user.properties['UserPrincipalName'])
    #    site_props = self.tenant.ensure_site(props)
    #    self.client.execute_query()
    #    self.assertIsNotNone(site_props)

    def test_10_get_site_by_url(self):
        site_props = self.tenant.get_site_properties_by_url(
            test_site_url, True
        ).execute_query()
        self.assertIsNotNone(site_props.url)
        # self.assertIsNotNone(site_props.resource_path)
        self.__class__.target_site_props = site_props

    def test_11_update_site(self):
        site_props_to_update = self.__class__.target_site_props
        site_props_to_update.set_property(
            "SharingCapability", SharingCapabilities.ExternalUserAndGuestSharing
        )
        site_props_to_update.update().execute_query()

        updated_site_props = self.tenant.get_site_properties_by_url(
            test_site_url, True
        ).execute_query()
        self.assertTrue(
            updated_site_props.sharing_capability
            == SharingCapabilities.ExternalUserAndGuestSharing
        )

    #    self.assertTrue(site_props_to_update.properties['Status'], 'Active')

    # def test_12_delete_site(self):
    #    site_url = self.__class__.target_site_props.properties['SiteUrl']
    #    self.tenant.remove_site(site_url)
    #    self.client.execute_query()

    def test_13_get_all_tenant_themes(self):
        tenant = Office365Tenant(self.client)
        result = tenant.get_all_tenant_themes().execute_query()
        self.assertIsNotNone(result)

    def test_14_get_external_users(self):
        tenant = Office365Tenant(self.client)
        result = tenant.get_external_users().execute_query()
        self.assertIsNotNone(result)

    def test_15_get_tenant_cdn_enabled(self):
        tenant = Office365Tenant(self.client)
        result = tenant.get_tenant_cdn_enabled(0).execute_query()
        self.assertIsInstance(result.value, bool)

    def test_16_get_tenant_cdn_policies(self):
        tenant = Office365Tenant(self.client)
        result = tenant.get_tenant_cdn_policies(0).execute_query()
        self.assertIsInstance(result.value, ClientValueCollection)

    def test_17_get_tenant_settings_service(self):
        result = self.tenant.admin_settings.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test_18_get_tenant_sharing_status(self):
        result = self.tenant.admin_settings.get_tenant_sharing_status().execute_query()
        self.assertIsNotNone(result.value)

    def test_19_get_site_thumbnail_logo(self):
        result = self.tenant.get_site_thumbnail_logo(test_site_url).execute_query()
        self.assertIsNotNone(result.value)

    def test_20_get_tenant_cdn_api(self):
        cdn_api = self.tenant.cdn_api.get().execute_query()
        self.assertIsNotNone(cdn_api.resource_path)

    # def test_21_get_onedrive_site_sharing_insights(self):
    #    result = self.tenant.get_onedrive_site_sharing_insights(1).execute_query()
    #    self.assertIsNotNone(result.value)

    # def test_22_get_home_site_url(self):
    #    result = self.tenant.get_home_site_url().execute_query()
    #    self.assertIsNotNone(result.value)

    def test_23_get_tenant_all_web_templates(self):
        result = self.tenant.get_spo_tenant_all_web_templates().execute_query()
        self.assertIsNotNone(result.items)

    def test_24_get_perf_data(self):
        from office365.sharepoint.migrationcenter.service.performance.data import (
            PerformanceData,
        )

        result = PerformanceData(self.client).get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test_25_get_power_apps_environments(self):
        result = self.tenant.get_power_apps_environments().execute_query()
        self.assertIsNotNone(result.value)

    # def test_26_get_ransomware_activities(self):
    #    result = self.tenant.get_ransomware_activities().execute_query()
    #    self.assertIsNotNone(result.value)

    def test_27_get_spo_all_web_templates(self):
        result = self.tenant.get_spo_all_web_templates().execute_query()
        self.assertIsNotNone(result)

    def test_28_get_collaboration_insights_data(self):
        # Note: You need a SharePoint Advanced Management license to perform this action
        result = self.tenant.get_collaboration_insights_data().execute_query()
        self.assertIsNotNone(result.value)

    def test_29_get_app_service_principal(self):
        from office365.sharepoint.tenant.administration.internal.appservice.principal import (
            SPOWebAppServicePrincipal,
        )

        result = SPOWebAppServicePrincipal(self.client).get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test_30_get_cdn_urls(self):
        result = self.tenant.cdn_api.get_cdn_urls([test_team_site_url]).execute_query()
        self.assertIsNotNone(result.value)

    # You need a SharePoint Advanced Management license to perform this action
    #def test_31_get_ransomware_events_overview(self):
    #    result = self.tenant.get_ransomware_events_overview().execute_query()
    #    self.assertIsNotNone(result.value)
