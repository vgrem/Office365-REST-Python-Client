"""Tests for SharePoint tenant administration including site properties, settings, CDN, and themes."""

from __future__ import annotations

from typing import ClassVar, Optional

from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.publishing.portalhealth.status import PortalHealthStatus
from office365.sharepoint.sites.site import Site
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
    test_client_id,
    test_site_url,
    test_team_site_url,
    test_tenant,
)
from tests.sharepoint.sharepoint_case import SPTestCase


class TestTenant(SPTestCase):
    """Test SharePoint tenant administration features."""

    target_site_props: ClassVar[Optional[SiteProperties]] = None
    target_site: ClassVar[Optional[Site]] = None

    @classmethod
    def setUpClass(cls):
        client = ClientContext(test_admin_site_url).with_username_and_password(
            test_tenant, test_client_id, test_admin_credentials.userName, test_admin_credentials.password
        )
        cls.tenant = Tenant(client)
        cls.client = client

    def test_01_get_tenant(self):
        """Get tenant and verify root site URL."""
        self.client.load(self.tenant)
        self.client.execute_query()
        self.assertIsNotNone(self.tenant.root_site_url)

    def test_02_get_tenant_settings(self):
        """Get current tenant settings."""
        tenant_settings = TenantSettings.current(self.client).get().execute_query()
        self.assertIsNotNone(tenant_settings.resource_path)

    def test_03_get_migration_center(self):
        """Get the migration center."""
        result = self.tenant.migration_center.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    # def test3_check_tenant_licenses(self):
    #    result = self.tenant.check_tenant_licenses(["SharePoint"])
    #    self.tenant.execute_query()
    #    self.assertIsNotNone(result.value)

    def test_04_get_site_health_status(self):
        """Get site health status for a team site."""
        result = self.tenant.get_site_health_status(test_team_site_url).execute_query()
        self.assertIsNotNone(result.value)
        self.assertIsInstance(result.value, PortalHealthStatus)

    def test_05_get_site_state(self):
        """Get lock state for the current site."""
        target_site = self.client.site.select(["Id"]).get().execute_query()
        self.assertIsNotNone(target_site)
        self.assertIsNotNone(target_site.id)
        result = self.tenant.get_lock_state_by_id(target_site.id)
        self.tenant.execute_query()
        self.assertIsNotNone(result.value)

    def test_06_list_sites(self):
        """List site properties from SharePoint."""
        result = self.tenant.get_site_properties_from_sharepoint_by_filters().execute_query()
        self.assertIsInstance(result, SitePropertiesCollection)

    def test_07_get_site_secondary_administrators(self):
        """Get secondary administrators for a site."""
        target_site = self.client.site.select(["Id"]).get().execute_query()
        self.assertIsNotNone(target_site)
        self.assertIsNotNone(target_site.id)
        result = self.tenant.get_site_secondary_administrators(target_site.id).execute_query()
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

    #    props = SiteCreationProperties(self.target_site_url, current_user.properties['UserPrincipalName'])
    #    site_props = self.tenant.ensure_site(props)
    #    self.client.execute_query()
    #    self.assertIsNotNone(site_props)

    def test_09_get_site_by_url(self):
        """Get site properties by URL."""
        site_props = self.tenant.get_site_properties_by_url(test_site_url, True).execute_query()
        self.assertIsNotNone(site_props.url)
        # self.assertIsNotNone(site_props.resource_path)
        TestTenant.target_site_props = site_props

    def test_10_update_site(self):
        """Update sharing capability for a site."""
        target_site_props = TestTenant.target_site_props
        if not target_site_props:
            self.skipTest("No target site props from previous test")
        site_props_to_update = target_site_props
        site_props_to_update.set_property("SharingCapability", SharingCapabilities.ExternalUserAndGuestSharing)
        site_props_to_update.update().execute_query()

        updated_site_props = self.tenant.get_site_properties_by_url(test_site_url, True).execute_query()
        self.assertEqual(updated_site_props.sharing_capability, SharingCapabilities.ExternalUserAndGuestSharing)

    #    self.assertTrue(site_props_to_update.properties['Status'], 'Active')

    # def test_12_delete_site(self):
    #    site_url = self.target_site_props.properties['SiteUrl']
    #    self.tenant.remove_site(site_url)
    #    self.client.execute_query()

    def test_11_get_all_tenant_themes(self):
        """Get all tenant themes."""
        tenant = Office365Tenant(self.client)
        result = tenant.get_all_tenant_themes().execute_query()
        self.assertIsNotNone(result)

    def test_12_get_external_users(self):
        """Get external users of the tenant."""
        tenant = Office365Tenant(self.client)
        result = tenant.get_external_users().execute_query()
        self.assertIsNotNone(result)

    def test_13_get_tenant_cdn_enabled(self):
        """Check if tenant CDN is enabled."""
        tenant = Office365Tenant(self.client)
        result = tenant.get_tenant_cdn_enabled(0).execute_query()
        self.assertIsInstance(result.value, bool)

    def test_14_get_tenant_cdn_policies(self):
        """Get tenant CDN policies."""
        tenant = Office365Tenant(self.client)
        result = tenant.get_tenant_cdn_policies(0).execute_query()
        self.assertIsInstance(result.value, ClientValueCollection)

    def test_15_get_tenant_settings_service(self):
        """Get tenant admin settings."""
        result = self.tenant.admin_settings.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test_16_get_tenant_sharing_status(self):
        """Get tenant sharing status."""
        result = self.tenant.admin_settings.get_tenant_sharing_status().execute_query()
        self.assertIsNotNone(result.value)

    def test_17_get_site_thumbnail_logo(self):
        """Get site thumbnail logo."""
        result = self.tenant.get_site_thumbnail_logo(test_site_url).execute_query()
        self.assertIsNotNone(result.value)

    def test_18_get_tenant_cdn_api(self):
        """Get tenant CDN API."""
        cdn_api = self.tenant.cdn_api.get().execute_query()
        self.assertIsNotNone(cdn_api.resource_path)

    # def test_21_get_onedrive_site_sharing_insights(self):
    #    result = self.tenant.get_onedrive_site_sharing_insights(1).execute_query()
    #    self.assertIsNotNone(result.value)

    # def test_22_get_home_site_url(self):
    #    result = self.tenant.get_home_site_url().execute_query()
    #    self.assertIsNotNone(result.value)

    def test_19_get_tenant_all_web_templates(self):
        """Get all tenant web templates."""
        result = self.tenant.get_spo_tenant_all_web_templates().execute_query()
        self.assertIsNotNone(result.items)

    def test_20_get_perf_data(self):
        """Get performance data from migration center."""
        from office365.sharepoint.migrationcenter.service.performance.data import (
            PerformanceData,
        )

        result = PerformanceData(self.client).get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test_21_get_power_apps_environments(self):
        """Get Power Apps environments."""
        result = self.tenant.get_power_apps_environments().execute_query()
        self.assertIsNotNone(result.value)

    # def test_26_get_ransomware_activities(self):
    #    result = self.tenant.get_ransomware_activities().execute_query()
    #    self.assertIsNotNone(result.value)

    def test_22_get_spo_all_web_templates(self):
        """Get all SharePoint web templates."""
        result = self.tenant.get_spo_all_web_templates().execute_query()
        self.assertIsNotNone(result)

    # SharePoint Advanced Management license is needed to perform this action
    # def test_28_get_collaboration_insights_data(self):
    #    # Note: You need a SharePoint Advanced Management license to perform this action
    #    result = self.tenant.get_collaboration_insights_data().execute_query()
    #    self.assertIsNotNone(result.value)

    def test_23_get_app_service_principal(self):
        """Get the app service principal."""
        from office365.sharepoint.tenant.administration.app_service_principal_public import (
            SPOWebAppServicePrincipalPublic,
        )

        result = SPOWebAppServicePrincipalPublic(self.client).get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test_24_get_cdn_urls(self):
        """Get CDN URLs for a team site."""
        result = self.tenant.cdn_api.get_cdn_urls([test_team_site_url]).execute_query()
        self.assertIsNotNone(result.value)

    # You need a SharePoint Advanced Management license to perform this action
    # def test_31_get_ransomware_events_overview(self):
    #    result = self.tenant.get_ransomware_events_overview().execute_query()
    #    self.assertIsNotNone(result.value)

    def test_25_get_admin_endpoints(self):
        """Get admin endpoints."""
        result = self.tenant.admin_endpoints.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    # def test_34_get_spo_app_billing_policies(self):
    #    result = self.tenant.get_spo_app_billing_policies().execute_query()
    #    self.assertIsNotNone(result.value)

    # def test_35_get_site_move_service(self):
    #    target_site = self.client.site.select(["Id"]).get().execute_query()
    #    from office365.sharepoint.administration.sitemove.service import SiteMoveService
    #    result = SiteMoveService(self.client, site_id=target_site.id).get().execute_query()
    #    self.assertIsNotNone(result.resource_path)

    def test_26_get_multi_geo_services(self):
        """Get multi-geo storage quotas."""
        result = self.tenant.multi_geo.storage_quotas.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    # def test_38_get_ib_insights_report_manager(self):
    #    result = SPTenantIBInsightsReportManager(self.client).get().execute_query()
    #    self.assertIsNotNone(result.resource_path)

    # def test38_get_comms_messages(self):
    #    result = self.tenant.comms_messages.get().execute_query()
    #    self.assertIsNotNone(result.resource_path)

    # def test39_check_m365_copilot_business_chat_license(self):
    #    result = self.tenant.check_m365_copilot_business_chat_license().execute_query()
    #    self.assertIsNotNone(result.value)
