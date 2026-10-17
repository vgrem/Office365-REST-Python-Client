from __future__ import annotations

import datetime as _dt
import time
from datetime import datetime
from typing import TYPE_CHECKING, AnyStr, Callable, List, Optional
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.v3.static import StaticPath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import GuidCollection, StringCollection
from office365.sharepoint.administration.archiving.file_size_metric import (
    ArchiveFileSizeMetric,
)
from office365.sharepoint.directory.tenant_service_info_value import (
    TenantServiceInfoValue,
)
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.gtp.request_options import ChatGptRequestOptions
from office365.sharepoint.listitems.collection import ListItemCollection
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.lists.render_data_parameters import RenderListDataParameters
from office365.sharepoint.lists.render_override_parameters import (
    RenderListDataOverrideParameters,
)
from office365.sharepoint.portal.hub_sites_utility import SPHubSitesUtility
from office365.sharepoint.publishing.portalhealth.status import PortalHealthStatus
from office365.sharepoint.sites.home.details import HomeSitesDetails
from office365.sharepoint.sites.site import Site
from office365.sharepoint.tenant.administration.collaboration.insights_data import (
    CollaborationInsightsData,
)
from office365.sharepoint.tenant.administration.collaboration.insights_overview import (
    CollaborationInsightsOverview,
)
from office365.sharepoint.tenant.administration.copilot.promousage import (
    SPOCopilotPromoUsage,
)
from office365.sharepoint.tenant.administration.deletedsiteproperties import (
    DeletedSiteProperties,
)
from office365.sharepoint.tenant.administration.hubsites.collection import (
    HubSiteCollection,
)
from office365.sharepoint.tenant.administration.hubsites.properties import (
    HubSiteProperties,
)
from office365.sharepoint.tenant.administration.insights.onedrive_site_sharing import (
    OneDriveSiteSharingInsights,
)
from office365.sharepoint.tenant.administration.insights.top_files_sharing import (
    TopFilesSharingInsights,
)
from office365.sharepoint.tenant.administration.jobs.spo_operation import SpoOperation
from office365.sharepoint.tenant.administration.policies.app_billing_properties import (
    SPOAppBillingProperties,
)
from office365.sharepoint.tenant.administration.policies.content_security_configuration import (
    SPOContentSecurityPolicyConfiguration,
)
from office365.sharepoint.tenant.administration.policies.create_request import (
    CreatePolicyRequest,
)
from office365.sharepoint.tenant.administration.policies.definition import (
    TenantAdminPolicyDefinition,
)
from office365.sharepoint.tenant.administration.policies.file_version_types import (
    SPOFileVersionBatchDeleteJobProgress,
)
from office365.sharepoint.tenant.administration.policies.fileversionsettings import (
    SPOFileVersionPolicySettings,
)
from office365.sharepoint.tenant.administration.powerapps.environment import (
    PowerAppsEnvironment,
)
from office365.sharepoint.tenant.administration.reports.recent_admin_action import (
    RecentAdminActionReport,
)
from office365.sharepoint.tenant.administration.reports.recent_admin_action_payload import (
    RecentAdminActionReportPayload,
)
from office365.sharepoint.tenant.administration.secondary_administrators_fields_data import (
    SecondaryAdministratorsFieldsData,
)
from office365.sharepoint.tenant.administration.secondary_administrators_info import (
    SecondaryAdministratorsInfo,
)
from office365.sharepoint.tenant.administration.siteinfo_for_site_picker import (
    SiteInfoForSitePicker,
)
from office365.sharepoint.tenant.administration.sites.administrators_info import (
    SiteAdministratorsInfo,
)
from office365.sharepoint.tenant.administration.sites.creation_properties import (
    SiteCreationProperties,
)
from office365.sharepoint.tenant.administration.sites.properties import SiteProperties
from office365.sharepoint.tenant.administration.sites.properties_collection import (
    SitePropertiesCollection,
)
from office365.sharepoint.tenant.administration.sites.properties_enumerable_filter import (
    SitePropertiesEnumerableFilter,
)
from office365.sharepoint.tenant.administration.syntex.billing_context import (
    SyntexBillingContext,
)
from office365.sharepoint.tenant.administration.syntex.power_apps import (
    SyntexPowerAppsEnvironmentsContext,
)
from office365.sharepoint.tenant.administration.updategroupsitepropertiesparameters import (
    UpdateGroupSitePropertiesParameters,
)
from office365.sharepoint.tenant.administration.webs.templates.collection import (
    SPOTenantWebTemplateCollection,
)
from office365.sharepoint.tenant.settings import TenantSettings

if TYPE_CHECKING:
    from office365.sharepoint.administration.filerequestbrandingassetconfig import (
        FileRequestBrandingAssetConfig,
    )
    from office365.sharepoint.administration.orgassets.org_assets import OrgAssets
    from office365.sharepoint.administration.unlicensedodbtenantmetrics import (
        UnlicensedOdbTenantMetrics,
    )
    from office365.sharepoint.authpolicy.baseline_security_mode_third_party_app_hpa_setting import (
        BaselineSecurityModeThirdPartyAppHPASetting,
    )
    from office365.sharepoint.authpolicy.spjitdlppolicydata import SPJitDlpPolicyData
    from office365.sharepoint.brandcenter.configuration import BrandCenterConfiguration
    from office365.sharepoint.brandcenter.orgassetslibraryconfigparam import (
        OrgAssetsLibraryConfigParam,
    )
    from office365.sharepoint.lists.data_parameters import (
        RenderListFilterDataParameters,
    )
    from office365.sharepoint.sites.home.siteconfigurationparam import (
        HomeSiteConfigurationParam,
    )
    from office365.sharepoint.tenant.administration.authoritative_resource_properties import (
        AuthoritativeResourceProperties,
    )
    from office365.sharepoint.tenant.administration.bulk_insert_operation_result import (
        BulkInsertOperationResult,
    )
    from office365.sharepoint.tenant.administration.catalog_management_schema import (
        CatalogManagementSchema,
    )
    from office365.sharepoint.tenant.administration.catalog_management_settings import (
        CatalogManagementSettings,
    )
    from office365.sharepoint.tenant.administration.catalog_management_status import (
        CatalogManagementStatus,
    )
    from office365.sharepoint.tenant.administration.container.applicationproperties import (
        SPContainerApplicationProperties,
    )
    from office365.sharepoint.tenant.administration.container.collection import (
        SPContainerCollection,
    )
    from office365.sharepoint.tenant.administration.container.filterorder import (
        SPContainerFilterOrder,
    )
    from office365.sharepoint.tenant.administration.container.properties import (
        SPContainerProperties,
    )
    from office365.sharepoint.tenant.administration.container.searchparameters import (
        SPContainerSearchParameters,
    )
    from office365.sharepoint.tenant.administration.container.sortorder import (
        SPContainerSortOrder,
    )
    from office365.sharepoint.tenant.administration.container.type.configurationproperties import (
        SPContainerTypeConfigurationProperties,
    )
    from office365.sharepoint.tenant.administration.container.type.properties import (
        SPContainerTypeProperties,
    )
    from office365.sharepoint.tenant.administration.container.type.status import (
        SPContainerTypeStatus,
    )
    from office365.sharepoint.tenant.administration.contentmanagementassessmentoperationresult import (
        ContentManagementAssessmentOperationResult,
    )
    from office365.sharepoint.tenant.administration.contentmanagementassessmentresults import (
        ContentManagementAssessmentResults,
    )
    from office365.sharepoint.tenant.administration.copilot.transpilerpayload import (
        CopilotTranspilerPayload,
    )
    from office365.sharepoint.tenant.administration.copilot.transpilerresponse import (
        CopilotTranspilerResponse,
    )
    from office365.sharepoint.tenant.administration.dataset_metadata_request_info import (
        DatasetMetadataRequestInfo,
    )
    from office365.sharepoint.tenant.administration.dataset_metadata_response import (
        DatasetMetadataResponse,
    )
    from office365.sharepoint.tenant.administration.ibsegmentinfo import IBSegmentInfo
    from office365.sharepoint.tenant.administration.insights.queueitem import (
        InsightsQueueItem,
    )
    from office365.sharepoint.tenant.administration.insights.summary_response import (
        InsightsSummaryResponse,
    )
    from office365.sharepoint.tenant.administration.listitemcolumnvalue import (
        TenantAdminListItemColumnValue,
    )
    from office365.sharepoint.tenant.administration.onedrives_summary_metrics import (
        OneDrivesSummaryMetrics,
    )
    from office365.sharepoint.tenant.administration.policies.list_parameters import (
        SPOListParameters,
    )
    from office365.sharepoint.tenant.administration.ransomware.activitiesoverview import (
        TenantAdminRansomwareActivitiesOverview,
    )
    from office365.sharepoint.tenant.administration.ransomware.activity import (
        TenantAdminRansomwareActivity,
    )
    from office365.sharepoint.tenant.administration.ransomware.event import (
        TenantAdminRansomwareEvent,
    )
    from office365.sharepoint.tenant.administration.recent_action import (
        TenantAdminRecentAction,
    )
    from office365.sharepoint.tenant.administration.recentactionpayload import (
        TenantAdminRecentActionPayload,
    )
    from office365.sharepoint.tenant.administration.report_query_response import (
        ReportQueryResponse,
    )
    from office365.sharepoint.tenant.administration.settings.dataproperty import (
        SettingDataProperty,
    )
    from office365.sharepoint.tenant.administration.sharepointembeddedclientlogproperties import (
        SharePointEmbeddedClientLogProperties,
    )
    from office365.sharepoint.tenant.administration.siteadministratorsfieldsdata import (
        SiteAdministratorsFieldsData,
    )
    from office365.sharepoint.tenant.administration.sitecohortssummary import (
        SiteCohortsSummary,
    )
    from office365.sharepoint.tenant.administration.sites.creation_source import (
        SiteCreationSource,
    )
    from office365.sharepoint.tenant.administration.siteusergroupsdata import (
        SiteUserGroupsData,
    )
    from office365.sharepoint.tenant.administration.spdeletedcontainerproperties import (
        SPDeletedContainerProperties,
    )
    from office365.sharepoint.tenant.administration.spdeletedcontainertypeproperties import (
        SPDeletedContainerTypeProperties,
    )
    from office365.sharepoint.tenant.administration.spo_tenant_version_policy_impact import (
        SPOTenantVersionPolicyImpact,
    )
    from office365.sharepoint.tenant.administration.spocontainerqueryparams import (
        SPOContainerQueryParams,
    )
    from office365.sharepoint.tenant.administration.spofileversionexpirationreportjobprogress import (
        SPOFileVersionExpirationReportJobProgress,
    )
    from office365.sharepoint.tenant.administration.spofileversionfiletypepolicysettings import (
        SPOFileVersionFileTypePolicySettings,
    )
    from office365.sharepoint.tenant.administration.sposerviceprioritizationappregistrations import (
        SPOServicePrioritizationAppRegistrations,
    )
    from office365.sharepoint.tenant.administration.sposerviceprioritizationbillingpayload import (
        SPOServicePrioritizationBillingPayload,
    )
    from office365.sharepoint.tenant.administration.sposerviceprioritizationpolicyfromtenantstore import (
        SPOServicePrioritizationPolicyFromTenantStore,
    )
    from office365.sharepoint.tenant.administration.spositecreationsource import (
        SPOSiteCreationSource,
    )
    from office365.sharepoint.tenant.administration.syntex.applicationproperties import (
        SPSyntexApplicationProperties,
    )
    from office365.sharepoint.tenant.administration.syntex.premiumfeaturesettings import (
        SyntexPremiumFeatureSettings,
    )
    from office365.sharepoint.tenant.administration.tenant_data_loss_prevention_quarantine_settings import (
        TenantDataLossPreventionQuarantineSettings,
    )
    from office365.sharepoint.tenantadministration.catalog_management_collection import (
        CatalogManagementCollection,
    )
    from office365.sharepoint.tenantadministration.catalog_management_custom_properties_collection import (
        CatalogManagementCustomPropertiesCollection,
    )
    from office365.sharepoint.tenantadministration.catalog_management_restricted_content_discovery_collection import (
        CatalogManagementRestrictedContentDiscoveryCollection,
    )
    from office365.sharepoint.tenantadministration.spo_file_archive_policy_info import (
        SPOFileArchivePolicyInfo,
    )
    from office365.sharepoint.tenantadministration.spo_file_archive_policy_report_info import (
        SPOFileArchivePolicyReportInfo,
    )
    from office365.sharepoint.tenantadministration.spo_file_archive_policy_site_info import (
        SPOFileArchivePolicySiteInfo,
    )
    from office365.sharepoint.viva.connections.license import VivaConnectionsLicense
    from office365.sharepoint.viva.syntexcustommodelsetting import (
        SyntexCustomModelSetting,
    )
    from office365.sharepoint.viva.targetedsitedetails import TargetedSiteDetails


class Tenant(Entity):
    """Represents a SharePoint tenant."""

    def __init__(self, context):
        super().__init__(context, StaticPath("Microsoft.Online.SharePoint.TenantAdministration.Tenant"))

    def accept_syntex_repository_terms_of_service(self) -> Self:
        """
        Used to accept the Microsoft Syntex repository terms of service for your organization.
        This acceptance is often necessary for enabling features related to document processing or repositories
        in Microsoft Syntex.
        """
        qry = ServiceOperationQuery(self, "AcceptSyntexRepositoryTermsOfService")
        self.context.add_query(qry)
        return self

    def activate_application_billing_policy(self, billing_policy_id: str) -> ClientResult[SPOAppBillingProperties]:
        """ """
        payload = {"billingPolicyId": billing_policy_id}
        return_type = ClientResult(self.context, SPOAppBillingProperties())
        qry = ServiceOperationQuery(self, "ActivateApplicationBillingPolicy", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add_recent_admin_action_report(self) -> ClientResult[RecentAdminActionReport]:
        """Logs recent administrative actions within a SharePoint Online tenant"""
        return_type = ClientResult(self.context, RecentAdminActionReport())
        payload = {"payload": RecentAdminActionReportPayload()}
        qry = ServiceOperationQuery(self, "AddRecentAdminActionReport", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def check_m365_copilot_business_chat_license(self) -> ClientResult[bool]:
        """ """
        return_type = ClientResult(self.context, bool())
        from office365.sharepoint.policy.license_utilities import PolicyLicenseUtilities

        PolicyLicenseUtilities.check_tenant_m365_copilot_business_chat_license(self.context)
        return return_type

    def get_corporate_catalog_site(self) -> Site:
        """Retrieves Corporate Catalog Site"""
        settings = TenantSettings.current(self.context)
        return_type = Site(self.context)

        def _settings_loaded():
            return_type.set_property("__siteUrl", settings.corporate_catalog_url)

        settings.ensure_property("CorporateCatalogUrl").after_execute(lambda _: _settings_loaded())
        return return_type

    def get_chat_gpt_response(self) -> ClientResult[ChatGptRequestOptions]:
        """"""
        return_type = ClientResult(self.context)
        payload = {"requestOptions": ChatGptRequestOptions()}
        qry = ServiceOperationQuery(self, "GetChatGptResponse", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_spo_copilot_promo_usage_statistics(self) -> ClientResult[SPOCopilotPromoUsage]:
        """ """
        return_type = ClientResult(self.context, SPOCopilotPromoUsage())
        qry = ServiceOperationQuery(self, "GetSPOCopilotPromoUsageStatistics", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def delete_policy_definition(self, item_id: int) -> Self:
        """Deletes a policy definition from a Microsoft 365 tenant.
        Policy definitions may refer to specific settings related to compliance, security,
        or site governance (such as site or group creation policies).

        Args:
            item_id (int):
        """
        qry = ServiceOperationQuery(self, "DeletePolicyDefinition", None, {"itemId": item_id})
        self.context.add_query(qry)
        return self

    def delete_recent_admin_action_report(self, report_id: int):
        """Args:
        report_id (int):
        """
        qry = ServiceOperationQuery(self, "DeleteRecentAdminActionReport", None, {"reportId": report_id})
        self.context.add_query(qry)
        return self

    def get_spo_tenant_all_web_templates(self) -> SPOTenantWebTemplateCollection:
        """ """
        return_type = SPOTenantWebTemplateCollection(self.context)
        qry = ServiceOperationQuery(self, "GetSPOTenantAllWebTemplates", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_onedrive_site_sharing_insights(self, query_mode):
        """Retrieves insights or reports related to OneDrive for Business site sharing activities"""
        return_type = ClientResult(self.context, OneDriveSiteSharingInsights())
        payload = {"queryMode": query_mode}
        qry = ServiceOperationQuery(self, "GetOneDriveSiteSharingInsights", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_collaboration_insights_data(self):
        """"""
        return_type = ClientResult[CollaborationInsightsData](self.context, CollaborationInsightsData())
        qry = ServiceOperationQuery(self, "GetCollaborationInsightsData", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_collaboration_insights_overview(self) -> ClientResult[CollaborationInsightsOverview]:
        """"""
        return_type = ClientResult(self.context, CollaborationInsightsOverview())
        qry = ServiceOperationQuery(self, "GetCollaborationInsightsOverview", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def render_recent_admin_actions(self) -> ClientResult[bytes]:
        """ """
        return_type = ClientResult(self.context, bytes())
        payload = {"parameters": RenderListDataParameters(), "overrideParameters": RenderListDataOverrideParameters()}
        qry = ServiceOperationQuery(self, "RenderRecentAdminActions", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_content_security_policy(self) -> SPOContentSecurityPolicyConfiguration:
        """"""
        return_type = SPOContentSecurityPolicyConfiguration(self.context)
        qry = ServiceOperationQuery(self, "GetContentSecurityPolicy", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_spo_app_billing_policies(self):
        """ """
        return_type = ClientResult(self.context, ClientValueCollection(SPOAppBillingProperties))
        qry = ServiceOperationQuery(self, "GetSPOAppBillingPolicies", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_top_files_sharing_insights(self, query_mode=None):
        """Retrieves a report or data about the most shared files within a SharePoint Online tenant

        Args:
            query_mode (int):
        """
        payload = {"queryMode": query_mode}
        return_type = EntityCollection(self.context, TopFilesSharingInsights)
        qry = ServiceOperationQuery(self, "GetTopFilesSharingInsights", payload, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_thumbnail_logo(self, site_url: str) -> ClientResult[AnyStr]:
        """Args:
        site_url (str):
        """
        payload = {"siteUrl": site_url}
        return_type = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "GetSiteThumbnailLogo", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_home_site_url(self) -> ClientResult[str]:
        """ """
        return_type = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "GetSPHSiteUrl", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_home_sites(self) -> ClientResult[ClientValueCollection[HomeSitesDetails]]:
        """Retrieves the Home Site that has been designated for your Microsoft 365 tenant."""
        return_type = ClientResult(self.context, ClientValueCollection(HomeSitesDetails))
        qry = ServiceOperationQuery(self, "GetHomeSites", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_home_sites_details(self):
        """Retrieves detailed information about the Home Sites configured in a SharePoint Online tenant."""
        return_type = ClientResult(self.context, ClientValueCollection(HomeSitesDetails))
        qry = ServiceOperationQuery(self, "GetHomeSitesDetails", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def remove_home_site(self, home_site_url: str) -> Self:
        """Remove home site

        Args:
            home_site_url (str):
        """
        payload = {"homeSiteUrl": home_site_url}
        qry = ServiceOperationQuery(self, "RemoveHomeSite", None, payload)
        self.context.add_query(qry)
        return self

    def has_valid_education_license(self) -> ClientResult[bool]:
        """"""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "HasValidEducationLicense", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def is_request_content_management_assessment_eligible(self) -> ClientResult[bool]:
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "IsRequestContentManagementAssessmentEligible", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def is_syntex_repository_terms_of_service_accepted(self) -> ClientResult[bool]:
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "IsSyntexRepositoryTermsOfServiceAccepted", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def export_to_csv(
        self,
        view_xml: Optional[str] = None,
        time_zone_id: Optional[int] = None,
        columns_info=None,
        list_name: Optional[str] = None,
    ):
        """Exports tenant-level data to a CSV file.

        Args:
            view_xml (str):
            time_zone_id (int):
            columns_info (list):
            list_name (str):
        """
        return_type = ClientResult(self.context)
        payload = {"viewXml": view_xml, "timeZoneId": time_zone_id, "columnsInfo": columns_info, "listName": list_name}
        qry = ServiceOperationQuery(self, "ExportToCSV", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def render_policy_report(self) -> ClientResult[bytes]:
        """"""
        return_type = ClientResult(self.context, bytes())
        payload = {"parameters": RenderListDataParameters(), "overrideParameters": RenderListDataOverrideParameters()}
        qry = ServiceOperationQuery(self, "RenderPolicyReport", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @staticmethod
    def from_url(admin_site_url: str):
        """Args:
        admin_site_url (str):
        """
        from office365.sharepoint.client_context import ClientContext

        admin_client = ClientContext(admin_site_url)
        return Tenant(admin_client)

    def get_lock_state_by_id(self, site_id: str) -> ClientResult[int]:
        """Args:
        site_id (str): The GUID to uniquely identify a SharePoint site
        """
        return self.sites.get_lock_state_by_id(site_id)

    def get_hub_sites(self) -> HubSiteCollection:
        """Gets information about all hub sites that the current user can access.

        Delegates to SPHubSitesUtility.GetHubSites().
        """
        return SPHubSitesUtility(self.context).get_hub_sites()

    def get_power_apps_environments(self):
        """ """
        return_type = ClientResult(self.context, ClientValueCollection(PowerAppsEnvironment))
        qry = ServiceOperationQuery(self, "GetPowerAppsEnvironments", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_ransomware_activities(self) -> ClientResult[bytes]:
        """ """
        return_type = ClientResult(self.context, bytes())
        payload = {"parameters": RenderListDataParameters()}
        qry = ServiceOperationQuery(self, "GetRansomwareActivities", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_ransomware_events_overview(self) -> ClientResult[bytes]:
        """ """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(self, "GetRansomwareEventsOverview", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_root_site_url(self) -> ClientResult[str]:
        """ """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetRootSiteUrl", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_authorization_code_for_migration(self, endpoint_url: str) -> ClientResult[str]:
        return_type = ClientResult(self.context, str())
        payload = {"endpointUrl": endpoint_url}
        qry = ServiceOperationQuery(self, "GetSiteAuthorizationCodeForMigration", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_subscription_id(self):
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetSiteSubscriptionId", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_sp_list_item_count(self, list_name: str) -> ClientResult[int]:
        """ """
        return_type = ClientResult(self.context, int())
        payload = {"listName": list_name}
        qry = ServiceOperationQuery(self, "GetSPListItemCount", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_sp_list_root_folder_properties(self, list_name: str) -> ClientResult[dict]:
        """ """
        return_type = ClientResult(self.context, dict())
        payload = {"listName": list_name}
        qry = ServiceOperationQuery(self, "GetSPListRootFolderProperties", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_spo_all_web_templates(
        self, culture_name: Optional[str] = None, compatibility_level: Optional[int] = None
    ) -> SPOTenantWebTemplateCollection:
        """ """
        return_type = SPOTenantWebTemplateCollection(self.context)
        payload = {"cultureName": culture_name, "compatibilityLevel": compatibility_level}
        qry = ServiceOperationQuery(self, "GetSPOAllWebTemplates", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def check_tenant_intune_license(self) -> ClientResult[bool]:
        """Checks whether a tenant has the Intune license."""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "CheckTenantIntuneLicense", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def check_tenant_licenses(self, licenses: List[str]) -> ClientResult[bool]:
        """Checks whether a tenant has the specified licenses.

        Args:
            licenses (list[str]): The list of licenses to check for.
        """
        return_type = ClientResult(self.context, bool())
        params = ClientValueCollection(str, licenses)
        qry = ServiceOperationQuery(self, "CheckTenantLicenses", None, params, "licenses", return_type)
        self.context.add_query(qry)
        return return_type

    def get_site(self, site_url: str) -> ListItem:
        return self._aggregated_site_collections_list.items.single(f"SiteUrl eq '{site_url.rstrip('/')}'").get()

    def get_sites_by_state(self, states: Optional[List[int]] = None):
        """Args:
        states (list[int]):
        """
        return_type = ListItemCollection(
            self.context, ResourcePath("items", self._aggregated_site_collections_list.resource_path)
        )
        payload = {"states": states}
        qry = ServiceOperationQuery(self, "GetSitesByState", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def _poll_site_status(self, site_url: str, polling_interval_secs: float) -> None:
        states = [0, 1, 2]
        time.sleep(polling_interval_secs)

        def _after(items):
            completed = len([item for item in items if item.properties.get("SiteUrl") == site_url]) > 0
            if not completed:
                self._poll_site_status(site_url, polling_interval_secs)

        self.get_sites_by_state(states).after_execute(_after, execute_first=True)

    def get_site_health_status(self, source_url: str) -> ClientResult[PortalHealthStatus]:
        """Checks the sitehealth of a specific SharePoint site or site collection in their tenant

        Args:
            source_url (str):
        """
        result = ClientResult(self.context, PortalHealthStatus())
        params = {"sourceUrl": source_url}
        qry = ServiceOperationQuery(self, "GetSiteHealthStatus", None, params, None, result)
        self.context.add_query(qry)
        return result

    def get_site_administrators(
        self, site_id: str, return_type: Optional[ClientResult[ClientValueCollection[SiteAdministratorsInfo]]] = None
    ):
        """Gets site collection administrators

        Args:
            site_id (str):
            return_type (ClientResult):
        """
        if return_type is None:
            return_type = ClientResult(self.context, ClientValueCollection(SiteAdministratorsInfo))
        payload = {"siteId": site_id}
        qry = ServiceOperationQuery(self, "GetSiteAdministrators", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_administrators_by_site_url(self, site_url: str):
        """
        Gets site collection administrators

        """
        return_type = ClientResult(self.context, ClientValueCollection(SiteAdministratorsInfo))

        def _get_site_administrators_by_site_url(site_props: SiteProperties) -> None:
            self.get_site_administrators(site_props.get_property("SiteId"), return_type)

        self.get_site_properties_by_url(site_url).after_execute(_get_site_administrators_by_site_url)
        return return_type

    def get_site_secondary_administrators(
        self,
        site_id: str,
        return_type: Optional[ClientResult[ClientValueCollection[SecondaryAdministratorsInfo]]] = None,
    ) -> ClientResult[ClientValueCollection[SecondaryAdministratorsInfo]]:
        """
        Gets site collection administrators
        """
        if return_type is None:
            return_type = ClientResult(self.context, ClientValueCollection(SecondaryAdministratorsInfo))
        payload = {"secondaryAdministratorsFieldsData": SecondaryAdministratorsFieldsData(site_id)}
        qry = ServiceOperationQuery(self, "GetSiteSecondaryAdministrators", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_secondary_administrators_by_site_url(
        self, site_url: str
    ) -> ClientResult[ClientValueCollection[SecondaryAdministratorsInfo]]:
        """
        Gets site collection administrators
        """
        return_type = ClientResult(self.context, ClientValueCollection(SecondaryAdministratorsInfo))

        def _get_site_secondary_administrators_by_site_url(site_props: SiteProperties) -> None:
            self.get_site_secondary_administrators(site_props.get_property("SiteId"), return_type)

        self.get_site_properties_by_url(site_url).after_execute(_get_site_secondary_administrators_by_site_url)
        return return_type

    def set_site_secondary_administrators(
        self, site_id: str, emails: Optional[List[str]] = None, names: Optional[List[str]] = None
    ) -> Self:
        """
        Sets site collection administrators
        """
        payload = {
            "secondaryAdministratorsFieldsData": SecondaryAdministratorsFieldsData(
                site_id, StringCollection(emails or []), StringCollection(names or [])
            )
        }
        qry = ServiceOperationQuery(self, "SetSiteSecondaryAdministrators", None, payload, None, None)
        self.context.add_query(qry)
        return self

    def set_site_secondary_administrators_by_site_url(
        self, site_url: str, emails: Optional[List[str]] = None, names: Optional[List[str]] = None
    ) -> Self:
        """
        Sets site collection administrators
        """

        def _set_site_secondary_administrators_by_site_url(site_props: SiteProperties) -> None:
            self.set_site_secondary_administrators(site_props.get_property("SiteId"), emails, names)

        self.get_site_properties_by_url(site_url).after_execute(_set_site_secondary_administrators_by_site_url)
        return self

    def clear_site_secondary_administrators(self, site_url: str) -> Self:
        """Clears site collection administrators"""

        def _clear_site_secondary_administrators(site_props: SiteProperties):
            self.set_site_secondary_administrators(site_props.get_property("SiteId"), emails=[])

        self.get_site_properties_by_url(site_url).after_execute(_clear_site_secondary_administrators)
        return self

    def register_hub_site(self, site_url: str) -> HubSiteProperties:
        """Registers an existing site as a hub site."""
        return_type = HubSiteProperties(self.context)
        params = {"siteUrl": site_url}
        qry = ServiceOperationQuery(self, "RegisterHubSite", None, params, None, return_type)
        self.context.add_query(qry)
        return return_type

    def unregister_hub_site(self, site_url: str) -> Self:
        """Unregisters a hub site so that it is no longer a hub site."""
        payload = {"siteUrl": site_url}
        qry = ServiceOperationQuery(self, "UnregisterHubSite", None, payload, None, None)
        self.context.add_query(qry)
        return self

    def create_policy_definition(self) -> ClientResult[TenantAdminPolicyDefinition]:
        """ """
        return_type = ClientResult(self.context, TenantAdminPolicyDefinition())
        payload = {"policyInputParameters": CreatePolicyRequest()}
        qry = ServiceOperationQuery(self, "CreatePolicyDefinition", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def create_site(self, url: str, owner: str, title: Optional[str] = None) -> SpoOperation:
        """Queues a site collection for creation with the specified properties.

        Args:
            title (str): Sets the new site’s title.
            url (str): Sets the new site’s URL.
            owner (str): Sets the login name of the owner of the new site.
        """
        return_type = SpoOperation(self.context)
        payload = {"siteCreationProperties": SiteCreationProperties(Title=title, Url=url, Owner=owner)}
        qry = ServiceOperationQuery(self, "CreateSite", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def create_site_sync(self, url: str, owner: str, title: Optional[str] = None) -> Site:
        """Creates a site collection

        Args:
            title (str): Sets the new site’s title.
            url (str): Sets the new site’s URL.
            owner (str): Sets the login name of the owner of the new site.
        """
        return_type = Site(self.context)

        def _ensure_status(op: SpoOperation) -> None:
            return_type.set_property("__siteUrl", url)
            if not op.is_complete:
                self._poll_site_status(url, op.polling_interval_secs or 0)

        self.create_site(url, owner, title).after_execute(_ensure_status)
        return return_type

    def remove_site(self, site_url: str) -> SpoOperation:
        """Deletes the site with the specified URL

        Args:
            site_url (str): A string representing the URL of the site.
        """
        return_type = SpoOperation(self.context)
        params = {"siteUrl": site_url}
        qry = ServiceOperationQuery(self, "removeSite", None, params, None, return_type)
        self.context.add_query(qry)
        return return_type

    def remove_site_sync(self, site_url: str) -> Self:
        def _remove_site_sync(op: SpoOperation):
            if not op.is_complete:
                self._poll_site_status(site_url, op.polling_interval_secs or 0)

        self.remove_site(site_url).after_execute(_remove_site_sync)
        return self

    def remove_deleted_site(self, site_url: str) -> SpoOperation:
        """Permanently removes the specified deleted site from the recycle bin.

        Args:
            site_url (str): A string representing the URL of the site.
        """
        result = SpoOperation(self.context)
        payload = {"siteUrl": site_url}
        qry = ServiceOperationQuery(self, "RemoveDeletedSite", None, payload, None, result)
        self.context.add_query(qry)
        return result

    def remove_deleted_sites(
        self, site_urls: List[str], success_callback: Optional[Callable[[SpoOperation, str], None]] = None
    ) -> Self:
        def _remove_next_deleted_site(op: Optional[SpoOperation] = None):
            if site_urls:
                site_url = site_urls.pop(0)
                if op and success_callback:
                    success_callback(op, site_url)
                self.remove_deleted_site(site_url).after_execute(_remove_next_deleted_site)

        _remove_next_deleted_site()
        return self

    def reorder_home_sites(
        self, home_sites_site_ids: List[str]
    ) -> ClientResult[ClientValueCollection[HomeSitesDetails]]:
        """Reorders Home Sites within a SharePoint Online tenant

        Args:
            home_sites_site_ids (list[str]):
        """
        payload = {"homeSitesSiteIds": home_sites_site_ids}
        return_type = ClientResult(self.context, ClientValueCollection(HomeSitesDetails))
        qry = ServiceOperationQuery(self, "ReorderHomeSites", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def restore_deleted_site(self, site_url: str):
        """Restores deleted site with the specified URL

        Args:
            site_url (str): A string representing the URL of the site.
        """
        return_type = SpoOperation(self.context)
        qry = ServiceOperationQuery(self, "RestoreDeletedSite", [site_url], None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def restore_deleted_site_by_id(self, site_id: str):
        """Restores deleted site with the specified URL

        Args:
            site_id (str): A string representing the site identifier.
        """
        return_type = SpoOperation(self.context)
        qry = ServiceOperationQuery(self, "RestoreDeletedSiteById", [site_id], None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_file_version_policy_for_library(self, site_url: str, list_params=None):
        """ """
        return_type = ClientResult(self.context, SPOFileVersionPolicySettings())
        payload = {"siteUrl": site_url, "listParams": list_params}
        qry = ServiceOperationQuery(self, "GetFileVersionPolicyForLibrary", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_file_version_batch_delete_job_progress_for_library(self, site_url, list_params):
        """Gets the progress of the file version batch delete job for the specified site and list parameters."""
        return_type = ClientResult(self.context, SPOFileVersionBatchDeleteJobProgress())
        payload = {"siteUrl": site_url, "listParams": list_params}
        qry = ServiceOperationQuery(
            self, "GetFileVersionBatchDeleteJobProgressForLibrary", None, payload, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_site_properties_by_site_id(self, site_id: str, include_detail: bool = False) -> SiteProperties:
        """Gets the site properties for the specified site ID.

        Args:
            site_id (str): A string that represents the site identifier.
            include_detail (bool): A Boolean value that indicates whether to include all of the SPSite properties.
        """
        return_type = SiteProperties(self.context)
        return_type.set_property("siteId", site_id, False)
        self.sites.add_child(return_type)
        payload = {"siteId": site_id, "includeDetail": include_detail}
        qry = ServiceOperationQuery(self, "GetSitePropertiesBySiteId", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_properties_by_url(self, url: str, include_detail: bool = False) -> SiteProperties:
        """Gets the site properties for the specified URL.

        Args:
            url (str): A string that represents the site URL.
            include_detail (bool): A Boolean value that indicates whether to include all of the SPSite properties.
        """
        return_type = SiteProperties(self.context)
        return_type.set_property("Url", url, False)
        self.sites.add_child(return_type)
        payload = {"url": url, "includeDetail": include_detail}
        qry = ServiceOperationQuery(self, "getSitePropertiesByUrl", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_properties_from_sharepoint(
        self, start_index: Optional[str] = None, include_detail: bool = False
    ) -> SitePropertiesCollection:
        """ """
        return_type = SitePropertiesCollection(self.context, self.sites.resource_path)
        payload = {"startIndex": start_index, "includeDetail": include_detail}
        qry = ServiceOperationQuery(self, "getSitePropertiesFromSharePoint", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_properties_from_sharepoint_by_filters(
        self, filter_text: Optional[str] = None, start_index: Optional[str] = None, include_detail: bool = False
    ) -> SitePropertiesCollection:
        """ """
        return_type = SitePropertiesCollection(self.context, self.sites.resource_path)
        payload = {"speFilter": SitePropertiesEnumerableFilter(filter_text, start_index, include_detail)}
        qry = ServiceOperationQuery(self, "getSitePropertiesFromSharePointByFilters", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_deleted_site_properties(self, start_index: Optional[int] = None) -> EntityCollection[DeletedSiteProperties]:
        """ """
        return_type = EntityCollection(self.context, DeletedSiteProperties)
        payload = {"startIndex": start_index}
        qry = ServiceOperationQuery(self, "GetDeletedSiteProperties", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_billing_policy_id_for_app(self, application_id: str) -> ClientResult[str]:
        """ """
        return_type = ClientResult(self.context)
        payload = {"applicationId": application_id}
        qry = ServiceOperationQuery(self, "GetBillingPolicyIdForApp", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def connect_site_to_hub_site_by_id(self, site_url: str, hub_site_id: str) -> Self:
        """Connects Site to Hub Site

        Args:
            site_url (str):
            hub_site_id (str):
        """
        params = {"siteUrl": site_url, "hubSiteId": hub_site_id}
        qry = ServiceOperationQuery(self, "ConnectSiteToHubSiteById", None, params, None, None)
        self.context.add_query(qry)
        return self

    def ensure_brand_center_feature(self):
        """Ensures that the Brand Center feature is enabled"""
        qry = ServiceOperationQuery(self, "EnsureBrandCenterFeature")
        self.context.add_query(qry)
        return self

    def export_unlicensed_one_drive_for_business_list_to_csv(self):
        """Exports a list of OneDrive for Business sites that are associated with unlicensed users into a CSV file"""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "ExportUnlicensedOneDriveForBusinessListToCSV")
        self.context.add_query(qry)
        return return_type

    def send_email(self, site_url: str, activity_event_json: str) -> ClientResult[bool]:
        """Send Email"""
        return_type = ClientResult(self.context, bool())
        payload = {"siteUrl": site_url, "activityEventJson": activity_event_json}
        qry = ServiceOperationQuery(self, "SendEmail", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def set_copilot_promo_optin_status(self, copilot_promo_optin_enabled: bool) -> Self:
        """ """
        payload = {"copilotPromoOptInEnabled": copilot_promo_optin_enabled}
        qry = ServiceOperationQuery(self, "SetCopilotPromoOptInStatus", None, payload)
        self.context.add_query(qry)
        return self

    def set_default_view(self, view_id: str, list_name: str) -> Self:
        """ """
        payload = {"viewId": view_id, "listName": list_name}
        qry = ServiceOperationQuery(self, "SetDefaultView", None, payload)
        self.context.add_query(qry)
        return self

    def get_file_version_policy(self):
        return_type = ClientResult(self.context, str())

        def _get_file_version_policy():
            return_type.set_property("__value", self.file_version_policy_xml)

        self.ensure_property("FileVersionPolicyXml").after_execute(lambda _: _get_file_version_policy())
        return return_type

    def set_file_version_policy(
        self, is_auto_trim_enabled: bool, major_version_limit: int, expire_versions_after_days: int
    ) -> Self:
        """Automatically delete older versions of documents after a specified number of days.
        Specify the maximum number of major versions to retain and the number of major versions
        for which all minor versions will be kept.

        Args:
            is_auto_trim_enabled (bool): If true, versions are trimmed automatically.
            major_version_limit (int): Retains only many major versions.
            expire_versions_after_days (int): Deletes versions older than this many days.
        """
        payload = {
            "isAutoTrimEnabled": is_auto_trim_enabled,
            "majorVersionLimit": major_version_limit,
            "expireVersionsAfterDays": expire_versions_after_days,
        }
        qry = ServiceOperationQuery(self, "SetFileVersionPolicy", None, payload)
        self.context.add_query(qry)
        return self

    def clear_file_version_policy(self) -> Self:
        self.set_property("FileVersionPolicyXml", "")
        self.update()
        return self

    def update_site_activity_data(self) -> Self:
        """ """
        qry = ServiceOperationQuery(self, "UpdateSiteActivityData")
        self.context.add_query(qry)
        return self

    def update_group_site_properties(
        self,
        group_id: str,
        site_id: str,
        update_type: str,
        parameters: Optional[UpdateGroupSitePropertiesParameters] = None,
    ):
        """ """
        return_type = ClientResult(self.context, str())
        payload = {"groupId": group_id, "siteId": site_id, "updateType": update_type, "parameters": parameters}
        qry = ServiceOperationQuery(self, "UpdateGroupSiteProperties", None, payload, None, return_type)
        self.context.add_query(qry)
        return self

    @property
    def app_service_principal(self):
        """ """
        from office365.sharepoint.tenant.administration.internal.appservice.principal import (
            SPOWebAppServicePrincipal,
        )

        return SPOWebAppServicePrincipal(self.context)

    @property
    def admin_settings(self):
        """Manage various tenant-level settings related to SharePoint administration"""
        from office365.sharepoint.tenant.administration.settings.service import (
            TenantAdminSettingsService,
        )

        return TenantAdminSettingsService(self.context)

    @property
    def migration_center(self):
        """ """
        from office365.sharepoint.migrationcenter.service.services import (
            MigrationCenterServices,
        )

        return MigrationCenterServices(self.context)

    @property
    def comms_messages(self):
        """ """
        from office365.sharepoint.tenant.administration.coms.messages_service_proxy import (
            Office365CommsMessagesServiceProxy,
        )

        return Office365CommsMessagesServiceProxy(self.context)

    @property
    def multi_geo(self):
        """ """
        from office365.sharepoint.multigeo.service.services import MultiGeoServices

        return MultiGeoServices(self.context)

    @property
    def ai_builder_enabled(self) -> Optional[str]:
        """Gets the value if the AIBuilder settings should be shown in the tenant"""
        return self.properties.get("AIBuilderEnabled", None)

    @property
    def ai_builder_site_info_list(self) -> ClientValueCollection[SiteInfoForSitePicker]:
        """"""
        return self.properties.get("AIBuilderSiteInfoList", ClientValueCollection(SiteInfoForSitePicker))

    @property
    def _aggregated_site_collections_list(self):
        """ """
        return self.context.web.lists.get_by_title("DO_NOT_DELETE_SPLIST_TENANTADMIN_AGGREGATED_SITECOLLECTIONS")

    @property
    def allow_comments_text_on_email_enabled(self) -> Optional[bool]:
        """
        When enabled, the email notification that a user receives when is mentioned,
        includes the surrounding document context
        """
        return self.properties.get("AllowCommentsTextOnEmailEnabled", None)

    @property
    def allow_everyone_except_external_users_claim_in_private_site(self) -> Optional[bool]:
        """
        Gets the value if EveryoneExceptExternalUsers claim is allowed or not in people picker in a private group site.
        False value means it is blocked
        """
        return self.properties.get("AllowEveryoneExceptExternalUsersClaimInPrivateSite", None)

    @property
    def allow_editing(self) -> Optional[bool]:
        """
        Prevents users from editing Office files in the browser and copying and pasting Office file contents
        out of the browser window.
        """
        return self.properties.get("AllowEditing", None)

    @property
    def default_content_center_site(self) -> SiteInfoForSitePicker:
        """"""
        return self.properties.get("DefaultContentCenterSite", SiteInfoForSitePicker())

    @property
    def file_version_policy_xml(self) -> Optional[str]:
        """ """
        return self.properties.get("FileVersionPolicyXml", None)

    @property
    def information_barriers_suspension(self) -> Optional[bool]:
        """Gets information barriers in SharePoint and OneDrive in your organization"""
        return self.properties.get("InformationBarriersSuspension", None)

    @property
    def ip_address_allow_list(self) -> Optional[str]:
        """Configures multiple IP addresses or IP address ranges (IPv4 or IPv6), that are recognized as trusted."""
        return self.properties.get("IPAddressAllowList", None)

    @property
    def ip_address_enforcement(self) -> Optional[bool]:
        """Determines whether access from network locations that are defined by an administrator is allowed."""
        return self.properties.get("IPAddressEnforcement", None)

    @ip_address_enforcement.setter
    def ip_address_enforcement(self, value: bool) -> None:
        """
        Allows access from network locations that are defined by an administrator.
        Before the IPAddressEnforcement parameter is set, make sure you add a valid IPv4 or IPv6 address to the
        IPAddressAllowList parameter.
        """
        self.set_property("IPAddressEnforcement", value)

    @property
    def no_access_redirect_url(self) -> Optional[bool]:
        """Specifies the URL of the redirected site for those site collections which have the locked state "NoAccess"""
        return self.properties.get("NoAccessRedirectUrl", None)

    @property
    def legacy_auth_protocols_enabled(self) -> Optional[bool]:
        """Gets legacy authentication protocols on the tenant"""
        return self.properties.get("LegacyAuthProtocolsEnabled", None)

    @property
    def notifications_in_share_point_enabled(self) -> Optional[bool]:
        """Enables or disables notifications in SharePoint."""
        return self.properties.get("NotificationsInSharePointEnabled", None)

    @property
    def notify_owners_when_invitations_accepted(self) -> Optional[bool]:
        """When this parameter is set to true and when an external user accepts an invitation to a resource
        in a user's OneDrive for Business, the OneDrive for Business owner is notified by e-mail.
        """
        return self.properties.get("NotifyOwnersWhenInvitationsAccepted", None)

    @property
    def one_drive_storage_quota(self) -> Optional[int]:
        """Gets a default OneDrive for Business storage quota for the tenant. It will be used for new OneDrive
        for Business sites created."""
        return self.properties.get("OneDriveStorageQuota", None)

    @property
    def notify_owners_when_items_reshared(self) -> Optional[bool]:
        """When is set to true and another user re-shares a document from a
        user's OneDrive for Business, the OneDrive for Business owner is notified by e-mail.
        """
        return self.properties.get("NotifyOwnersWhenItemsReshared", None)

    @property
    def one_drive_default_link_to_existing_access(self) -> Optional[str]:
        """ """
        return self.properties.get("OneDriveDefaultLinkToExistingAccess", None)

    @property
    def root_site_url(self) -> Optional[str]:
        """The tenant's root site url"""
        return self.properties.get("RootSiteUrl", None)

    @property
    def sites(self) -> SitePropertiesCollection:
        """Gets a collection of sites."""
        return self.properties.get(
            "sites", SitePropertiesCollection(self.context, ResourcePath("sites", self.resource_path))
        )

    @property
    def total_tenant_archive_file_size_aggregation(self) -> ArchiveFileSizeMetric:
        """ """
        return self.properties.get(
            "TotalTenantArchiveFileSizeAggregation",
            ArchiveFileSizeMetric(
                self.context, ResourcePath("TotalTenantArchiveFileSizeAggregation", self.resource_path)
            ),
        )

    @property
    def syntex_power_apps_environments_context(self) -> SyntexPowerAppsEnvironmentsContext:
        """ """
        return self.properties.get("SyntexPowerAppsEnvironmentsContext", SyntexPowerAppsEnvironmentsContext())

    @property
    def taxonomy_tagging_enabled(self) -> Optional[bool]:
        """ """
        return self.properties.get("TaxonomyTaggingEnabled", None)

    @property
    def cdn_api(self):
        """ """
        from office365.sharepoint.tenant.cdn_api import TenantCdnApi

        return TenantCdnApi(self.context)

    @property
    def crawl_versions_info_provider(self):
        """Retrieves information about crawl versions for a tenant in SharePoint"""
        from office365.sharepoint.search.administration.providers.crawl_versions_info import (
            TenantCrawlVersionsInfoProvider,
        )

        return TenantCrawlVersionsInfoProvider(self.context)

    @property
    def syntex_billing_subscription_settings(self) -> SyntexBillingContext:
        """
        Manages billing and subscription details for Microsoft Syntex in SharePoint Online or Microsoft 365 environments
        """
        return self.properties.get("SyntexBillingSubscriptionSettings", SyntexBillingContext())

    @property
    def admin_endpoints(self):
        """ """
        from office365.sharepoint.tenant.administration.endpoints import (
            TenantAdminEndpoints,
        )

        return TenantAdminEndpoints(self.context)

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.Tenant"

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def id_(self) -> Optional[UUID]:
        """Gets the id property"""
        return self.properties.get("id", None)

    @property
    def service_info(self) -> ClientValueCollection[TenantServiceInfoValue]:
        """Gets the serviceInfo property"""
        return self.properties.get("serviceInfo", ClientValueCollection[TenantServiceInfoValue](TenantServiceInfoValue))

    def create_service_info(self, request_body: dict) -> Self:
        """CreateServiceInfo operation.

        Args:
            request_body (dict): requestBody parameter
        """
        qry = ServiceOperationQuery(self, "CreateServiceInfo", None, {"requestBody": request_body}, None)
        self.context.add_query(qry)
        return self

    @property
    def addressbar_link_permission(self) -> Optional[int]:
        """Gets the AddressbarLinkPermission property"""
        return self.properties.get("AddressbarLinkPermission", None)

    @property
    def ai_builder_default_power_apps_environment(self) -> Optional[str]:
        """Gets the AIBuilderDefaultPowerAppsEnvironment property"""
        return self.properties.get("AIBuilderDefaultPowerAppsEnvironment", None)

    @property
    def ai_builder_enabled_in_content_center(self) -> Optional[int]:
        """Gets the AIBuilderEnabledInContentCenter property"""
        return self.properties.get("AIBuilderEnabledInContentCenter", None)

    @property
    def ai_builder_site_list(self) -> GuidCollection:
        """Gets the AIBuilderSiteList property"""
        return self.properties.get("AIBuilderSiteList", GuidCollection())

    @property
    def ai_builder_site_list_file_name(self) -> Optional[str]:
        """Gets the AIBuilderSiteListFileName property"""
        return self.properties.get("AIBuilderSiteListFileName", None)

    @property
    def all_organization_security_group_id(self) -> Optional[UUID]:
        """Gets the AllOrganizationSecurityGroupId property"""
        return self.properties.get("AllOrganizationSecurityGroupId", None)

    @property
    def allow_anonymous_meeting_participants_to_access_whiteboards(self) -> Optional[int]:
        """Gets the AllowAnonymousMeetingParticipantsToAccessWhiteboards property"""
        return self.properties.get("AllowAnonymousMeetingParticipantsToAccessWhiteboards", None)

    @property
    def allow_apps_bypass_of_unmanaged_device_policy(self) -> Optional[bool]:
        """Gets the AllowAppsBypassOfUnmanagedDevicePolicy property"""
        return self.properties.get("AllowAppsBypassOfUnmanagedDevicePolicy", None)

    @property
    def allow_classic_publishing_site_creation(self) -> Optional[bool]:
        """Gets the AllowClassicPublishingSiteCreation property"""
        return self.properties.get("AllowClassicPublishingSiteCreation", None)

    @property
    def allow_downloading_non_web_viewable_files(self) -> Optional[bool]:
        """Gets the AllowDownloadingNonWebViewableFiles property"""
        return self.properties.get("AllowDownloadingNonWebViewableFiles", None)

    @property
    def allowed_domain_list_for_sync_client(self) -> GuidCollection:
        """Gets the AllowedDomainListForSyncClient property"""
        return self.properties.get("AllowedDomainListForSyncClient", GuidCollection())

    @property
    def allow_file_archive(self) -> Optional[bool]:
        """Gets the AllowFileArchive property"""
        return self.properties.get("AllowFileArchive", None)

    @property
    def allow_file_archive_on_new_sites_by_default(self) -> Optional[bool]:
        """Gets the AllowFileArchiveOnNewSitesByDefault property"""
        return self.properties.get("AllowFileArchiveOnNewSitesByDefault", None)

    @property
    def allow_guest_user_share_to_users_not_in_site_collection(self) -> Optional[bool]:
        """Gets the AllowGuestUserShareToUsersNotInSiteCollection property"""
        return self.properties.get("AllowGuestUserShareToUsersNotInSiteCollection", None)

    @property
    def allow_legacy_auth_protocols_enabled_setting(self) -> Optional[bool]:
        """Gets the AllowLegacyAuthProtocolsEnabledSetting property"""
        return self.properties.get("AllowLegacyAuthProtocolsEnabledSetting", None)

    @property
    def allow_legacy_browser_auth_protocols_enabled_setting(self) -> Optional[bool]:
        """Gets the AllowLegacyBrowserAuthProtocolsEnabledSetting property"""
        return self.properties.get("AllowLegacyBrowserAuthProtocolsEnabledSetting", None)

    @property
    def allow_limited_access_on_unmanaged_devices(self) -> Optional[bool]:
        """Gets the AllowLimitedAccessOnUnmanagedDevices property"""
        return self.properties.get("AllowLimitedAccessOnUnmanagedDevices", None)

    @property
    def allow_override_for_block_user_info_visibility(self) -> Optional[bool]:
        """Gets the AllowOverrideForBlockUserInfoVisibility property"""
        return self.properties.get("AllowOverrideForBlockUserInfoVisibility", None)

    @property
    def allow_select_security_groups_in_sp_sites_list(self) -> StringCollection:
        """Gets the AllowSelectSecurityGroupsInSPSitesList property"""
        return self.properties.get("AllowSelectSecurityGroupsInSPSitesList", StringCollection())

    @property
    def allow_select_sgs_in_odb_list_in_tenant(self) -> StringCollection:
        """Gets the AllowSelectSGsInODBListInTenant property"""
        return self.properties.get("AllowSelectSGsInODBListInTenant", StringCollection())

    @property
    def allow_sensitivity_label_on_records(self) -> Optional[bool]:
        """Gets the AllowSensitivityLabelOnRecords property"""
        return self.properties.get("AllowSensitivityLabelOnRecords", None)

    @property
    def allow_sharing_outside_restricted_access_control_groups(self) -> Optional[bool]:
        """Gets the AllowSharingOutsideRestrictedAccessControlGroups property"""
        return self.properties.get("AllowSharingOutsideRestrictedAccessControlGroups", None)

    @property
    def allow_web_property_bag_update_when_deny_add_and_customize_pages_is_enabled(self) -> Optional[bool]:
        """Gets the AllowWebPropertyBagUpdateWhenDenyAddAndCustomizePagesIsEnabled property"""
        return self.properties.get("AllowWebPropertyBagUpdateWhenDenyAddAndCustomizePagesIsEnabled", None)

    @property
    def amplify_admin_settings(self) -> Optional[str]:
        """Gets the AmplifyAdminSettings property"""
        return self.properties.get("AmplifyAdminSettings", None)

    @property
    def anyone_link_track_users(self) -> Optional[bool]:
        """Gets the AnyoneLinkTrackUsers property"""
        return self.properties.get("AnyoneLinkTrackUsers", None)

    @property
    def app_access_information_barriers_allow_list(self) -> GuidCollection:
        """Gets the AppAccessInformationBarriersAllowList property"""
        return self.properties.get("AppAccessInformationBarriersAllowList", GuidCollection())

    @property
    def app_bypass_information_barriers(self) -> Optional[bool]:
        """Gets the AppBypassInformationBarriers property"""
        return self.properties.get("AppBypassInformationBarriers", None)

    @property
    def apply_app_enforced_restrictions_to_ad_hoc_recipients(self) -> Optional[bool]:
        """Gets the ApplyAppEnforcedRestrictionsToAdHocRecipients property"""
        return self.properties.get("ApplyAppEnforcedRestrictionsToAdHocRecipients", None)

    @property
    def app_only_bypass_people_picker_policies(self) -> Optional[bool]:
        """Gets the AppOnlyBypassPeoplePickerPolicies property"""
        return self.properties.get("AppOnlyBypassPeoplePickerPolicies", None)

    @property
    def archived_file_storage_usage_mb(self) -> Optional[int]:
        """Gets the ArchivedFileStorageUsageMB property"""
        return self.properties.get("ArchivedFileStorageUsageMB", None)

    @property
    def archive_redirect_url(self) -> Optional[str]:
        """Gets the ArchiveRedirectUrl property"""
        return self.properties.get("ArchiveRedirectUrl", None)

    @property
    def auth_context_resilience_mode(self) -> Optional[int]:
        """Gets the AuthContextResilienceMode property"""
        return self.properties.get("AuthContextResilienceMode", None)

    @property
    def autofill_columns_custom_model_enabled(self) -> Optional[bool]:
        """Gets the AutofillColumnsCustomModelEnabled property"""
        return self.properties.get("AutofillColumnsCustomModelEnabled", None)

    @property
    def autofill_columns_custom_model_settings(self) -> ClientValueCollection[SyntexCustomModelSetting]:
        """Gets the AutofillColumnsCustomModelSettings property"""
        from office365.sharepoint.viva.syntexcustommodelsetting import (
            SyntexCustomModelSetting,
        )

        return self.properties.get(
            "AutofillColumnsCustomModelSettings",
            ClientValueCollection[SyntexCustomModelSetting](SyntexCustomModelSetting),
        )

    @property
    def autofill_columns_enabled(self) -> Optional[bool]:
        """Gets the AutofillColumnsEnabled property"""
        return self.properties.get("AutofillColumnsEnabled", None)

    @property
    def autofill_columns_site_info_list(self) -> ClientValueCollection[SiteInfoForSitePicker]:
        """Gets the AutofillColumnsSiteInfoList property"""
        from office365.sharepoint.tenant.administration.siteinfo_for_site_picker import (
            SiteInfoForSitePicker,
        )

        return self.properties.get(
            "AutofillColumnsSiteInfoList", ClientValueCollection[SiteInfoForSitePicker](SiteInfoForSitePicker)
        )

    @property
    def autofill_columns_site_list(self) -> GuidCollection:
        """Gets the AutofillColumnsSiteList property"""
        return self.properties.get("AutofillColumnsSiteList", GuidCollection())

    @property
    def autofill_columns_site_list_file_name(self) -> Optional[str]:
        """Gets the AutofillColumnsSiteListFileName property"""
        return self.properties.get("AutofillColumnsSiteListFileName", None)

    @property
    def baseline_security_mode_third_party_app_hpa(self) -> BaselineSecurityModeThirdPartyAppHPASetting:
        """Gets the BaselineSecurityModeThirdPartyAppHPA property"""
        from office365.sharepoint.authpolicy.baseline_security_mode_third_party_app_hpa_setting import (
            BaselineSecurityModeThirdPartyAppHPASetting,
        )

        return self.properties.get("BaselineSecurityModeThirdPartyAppHPA", BaselineSecurityModeThirdPartyAppHPASetting())

    @property
    def bcc_external_sharing_invitations(self) -> Optional[bool]:
        """Gets the BccExternalSharingInvitations property"""
        return self.properties.get("BccExternalSharingInvitations", None)

    @property
    def bcc_external_sharing_invitations_list(self) -> Optional[str]:
        """Gets the BccExternalSharingInvitationsList property"""
        return self.properties.get("BccExternalSharingInvitationsList", None)

    @property
    def block_access_on_unmanaged_devices(self) -> Optional[bool]:
        """Gets the BlockAccessOnUnmanagedDevices property"""
        return self.properties.get("BlockAccessOnUnmanagedDevices", None)

    @property
    def block_app_access_with_authentication_context(self) -> Optional[bool]:
        """Gets the BlockAppAccessWithAuthenticationContext property"""
        return self.properties.get("BlockAppAccessWithAuthenticationContext", None)

    @property
    def block_download_file_type_ids(self) -> ClientValueCollection:
        """Gets the BlockDownloadFileTypeIds property"""
        return self.properties.get("BlockDownloadFileTypeIds", ClientValueCollection(int))

    @property
    def block_download_file_type_policy(self) -> Optional[bool]:
        """Gets the BlockDownloadFileTypePolicy property"""
        return self.properties.get("BlockDownloadFileTypePolicy", None)

    @property
    def block_download_links_file_type(self) -> Optional[int]:
        """Gets the BlockDownloadLinksFileType property"""
        return self.properties.get("BlockDownloadLinksFileType", None)

    @property
    def block_download_of_all_files_for_guests(self) -> Optional[bool]:
        """Gets the BlockDownloadOfAllFilesForGuests property"""
        return self.properties.get("BlockDownloadOfAllFilesForGuests", None)

    @property
    def block_download_of_all_files_on_unmanaged_devices(self) -> Optional[bool]:
        """Gets the BlockDownloadOfAllFilesOnUnmanagedDevices property"""
        return self.properties.get("BlockDownloadOfAllFilesOnUnmanagedDevices", None)

    @property
    def block_download_of_viewable_files_for_guests(self) -> Optional[bool]:
        """Gets the BlockDownloadOfViewableFilesForGuests property"""
        return self.properties.get("BlockDownloadOfViewableFilesForGuests", None)

    @property
    def block_download_of_viewable_files_on_unmanaged_devices(self) -> Optional[bool]:
        """Gets the BlockDownloadOfViewableFilesOnUnmanagedDevices property"""
        return self.properties.get("BlockDownloadOfViewableFilesOnUnmanagedDevices", None)

    @property
    def block_mac_sync(self) -> Optional[bool]:
        """Gets the BlockMacSync property"""
        return self.properties.get("BlockMacSync", None)

    @property
    def block_send_label_mismatch_email(self) -> Optional[bool]:
        """Gets the BlockSendLabelMismatchEmail property"""
        return self.properties.get("BlockSendLabelMismatchEmail", None)

    @property
    def block_user_info_visibility(self) -> Optional[str]:
        """Gets the BlockUserInfoVisibility property"""
        return self.properties.get("BlockUserInfoVisibility", None)

    @property
    def block_user_info_visibility_in_onedrive(self) -> Optional[int]:
        """Gets the BlockUserInfoVisibilityInOneDrive property"""
        return self.properties.get("BlockUserInfoVisibilityInOneDrive", None)

    @property
    def block_user_info_visibility_in_sharepoint(self) -> Optional[int]:
        """Gets the BlockUserInfoVisibilityInSharePoint property"""
        return self.properties.get("BlockUserInfoVisibilityInSharePoint", None)

    @property
    def bonus_storage_quota_mb(self) -> Optional[int]:
        """Gets the BonusStorageQuotaMB property"""
        return self.properties.get("BonusStorageQuotaMB", None)

    @property
    def business_connectivity_service_disabled(self) -> Optional[bool]:
        """Gets the BusinessConnectivityServiceDisabled property"""
        return self.properties.get("BusinessConnectivityServiceDisabled", None)

    @property
    def classic_pages_restrict_mode(self) -> Optional[bool]:
        """Gets the ClassicPagesRestrictMode property"""
        return self.properties.get("ClassicPagesRestrictMode", None)

    @property
    def comments_on_files_disabled(self) -> Optional[bool]:
        """Gets the CommentsOnFilesDisabled property"""
        return self.properties.get("CommentsOnFilesDisabled", None)

    @property
    def comments_on_list_items_disabled(self) -> Optional[bool]:
        """Gets the CommentsOnListItemsDisabled property"""
        return self.properties.get("CommentsOnListItemsDisabled", None)

    @property
    def comments_on_site_pages_disabled(self) -> Optional[bool]:
        """Gets the CommentsOnSitePagesDisabled property"""
        return self.properties.get("CommentsOnSitePagesDisabled", None)

    @property
    def compatibility_range(self) -> Optional[str]:
        """Gets the CompatibilityRange property"""
        return self.properties.get("CompatibilityRange", None)

    @property
    def conditional_access_policy(self) -> Optional[int]:
        """Gets the ConditionalAccessPolicy property"""
        return self.properties.get("ConditionalAccessPolicy", None)

    @property
    def conditional_access_policy_error_help_link(self) -> Optional[str]:
        """Gets the ConditionalAccessPolicyErrorHelpLink property"""
        return self.properties.get("ConditionalAccessPolicyErrorHelpLink", None)

    @property
    def content_security_policy_config_synced(self) -> Optional[bool]:
        """Gets the ContentSecurityPolicyConfigSynced property"""
        return self.properties.get("ContentSecurityPolicyConfigSynced", None)

    @property
    def content_security_policy_enforcement(self) -> Optional[bool]:
        """Gets the ContentSecurityPolicyEnforcement property"""
        return self.properties.get("ContentSecurityPolicyEnforcement", None)

    @property
    def content_type_sync_site_templates_list(self) -> StringCollection:
        """Gets the ContentTypeSyncSiteTemplatesList property"""
        return self.properties.get("ContentTypeSyncSiteTemplatesList", StringCollection())

    @property
    def copilot_search_opt_in(self) -> Optional[bool]:
        """Gets the CopilotSearchOptIn property"""
        return self.properties.get("CopilotSearchOptIn", None)

    @property
    def core_anyone_sharing_link_max_expiration_in_days(self) -> Optional[int]:
        """Gets the CoreAnyoneSharingLinkMaxExpirationInDays property"""
        return self.properties.get("CoreAnyoneSharingLinkMaxExpirationInDays", None)

    @property
    def core_anyone_sharing_link_recommended_expiration_in_days(self) -> Optional[int]:
        """Gets the CoreAnyoneSharingLinkRecommendedExpirationInDays property"""
        return self.properties.get("CoreAnyoneSharingLinkRecommendedExpirationInDays", None)

    @property
    def core_block_guests_as_site_admin(self) -> Optional[int]:
        """Gets the CoreBlockGuestsAsSiteAdmin property"""
        return self.properties.get("CoreBlockGuestsAsSiteAdmin", None)

    @property
    def core_default_link_to_existing_access(self) -> Optional[bool]:
        """Gets the CoreDefaultLinkToExistingAccess property"""
        return self.properties.get("CoreDefaultLinkToExistingAccess", None)

    @property
    def core_default_share_link_role(self) -> Optional[int]:
        """Gets the CoreDefaultShareLinkRole property"""
        return self.properties.get("CoreDefaultShareLinkRole", None)

    @property
    def core_default_share_link_scope(self) -> Optional[int]:
        """Gets the CoreDefaultShareLinkScope property"""
        return self.properties.get("CoreDefaultShareLinkScope", None)

    @property
    def core_loop_default_sharing_link_role(self) -> Optional[int]:
        """Gets the CoreLoopDefaultSharingLinkRole property"""
        return self.properties.get("CoreLoopDefaultSharingLinkRole", None)

    @property
    def core_loop_default_sharing_link_scope(self) -> Optional[int]:
        """Gets the CoreLoopDefaultSharingLinkScope property"""
        return self.properties.get("CoreLoopDefaultSharingLinkScope", None)

    @property
    def core_loop_sharing_capability(self) -> Optional[int]:
        """Gets the CoreLoopSharingCapability property"""
        return self.properties.get("CoreLoopSharingCapability", None)

    @property
    def core_organization_sharing_link_max_expiration_in_days(self) -> Optional[int]:
        """Gets the CoreOrganizationSharingLinkMaxExpirationInDays property"""
        return self.properties.get("CoreOrganizationSharingLinkMaxExpirationInDays", None)

    @property
    def core_organization_sharing_link_recommended_expiration_in_days(self) -> Optional[int]:
        """Gets the CoreOrganizationSharingLinkRecommendedExpirationInDays property"""
        return self.properties.get("CoreOrganizationSharingLinkRecommendedExpirationInDays", None)

    @property
    def core_request_files_link_enabled(self) -> Optional[bool]:
        """Gets the CoreRequestFilesLinkEnabled property"""
        return self.properties.get("CoreRequestFilesLinkEnabled", None)

    @property
    def core_request_files_link_expiration_in_days(self) -> Optional[int]:
        """Gets the CoreRequestFilesLinkExpirationInDays property"""
        return self.properties.get("CoreRequestFilesLinkExpirationInDays", None)

    @property
    def core_sharing_capability(self) -> Optional[int]:
        """Gets the CoreSharingCapability property"""
        return self.properties.get("CoreSharingCapability", None)

    @property
    def customized_external_sharing_service_url(self) -> Optional[str]:
        """Gets the CustomizedExternalSharingServiceUrl property"""
        return self.properties.get("CustomizedExternalSharingServiceUrl", None)

    @property
    def custom_scripts_restrict_mode(self) -> Optional[bool]:
        """Gets the CustomScriptsRestrictMode property"""
        return self.properties.get("CustomScriptsRestrictMode", None)

    @property
    def dataverse_usage_consent_enabled(self) -> Optional[bool]:
        """Gets the DataverseUsageConsentEnabled property"""
        return self.properties.get("DataverseUsageConsentEnabled", None)

    @property
    def default_language_for_site_creation(self) -> Optional[str]:
        """Gets the DefaultLanguageForSiteCreation property"""
        return self.properties.get("DefaultLanguageForSiteCreation", None)

    @property
    def default_link_permission(self) -> Optional[int]:
        """Gets the DefaultLinkPermission property"""
        return self.properties.get("DefaultLinkPermission", None)

    @property
    def default_odb_mode(self) -> Optional[str]:
        """Gets the DefaultODBMode property"""
        return self.properties.get("DefaultODBMode", None)

    @property
    def default_sharing_link_type(self) -> Optional[int]:
        """Gets the DefaultSharingLinkType property"""
        return self.properties.get("DefaultSharingLinkType", None)

    @property
    def delay_content_security_policy_enforcement(self) -> Optional[bool]:
        """Gets the DelayContentSecurityPolicyEnforcement property"""
        return self.properties.get("DelayContentSecurityPolicyEnforcement", None)

    @property
    def delay_deny_add_and_customize_pages_enforcement(self) -> Optional[bool]:
        """Gets the DelayDenyAddAndCustomizePagesEnforcement property"""
        return self.properties.get("DelayDenyAddAndCustomizePagesEnforcement", None)

    @property
    def delay_deny_add_and_customize_pages_enforcement_on_classic_publishing_sites(self) -> Optional[bool]:
        """Gets the DelayDenyAddAndCustomizePagesEnforcementOnClassicPublishingSites property"""
        return self.properties.get("DelayDenyAddAndCustomizePagesEnforcementOnClassicPublishingSites", None)

    @property
    def delegate_restricted_access_control_configuration(self) -> Optional[bool]:
        """Gets the DelegateRestrictedAccessControlConfiguration property"""
        return self.properties.get("DelegateRestrictedAccessControlConfiguration", None)

    @property
    def delegate_restricted_content_discovery_configuration(self) -> Optional[bool]:
        """Gets the DelegateRestrictedContentDiscoveryConfiguration property"""
        return self.properties.get("DelegateRestrictedContentDiscoveryConfiguration", None)

    @property
    def deny_select_security_groups_in_sp_sites_list(self) -> StringCollection:
        """Gets the DenySelectSecurityGroupsInSPSitesList property"""
        return self.properties.get("DenySelectSecurityGroupsInSPSitesList", StringCollection())

    @property
    def deny_select_sgs_in_odb_list_in_tenant(self) -> StringCollection:
        """Gets the DenySelectSGsInODBListInTenant property"""
        return self.properties.get("DenySelectSGsInODBListInTenant", StringCollection())

    @property
    def disable_add_to_onedrive(self) -> Optional[bool]:
        """Gets the DisableAddToOneDrive property"""
        return self.properties.get("DisableAddToOneDrive", None)

    @property
    def disable_back_to_classic(self) -> Optional[bool]:
        """Gets the DisableBackToClassic property"""
        return self.properties.get("DisableBackToClassic", None)

    @property
    def disable_custom_app_authentication(self) -> Optional[bool]:
        """Gets the DisableCustomAppAuthentication property"""
        return self.properties.get("DisableCustomAppAuthentication", None)

    @property
    def disabled_adaptive_card_extension_ids(self) -> GuidCollection:
        """Gets the DisabledAdaptiveCardExtensionIds property"""
        return self.properties.get("DisabledAdaptiveCardExtensionIds", GuidCollection())

    @property
    def disabled_modern_list_template_ids(self) -> GuidCollection:
        """Gets the DisabledModernListTemplateIds property"""
        return self.properties.get("DisabledModernListTemplateIds", GuidCollection())

    @property
    def disable_document_library_default_labeling(self) -> Optional[bool]:
        """Gets the DisableDocumentLibraryDefaultLabeling property"""
        return self.properties.get("DisableDocumentLibraryDefaultLabeling", None)

    @property
    def disabled_web_part_ids(self) -> GuidCollection:
        """Gets the DisabledWebPartIds property"""
        return self.properties.get("DisabledWebPartIds", GuidCollection())

    @property
    def disable_outlook_pst_version_trimming(self) -> Optional[bool]:
        """Gets the DisableOutlookPSTVersionTrimming property"""
        return self.properties.get("DisableOutlookPSTVersionTrimming", None)

    @property
    def disable_personal_list_creation(self) -> Optional[bool]:
        """Gets the DisablePersonalListCreation property"""
        return self.properties.get("DisablePersonalListCreation", None)

    @property
    def disable_report_problem_dialog(self) -> Optional[bool]:
        """Gets the DisableReportProblemDialog property"""
        return self.properties.get("DisableReportProblemDialog", None)

    @property
    def disable_sharepoint_store_access(self) -> Optional[bool]:
        """Gets the DisableSharePointStoreAccess property"""
        return self.properties.get("DisableSharePointStoreAccess", None)

    @property
    def disable_spaces_activation(self) -> Optional[bool]:
        """Gets the DisableSpacesActivation property"""
        return self.properties.get("DisableSpacesActivation", None)

    @property
    def disable_spfx_top_bottom_placeholders_in_elevated_content(self) -> Optional[bool]:
        """Gets the DisableSpfxTopBottomPlaceholdersInElevatedContent property"""
        return self.properties.get("DisableSpfxTopBottomPlaceholdersInElevatedContent", None)

    @property
    def disable_teams_meeting_recording_deleted_notification(self) -> Optional[bool]:
        """Gets the DisableTeamsMeetingRecordingDeletedNotification property"""
        return self.properties.get("DisableTeamsMeetingRecordingDeletedNotification", None)

    @property
    def disable_viva_connections_analytics(self) -> Optional[bool]:
        """Gets the DisableVivaConnectionsAnalytics property"""
        return self.properties.get("DisableVivaConnectionsAnalytics", None)

    @property
    def disallow_infected_file_download(self) -> Optional[bool]:
        """Gets the DisallowInfectedFileDownload property"""
        return self.properties.get("DisallowInfectedFileDownload", None)

    @property
    def display_names_of_file_viewers(self) -> Optional[bool]:
        """Gets the DisplayNamesOfFileViewers property"""
        return self.properties.get("DisplayNamesOfFileViewers", None)

    @property
    def display_names_of_file_viewers_in_spo(self) -> Optional[bool]:
        """Gets the DisplayNamesOfFileViewersInSpo property"""
        return self.properties.get("DisplayNamesOfFileViewersInSpo", None)

    @property
    def display_start_a_site_option(self) -> Optional[bool]:
        """Gets the DisplayStartASiteOption property"""
        return self.properties.get("DisplayStartASiteOption", None)

    @property
    def document_understanding_enabled(self) -> Optional[bool]:
        """Gets the DocumentUnderstandingEnabled property"""
        return self.properties.get("DocumentUnderstandingEnabled", None)

    @property
    def document_understanding_enabled_in_content_center(self) -> Optional[int]:
        """Gets the DocumentUnderstandingEnabledInContentCenter property"""
        return self.properties.get("DocumentUnderstandingEnabledInContentCenter", None)

    @property
    def document_understanding_site_info_list(self) -> ClientValueCollection[SiteInfoForSitePicker]:
        """Gets the DocumentUnderstandingSiteInfoList property"""
        from office365.sharepoint.tenant.administration.siteinfo_for_site_picker import (
            SiteInfoForSitePicker,
        )

        return self.properties.get(
            "DocumentUnderstandingSiteInfoList", ClientValueCollection[SiteInfoForSitePicker](SiteInfoForSitePicker)
        )

    @property
    def document_understanding_site_list(self) -> GuidCollection:
        """Gets the DocumentUnderstandingSiteList property"""
        return self.properties.get("DocumentUnderstandingSiteList", GuidCollection())

    @property
    def document_understanding_site_list_file_name(self) -> Optional[str]:
        """Gets the DocumentUnderstandingSiteListFileName property"""
        return self.properties.get("DocumentUnderstandingSiteListFileName", None)

    @property
    def email_attestation_enabled(self) -> Optional[bool]:
        """Gets the EmailAttestationEnabled property"""
        return self.properties.get("EmailAttestationEnabled", None)

    @property
    def email_attestation_re_auth_days(self) -> Optional[int]:
        """Gets the EmailAttestationReAuthDays property"""
        return self.properties.get("EmailAttestationReAuthDays", None)

    @property
    def email_attestation_required(self) -> Optional[bool]:
        """Gets the EmailAttestationRequired property"""
        return self.properties.get("EmailAttestationRequired", None)

    @property
    def enable_agent_worker_sharing_disclaimer(self) -> Optional[bool]:
        """Gets the EnableAgentWorkerSharingDisclaimer property"""
        return self.properties.get("EnableAgentWorkerSharingDisclaimer", None)

    @property
    def enable_aip_integration(self) -> Optional[bool]:
        """Gets the EnableAIPIntegration property"""
        return self.properties.get("EnableAIPIntegration", None)

    @property
    def enable_auto_expiration_version_trim(self) -> Optional[bool]:
        """Gets the EnableAutoExpirationVersionTrim property"""
        return self.properties.get("EnableAutoExpirationVersionTrim", None)

    @property
    def enable_auto_news_digest(self) -> Optional[bool]:
        """Gets the EnableAutoNewsDigest property"""
        return self.properties.get("EnableAutoNewsDigest", None)

    @property
    def enable_azure_adb2_b_integration(self) -> Optional[bool]:
        """Gets the EnableAzureADB2BIntegration property"""
        return self.properties.get("EnableAzureADB2BIntegration", None)

    @property
    def enabled_flight_allow_aadb2_b_skip_checking_otp(self) -> Optional[bool]:
        """Gets the EnabledFlightAllowAADB2BSkipCheckingOTP property"""
        return self.properties.get("EnabledFlightAllowAADB2BSkipCheckingOTP", None)

    @property
    def enable_direct_to_customer_billing(self) -> Optional[bool]:
        """Gets the EnableDirectToCustomerBilling property"""
        return self.properties.get("EnableDirectToCustomerBilling", None)

    @property
    def enable_discoverable_by_organization_for_videos(self) -> Optional[bool]:
        """Gets the EnableDiscoverableByOrganizationForVideos property"""
        return self.properties.get("EnableDiscoverableByOrganizationForVideos", None)

    @property
    def enable_guest_sign_in_acceleration(self) -> Optional[bool]:
        """Gets the EnableGuestSignInAcceleration property"""
        return self.properties.get("EnableGuestSignInAcceleration", None)

    @property
    def enable_media_reactions(self) -> Optional[bool]:
        """Gets the EnableMediaReactions property"""
        return self.properties.get("EnableMediaReactions", None)

    @property
    def enable_minimum_version_requirement(self) -> Optional[bool]:
        """Gets the EnableMinimumVersionRequirement property"""
        return self.properties.get("EnableMinimumVersionRequirement", None)

    @property
    def enable_mip_site_label(self) -> Optional[bool]:
        """Gets the EnableMipSiteLabel property"""
        return self.properties.get("EnableMipSiteLabel", None)

    @property
    def enable_notifications_subscriptions(self) -> Optional[bool]:
        """Gets the EnableNotificationsSubscriptions property"""
        return self.properties.get("EnableNotificationsSubscriptions", None)

    @property
    def enable_promoted_file_handlers(self) -> Optional[bool]:
        """Gets the EnablePromotedFileHandlers property"""
        return self.properties.get("EnablePromotedFileHandlers", None)

    @property
    def enable_restricted_access_control(self) -> Optional[bool]:
        """Gets the EnableRestrictedAccessControl property"""
        return self.properties.get("EnableRestrictedAccessControl", None)

    @property
    def enable_sensitivity_label_for_onenote(self) -> Optional[bool]:
        """Gets the EnableSensitivityLabelForOneNote property"""
        return self.properties.get("EnableSensitivityLabelForOneNote", None)

    @property
    def enable_sensitivity_label_for_pdf(self) -> Optional[bool]:
        """Gets the EnableSensitivityLabelForPDF property"""
        return self.properties.get("EnableSensitivityLabelForPDF", None)

    @property
    def enable_sensitivity_label_for_video_files(self) -> Optional[bool]:
        """Gets the EnableSensitivityLabelForVideoFiles property"""
        return self.properties.get("EnableSensitivityLabelForVideoFiles", None)

    @property
    def enable_site_archive(self) -> Optional[bool]:
        """Gets the EnableSiteArchive property"""
        return self.properties.get("EnableSiteArchive", None)

    @property
    def enable_tenant_restrictions_insights(self) -> Optional[bool]:
        """Gets the EnableTenantRestrictionsInsights property"""
        return self.properties.get("EnableTenantRestrictionsInsights", None)

    @property
    def enforce_request_digest(self) -> Optional[bool]:
        """Gets the EnforceRequestDigest property"""
        return self.properties.get("EnforceRequestDigest", None)

    @property
    def e_signature_app_list(self) -> StringCollection:
        """Gets the ESignatureAppList property"""
        return self.properties.get("ESignatureAppList", StringCollection())

    @property
    def e_signature_enabled(self) -> Optional[bool]:
        """Gets the ESignatureEnabled property"""
        return self.properties.get("ESignatureEnabled", None)

    @property
    def e_signature_site_info_list(self) -> ClientValueCollection[SiteInfoForSitePicker]:
        """Gets the ESignatureSiteInfoList property"""
        from office365.sharepoint.tenant.administration.siteinfo_for_site_picker import (
            SiteInfoForSitePicker,
        )

        return self.properties.get(
            "ESignatureSiteInfoList", ClientValueCollection[SiteInfoForSitePicker](SiteInfoForSitePicker)
        )

    @property
    def e_signature_site_list(self) -> GuidCollection:
        """Gets the ESignatureSiteList property"""
        return self.properties.get("ESignatureSiteList", GuidCollection())

    @property
    def e_signature_site_list_file_name(self) -> Optional[str]:
        """Gets the ESignatureSiteListFileName property"""
        return self.properties.get("ESignatureSiteListFileName", None)

    @property
    def e_signature_third_party_provider_info_list(self) -> StringCollection:
        """Gets the ESignatureThirdPartyProviderInfoList property"""
        return self.properties.get("ESignatureThirdPartyProviderInfoList", StringCollection())

    @property
    def e_signature_third_party_provider_list(self) -> StringCollection:
        """Gets the ESignatureThirdPartyProviderList property"""
        return self.properties.get("ESignatureThirdPartyProviderList", StringCollection())

    @property
    def e_signature_third_party_provider_list_file_name(self) -> Optional[str]:
        """Gets the ESignatureThirdPartyProviderListFileName property"""
        return self.properties.get("ESignatureThirdPartyProviderListFileName", None)

    @property
    def excluded_block_download_group_ids(self) -> GuidCollection:
        """Gets the ExcludedBlockDownloadGroupIds property"""
        return self.properties.get("ExcludedBlockDownloadGroupIds", GuidCollection())

    @property
    def excluded_file_extensions_for_sync_client(self) -> StringCollection:
        """Gets the ExcludedFileExtensionsForSyncClient property"""
        return self.properties.get("ExcludedFileExtensionsForSyncClient", StringCollection())

    @property
    def exempt_native_users_from_tenant_level_restriced_access_control(self) -> Optional[bool]:
        """Gets the ExemptNativeUsersFromTenantLevelRestricedAccessControl property"""
        return self.properties.get("ExemptNativeUsersFromTenantLevelRestricedAccessControl", None)

    @property
    def expire_versions_after_days(self) -> Optional[int]:
        """Gets the ExpireVersionsAfterDays property"""
        return self.properties.get("ExpireVersionsAfterDays", None)

    @property
    def extend_permissions_to_unprotected_files(self) -> Optional[bool]:
        """Gets the ExtendPermissionsToUnprotectedFiles property"""
        return self.properties.get("ExtendPermissionsToUnprotectedFiles", None)

    @property
    def external_services_enabled(self) -> Optional[bool]:
        """Gets the ExternalServicesEnabled property"""
        return self.properties.get("ExternalServicesEnabled", None)

    @property
    def external_user_expiration_required(self) -> Optional[bool]:
        """Gets the ExternalUserExpirationRequired property"""
        return self.properties.get("ExternalUserExpirationRequired", None)

    @property
    def external_user_expire_in_days(self) -> Optional[int]:
        """Gets the ExternalUserExpireInDays property"""
        return self.properties.get("ExternalUserExpireInDays", None)

    @property
    def file_anonymous_link_type(self) -> Optional[int]:
        """Gets the FileAnonymousLinkType property"""
        return self.properties.get("FileAnonymousLinkType", None)

    @property
    def file_picker_external_image_search_enabled(self) -> Optional[bool]:
        """Gets the FilePickerExternalImageSearchEnabled property"""
        return self.properties.get("FilePickerExternalImageSearchEnabled", None)

    @property
    def file_preview_allowed_domain_list(self) -> Optional[str]:
        """Gets the FilePreviewAllowedDomainList property"""
        return self.properties.get("FilePreviewAllowedDomainList", None)

    @property
    def folder_anonymous_link_type(self) -> Optional[int]:
        """Gets the FolderAnonymousLinkType property"""
        return self.properties.get("FolderAnonymousLinkType", None)

    @property
    def guest_sharing_group_allow_list_in_tenant(self) -> Optional[str]:
        """Gets the GuestSharingGroupAllowListInTenant property"""
        return self.properties.get("GuestSharingGroupAllowListInTenant", None)

    @property
    def guest_sharing_group_allow_list_in_tenant_by_group_id(self) -> StringCollection:
        """Gets the GuestSharingGroupAllowListInTenantByGroupId property"""
        return self.properties.get("GuestSharingGroupAllowListInTenantByGroupId", StringCollection())

    @property
    def guest_sharing_group_allow_list_in_tenant_by_principal_identity(self) -> StringCollection:
        """Gets the GuestSharingGroupAllowListInTenantByPrincipalIdentity property"""
        return self.properties.get("GuestSharingGroupAllowListInTenantByPrincipalIdentity", StringCollection())

    @property
    def hard_deprecation_rps_enabled(self) -> Optional[bool]:
        """Gets the HardDeprecationRPSEnabled property"""
        return self.properties.get("HardDeprecationRPSEnabled", None)

    @property
    def has_admin_completed_cu_configuration(self) -> Optional[bool]:
        """Gets the HasAdminCompletedCUConfiguration property"""
        return self.properties.get("HasAdminCompletedCUConfiguration", None)

    @property
    def has_intelligent_content_services_capability(self) -> Optional[bool]:
        """Gets the HasIntelligentContentServicesCapability property"""
        return self.properties.get("HasIntelligentContentServicesCapability", None)

    @property
    def has_topic_experiences_capability(self) -> Optional[bool]:
        """Gets the HasTopicExperiencesCapability property"""
        return self.properties.get("HasTopicExperiencesCapability", None)

    @property
    def hide_default_themes(self) -> Optional[bool]:
        """Gets the HideDefaultThemes property"""
        return self.properties.get("HideDefaultThemes", None)

    @property
    def hide_sync_button_on_doc_lib(self) -> Optional[bool]:
        """Gets the HideSyncButtonOnDocLib property"""
        return self.properties.get("HideSyncButtonOnDocLib", None)

    @property
    def hide_sync_button_on_odb(self) -> Optional[bool]:
        """Gets the HideSyncButtonOnODB property"""
        return self.properties.get("HideSyncButtonOnODB", None)

    @property
    def ib_implicit_group_based(self) -> Optional[bool]:
        """Gets the IBImplicitGroupBased property"""
        return self.properties.get("IBImplicitGroupBased", None)

    @property
    def image_tagging_option(self) -> Optional[int]:
        """Gets the ImageTaggingOption property"""
        return self.properties.get("ImageTaggingOption", None)

    @property
    def image_tagging_site_info_list(self) -> ClientValueCollection[SiteInfoForSitePicker]:
        """Gets the ImageTaggingSiteInfoList property"""
        from office365.sharepoint.tenant.administration.siteinfo_for_site_picker import (
            SiteInfoForSitePicker,
        )

        return self.properties.get(
            "ImageTaggingSiteInfoList", ClientValueCollection[SiteInfoForSitePicker](SiteInfoForSitePicker)
        )

    @property
    def image_tagging_site_list(self) -> GuidCollection:
        """Gets the ImageTaggingSiteList property"""
        return self.properties.get("ImageTaggingSiteList", GuidCollection())

    @property
    def image_tagging_site_list_file_name(self) -> Optional[str]:
        """Gets the ImageTaggingSiteListFileName property"""
        return self.properties.get("ImageTaggingSiteListFileName", None)

    @property
    def include_at_a_glance_in_share_emails(self) -> Optional[bool]:
        """Gets the IncludeAtAGlanceInShareEmails property"""
        return self.properties.get("IncludeAtAGlanceInShareEmails", None)

    @property
    def ip_address_wac_token_lifetime(self) -> Optional[int]:
        """Gets the IPAddressWACTokenLifetime property"""
        return self.properties.get("IPAddressWACTokenLifetime", None)

    @property
    def is_app_bar_temporarily_disabled(self) -> Optional[bool]:
        """Gets the IsAppBarTemporarilyDisabled property"""
        return self.properties.get("IsAppBarTemporarilyDisabled", None)

    @property
    def is_collab_meeting_notes_fluid_enabled(self) -> Optional[bool]:
        """Gets the IsCollabMeetingNotesFluidEnabled property"""
        return self.properties.get("IsCollabMeetingNotesFluidEnabled", None)

    @property
    def is_data_access_in_card_designer_enabled(self) -> Optional[bool]:
        """Gets the IsDataAccessInCardDesignerEnabled property"""
        return self.properties.get("IsDataAccessInCardDesignerEnabled", None)

    @property
    def is_enable_app_auth_pop_up_enabled(self) -> Optional[bool]:
        """Gets the IsEnableAppAuthPopUpEnabled property"""
        return self.properties.get("IsEnableAppAuthPopUpEnabled", None)

    @property
    def is_file_preview_domain_restriction_enabled(self) -> Optional[bool]:
        """Gets the IsFilePreviewDomainRestrictionEnabled property"""
        return self.properties.get("IsFilePreviewDomainRestrictionEnabled", None)

    @property
    def is_fluid_enabled(self) -> Optional[bool]:
        """Gets the IsFluidEnabled property"""
        return self.properties.get("IsFluidEnabled", None)

    @property
    def is_hub_sites_multi_geo_flight_enabled(self) -> Optional[bool]:
        """Gets the IsHubSitesMultiGeoFlightEnabled property"""
        return self.properties.get("IsHubSitesMultiGeoFlightEnabled", None)

    @property
    def is_loop_enabled(self) -> Optional[bool]:
        """Gets the IsLoopEnabled property"""
        return self.properties.get("IsLoopEnabled", None)

    @property
    def is_mn_a_flight_enabled(self) -> Optional[bool]:
        """Gets the IsMnAFlightEnabled property"""
        return self.properties.get("IsMnAFlightEnabled", None)

    @property
    def is_multi_geo(self) -> Optional[bool]:
        """Gets the IsMultiGeo property"""
        return self.properties.get("IsMultiGeo", None)

    @property
    def is_multiple_home_sites_flight_enabled(self) -> Optional[bool]:
        """Gets the IsMultipleHomeSitesFlightEnabled property"""
        return self.properties.get("IsMultipleHomeSitesFlightEnabled", None)

    @property
    def is_multiple_viva_connections_flight_enabled(self) -> Optional[bool]:
        """Gets the IsMultipleVivaConnectionsFlightEnabled property"""
        return self.properties.get("IsMultipleVivaConnectionsFlightEnabled", None)

    @property
    def is_only_certified_apps_allowed(self) -> Optional[bool]:
        """Gets the IsOnlyCertifiedAppsAllowed property"""
        return self.properties.get("IsOnlyCertifiedAppsAllowed", None)

    @property
    def is_self_service_container_type_management_enabled(self) -> Optional[bool]:
        """Gets the IsSelfServiceContainerTypeManagementEnabled property"""
        return self.properties.get("IsSelfServiceContainerTypeManagementEnabled", None)

    @property
    def is_unmanaged_sync_client_for_tenant_restricted(self) -> Optional[bool]:
        """Gets the IsUnmanagedSyncClientForTenantRestricted property"""
        return self.properties.get("IsUnmanagedSyncClientForTenantRestricted", None)

    @property
    def is_unmanaged_sync_client_restriction_flight_enabled(self) -> Optional[bool]:
        """Gets the IsUnmanagedSyncClientRestrictionFlightEnabled property"""
        return self.properties.get("IsUnmanagedSyncClientRestrictionFlightEnabled", None)

    @property
    def is_viva_home_flight_enabled(self) -> Optional[bool]:
        """Gets the IsVivaHomeFlightEnabled property"""
        return self.properties.get("IsVivaHomeFlightEnabled", None)

    @property
    def is_viva_home_ga_flight_enabled(self) -> Optional[bool]:
        """Gets the IsVivaHomeGAFlightEnabled property"""
        return self.properties.get("IsVivaHomeGAFlightEnabled", None)

    @property
    def is_wb_fluid_enabled(self) -> Optional[bool]:
        """Gets the IsWBFluidEnabled property"""
        return self.properties.get("IsWBFluidEnabled", None)

    @property
    def knowledge_agent_enabled(self) -> Optional[bool]:
        """Gets the KnowledgeAgentEnabled property"""
        return self.properties.get("KnowledgeAgentEnabled", None)

    @property
    def knowledge_agent_scope_mode(self) -> Optional[int]:
        """Gets the KnowledgeAgentScopeMode property"""
        return self.properties.get("KnowledgeAgentScopeMode", None)

    @property
    def knowledge_agent_site_info_list(self) -> ClientValueCollection[SiteInfoForSitePicker]:
        """Gets the KnowledgeAgentSiteInfoList property"""
        from office365.sharepoint.tenant.administration.siteinfo_for_site_picker import (
            SiteInfoForSitePicker,
        )

        return self.properties.get(
            "KnowledgeAgentSiteInfoList", ClientValueCollection[SiteInfoForSitePicker](SiteInfoForSitePicker)
        )

    @property
    def knowledge_agent_site_list(self) -> GuidCollection:
        """Gets the KnowledgeAgentSiteList property"""
        return self.properties.get("KnowledgeAgentSiteList", GuidCollection())

    @property
    def knowledge_agent_site_list_file_name(self) -> Optional[str]:
        """Gets the KnowledgeAgentSiteListFileName property"""
        return self.properties.get("KnowledgeAgentSiteListFileName", None)

    @property
    def label_mismatch_email_help_link(self) -> Optional[str]:
        """Gets the LabelMismatchEmailHelpLink property"""
        return self.properties.get("LabelMismatchEmailHelpLink", None)

    @property
    def legacy_browser_auth_protocols_enabled(self) -> Optional[bool]:
        """Gets the LegacyBrowserAuthProtocolsEnabled property"""
        return self.properties.get("LegacyBrowserAuthProtocolsEnabled", None)

    @property
    def limited_access_file_type(self) -> Optional[int]:
        """Gets the LimitedAccessFileType property"""
        return self.properties.get("LimitedAccessFileType", None)

    @property
    def m365_additional_storage_spo_enabled(self) -> Optional[bool]:
        """Gets the M365AdditionalStorageSPOEnabled property"""
        return self.properties.get("M365AdditionalStorageSPOEnabled", None)

    @property
    def m365_sharepoint_storage_enabled(self) -> Optional[bool]:
        """Gets the M365SharePointStorageEnabled property"""
        return self.properties.get("M365SharePointStorageEnabled", None)

    @property
    def machine_learning_capture_enabled(self) -> Optional[bool]:
        """Gets the MachineLearningCaptureEnabled property"""
        return self.properties.get("MachineLearningCaptureEnabled", None)

    @property
    def major_version_limit(self) -> Optional[int]:
        """Gets the MajorVersionLimit property"""
        return self.properties.get("MajorVersionLimit", None)

    @property
    def managed_paths_for_site_creation(self) -> StringCollection:
        """Gets the ManagedPathsForSiteCreation property"""
        return self.properties.get("ManagedPathsForSiteCreation", StringCollection())

    @property
    def mark_all_files_as_sensitive_by_default(self) -> Optional[bool]:
        """Gets the MarkAllFilesAsSensitiveByDefault property"""
        return self.properties.get("MarkAllFilesAsSensitiveByDefault", None)

    @property
    def mark_new_files_sensitive_by_default(self) -> Optional[int]:
        """Gets the MarkNewFilesSensitiveByDefault property"""
        return self.properties.get("MarkNewFilesSensitiveByDefault", None)

    @property
    def mass_delete_notification_disabled(self) -> Optional[bool]:
        """Gets the MassDeleteNotificationDisabled property"""
        return self.properties.get("MassDeleteNotificationDisabled", None)

    @property
    def mass_delete_notification_disabled_for_odb(self) -> Optional[bool]:
        """Gets the MassDeleteNotificationDisabledForODB property"""
        return self.properties.get("MassDeleteNotificationDisabledForODB", None)

    @property
    def mass_delete_notification_disabled_for_spo(self) -> Optional[bool]:
        """Gets the MassDeleteNotificationDisabledForSPO property"""
        return self.properties.get("MassDeleteNotificationDisabledForSPO", None)

    @property
    def max_site_storage_quota_mb(self) -> Optional[int]:
        """Gets the MaxSiteStorageQuotaMB property"""
        return self.properties.get("MaxSiteStorageQuotaMB", None)

    @property
    def media_transcription(self) -> Optional[int]:
        """Gets the MediaTranscription property"""
        return self.properties.get("MediaTranscription", None)

    @property
    def media_transcription_automatic_features(self) -> Optional[int]:
        """Gets the MediaTranscriptionAutomaticFeatures property"""
        return self.properties.get("MediaTranscriptionAutomaticFeatures", None)

    @property
    def mobile_friendly_url_enabled_in_tenant(self) -> Optional[bool]:
        """Gets the MobileFriendlyUrlEnabledInTenant property"""
        return self.properties.get("MobileFriendlyUrlEnabledInTenant", None)

    @property
    def new_sharepoint_experience_opt_in(self) -> Optional[bool]:
        """Gets the NewSharePointExperienceOptIn property"""
        return self.properties.get("NewSharePointExperienceOptIn", None)

    @property
    def notifications_in_onedrive_for_business_enabled(self) -> Optional[bool]:
        """Gets the NotificationsInOneDriveForBusinessEnabled property"""
        return self.properties.get("NotificationsInOneDriveForBusinessEnabled", None)

    @property
    def notifications_in_sharepoint_enabled(self) -> Optional[bool]:
        """Gets the NotificationsInSharePointEnabled property"""
        return self.properties.get("NotificationsInSharePointEnabled", None)

    @property
    def ocr_admin_odb_group_list(self) -> GuidCollection:
        """Gets the OCRAdminODBGroupList property"""
        return self.properties.get("OCRAdminODBGroupList", GuidCollection())

    @property
    def ocr_admin_odb_user_list(self) -> GuidCollection:
        """Gets the OCRAdminODBUserList property"""
        return self.properties.get("OCRAdminODBUserList", GuidCollection())

    @property
    def ocr_admin_site_info_list(self) -> ClientValueCollection[SiteInfoForSitePicker]:
        """Gets the OCRAdminSiteInfoList property"""
        from office365.sharepoint.tenant.administration.siteinfo_for_site_picker import (
            SiteInfoForSitePicker,
        )

        return self.properties.get(
            "OCRAdminSiteInfoList", ClientValueCollection[SiteInfoForSitePicker](SiteInfoForSitePicker)
        )

    @property
    def ocr_admin_site_list(self) -> GuidCollection:
        """Gets the OCRAdminSiteList property"""
        return self.properties.get("OCRAdminSiteList", GuidCollection())

    @property
    def ocr_admin_site_list_file_name(self) -> Optional[str]:
        """Gets the OCRAdminSiteListFileName property"""
        return self.properties.get("OCRAdminSiteListFileName", None)

    @property
    def ocr_compliance_odb_group_list(self) -> GuidCollection:
        """Gets the OCRComplianceODBGroupList property"""
        return self.properties.get("OCRComplianceODBGroupList", GuidCollection())

    @property
    def ocr_compliance_odb_user_list(self) -> GuidCollection:
        """Gets the OCRComplianceODBUserList property"""
        return self.properties.get("OCRComplianceODBUserList", GuidCollection())

    @property
    def ocr_compliance_site_info_list(self) -> ClientValueCollection[SiteInfoForSitePicker]:
        """Gets the OCRComplianceSiteInfoList property"""
        from office365.sharepoint.tenant.administration.siteinfo_for_site_picker import (
            SiteInfoForSitePicker,
        )

        return self.properties.get(
            "OCRComplianceSiteInfoList", ClientValueCollection[SiteInfoForSitePicker](SiteInfoForSitePicker)
        )

    @property
    def ocr_compliance_site_list(self) -> GuidCollection:
        """Gets the OCRComplianceSiteList property"""
        return self.properties.get("OCRComplianceSiteList", GuidCollection())

    @property
    def ocr_compliance_site_list_file_name(self) -> Optional[str]:
        """Gets the OCRComplianceSiteListFileName property"""
        return self.properties.get("OCRComplianceSiteListFileName", None)

    @property
    def ocr_mode_for_admin_odbs(self) -> Optional[int]:
        """Gets the OCRModeForAdminODBs property"""
        return self.properties.get("OCRModeForAdminODBs", None)

    @property
    def ocr_mode_for_admin_sites(self) -> Optional[int]:
        """Gets the OCRModeForAdminSites property"""
        return self.properties.get("OCRModeForAdminSites", None)

    @property
    def ocr_mode_for_compliance_odbs(self) -> Optional[int]:
        """Gets the OCRModeForComplianceODBs property"""
        return self.properties.get("OCRModeForComplianceODBs", None)

    @property
    def ocr_mode_for_compliance_sites(self) -> Optional[int]:
        """Gets the OCRModeForComplianceSites property"""
        return self.properties.get("OCRModeForComplianceSites", None)

    @property
    def odb_access_requests(self) -> Optional[int]:
        """Gets the ODBAccessRequests property"""
        return self.properties.get("ODBAccessRequests", None)

    @property
    def odb_members_can_share(self) -> Optional[int]:
        """Gets the ODBMembersCanShare property"""
        return self.properties.get("ODBMembersCanShare", None)

    @property
    def odb_sensitivity_refresh_window_in_hours(self) -> Optional[int]:
        """Gets the ODBSensitivityRefreshWindowInHours property"""
        return self.properties.get("ODBSensitivityRefreshWindowInHours", None)

    @property
    def odb_sharing_capability(self) -> Optional[int]:
        """Gets the ODBSharingCapability property"""
        return self.properties.get("ODBSharingCapability", None)

    @property
    def odb_translation_enabled(self) -> Optional[bool]:
        """Gets the ODBTranslationEnabled property"""
        return self.properties.get("ODBTranslationEnabled", None)

    @property
    def office_client_adal_disabled(self) -> Optional[bool]:
        """Gets the OfficeClientADALDisabled property"""
        return self.properties.get("OfficeClientADALDisabled", None)

    @property
    def onedrive_anyone_sharing_link_max_expiration_in_days(self) -> Optional[int]:
        """Gets the OneDriveAnyoneSharingLinkMaxExpirationInDays property"""
        return self.properties.get("OneDriveAnyoneSharingLinkMaxExpirationInDays", None)

    @property
    def onedrive_anyone_sharing_link_recommended_expiration_in_days(self) -> Optional[int]:
        """Gets the OneDriveAnyoneSharingLinkRecommendedExpirationInDays property"""
        return self.properties.get("OneDriveAnyoneSharingLinkRecommendedExpirationInDays", None)

    @property
    def onedrive_block_guests_as_site_admin(self) -> Optional[int]:
        """Gets the OneDriveBlockGuestsAsSiteAdmin property"""
        return self.properties.get("OneDriveBlockGuestsAsSiteAdmin", None)

    @property
    def onedrive_default_link_to_existing_access(self) -> Optional[bool]:
        """Gets the OneDriveDefaultLinkToExistingAccess property"""
        return self.properties.get("OneDriveDefaultLinkToExistingAccess", None)

    @property
    def onedrive_default_share_link_role(self) -> Optional[int]:
        """Gets the OneDriveDefaultShareLinkRole property"""
        return self.properties.get("OneDriveDefaultShareLinkRole", None)

    @property
    def onedrive_default_share_link_scope(self) -> Optional[int]:
        """Gets the OneDriveDefaultShareLinkScope property"""
        return self.properties.get("OneDriveDefaultShareLinkScope", None)

    @property
    def onedrive_for_guests_enabled(self) -> Optional[bool]:
        """Gets the OneDriveForGuestsEnabled property"""
        return self.properties.get("OneDriveForGuestsEnabled", None)

    @property
    def onedrive_loop_default_sharing_link_role(self) -> Optional[int]:
        """Gets the OneDriveLoopDefaultSharingLinkRole property"""
        return self.properties.get("OneDriveLoopDefaultSharingLinkRole", None)

    @property
    def onedrive_loop_default_sharing_link_scope(self) -> Optional[int]:
        """Gets the OneDriveLoopDefaultSharingLinkScope property"""
        return self.properties.get("OneDriveLoopDefaultSharingLinkScope", None)

    @property
    def onedrive_loop_sharing_capability(self) -> Optional[int]:
        """Gets the OneDriveLoopSharingCapability property"""
        return self.properties.get("OneDriveLoopSharingCapability", None)

    @property
    def onedrive_organization_sharing_link_max_expiration_in_days(self) -> Optional[int]:
        """Gets the OneDriveOrganizationSharingLinkMaxExpirationInDays property"""
        return self.properties.get("OneDriveOrganizationSharingLinkMaxExpirationInDays", None)

    @property
    def onedrive_organization_sharing_link_recommended_expiration_in_days(self) -> Optional[int]:
        """Gets the OneDriveOrganizationSharingLinkRecommendedExpirationInDays property"""
        return self.properties.get("OneDriveOrganizationSharingLinkRecommendedExpirationInDays", None)

    @property
    def onedrive_request_files_link_enabled(self) -> Optional[bool]:
        """Gets the OneDriveRequestFilesLinkEnabled property"""
        return self.properties.get("OneDriveRequestFilesLinkEnabled", None)

    @property
    def onedrive_request_files_link_expiration_in_days(self) -> Optional[int]:
        """Gets the OneDriveRequestFilesLinkExpirationInDays property"""
        return self.properties.get("OneDriveRequestFilesLinkExpirationInDays", None)

    @property
    def onedrive_storage_quota(self) -> Optional[int]:
        """Gets the OneDriveStorageQuota property"""
        return self.properties.get("OneDriveStorageQuota", None)

    @property
    def opt_out_of_groove_block(self) -> Optional[bool]:
        """Gets the OptOutOfGrooveBlock property"""
        return self.properties.get("OptOutOfGrooveBlock", None)

    @property
    def opt_out_of_groove_soft_block(self) -> Optional[bool]:
        """Gets the OptOutOfGrooveSoftBlock property"""
        return self.properties.get("OptOutOfGrooveSoftBlock", None)

    @property
    def org_news_site_url(self) -> Optional[str]:
        """Gets the OrgNewsSiteUrl property"""
        return self.properties.get("OrgNewsSiteUrl", None)

    @property
    def orphaned_personal_sites_retention_period(self) -> Optional[int]:
        """Gets the OrphanedPersonalSitesRetentionPeriod property"""
        return self.properties.get("OrphanedPersonalSitesRetentionPeriod", None)

    @property
    def owner_anonymous_notification(self) -> Optional[bool]:
        """Gets the OwnerAnonymousNotification property"""
        return self.properties.get("OwnerAnonymousNotification", None)

    @property
    def permissive_browser_file_handling_override(self) -> Optional[bool]:
        """Gets the PermissiveBrowserFileHandlingOverride property"""
        return self.properties.get("PermissiveBrowserFileHandlingOverride", None)

    @property
    def prebuilt_enabled(self) -> Optional[bool]:
        """Gets the PrebuiltEnabled property"""
        return self.properties.get("PrebuiltEnabled", None)

    @property
    def prebuilt_enabled_in_content_center(self) -> Optional[int]:
        """Gets the PrebuiltEnabledInContentCenter property"""
        return self.properties.get("PrebuiltEnabledInContentCenter", None)

    @property
    def prebuilt_site_info_list(self) -> ClientValueCollection[SiteInfoForSitePicker]:
        """Gets the PrebuiltSiteInfoList property"""
        from office365.sharepoint.tenant.administration.siteinfo_for_site_picker import (
            SiteInfoForSitePicker,
        )

        return self.properties.get(
            "PrebuiltSiteInfoList", ClientValueCollection[SiteInfoForSitePicker](SiteInfoForSitePicker)
        )

    @property
    def prebuilt_site_list(self) -> GuidCollection:
        """Gets the PrebuiltSiteList property"""
        return self.properties.get("PrebuiltSiteList", GuidCollection())

    @property
    def prebuilt_site_list_file_name(self) -> Optional[str]:
        """Gets the PrebuiltSiteListFileName property"""
        return self.properties.get("PrebuiltSiteListFileName", None)

    @property
    def prevent_external_users_from_resharing(self) -> Optional[bool]:
        """Gets the PreventExternalUsersFromResharing property"""
        return self.properties.get("PreventExternalUsersFromResharing", None)

    @property
    def provision_shared_with_everyone_folder(self) -> Optional[bool]:
        """Gets the ProvisionSharedWithEveryoneFolder property"""
        return self.properties.get("ProvisionSharedWithEveryoneFolder", None)

    @property
    def public_cdn_allowed_file_types(self) -> Optional[str]:
        """Gets the PublicCdnAllowedFileTypes property"""
        return self.properties.get("PublicCdnAllowedFileTypes", None)

    @property
    def public_cdn_enabled(self) -> Optional[bool]:
        """Gets the PublicCdnEnabled property"""
        return self.properties.get("PublicCdnEnabled", None)

    @property
    def public_cdn_origins(self) -> StringCollection:
        """Gets the PublicCdnOrigins property"""
        return self.properties.get("PublicCdnOrigins", StringCollection())

    @property
    def reactivation_cost(self) -> Optional[float]:
        """Gets the ReactivationCost property"""
        return self.properties.get("ReactivationCost", None)

    @property
    def recycle_bin_retention_period(self) -> Optional[int]:
        """Gets the RecycleBinRetentionPeriod property"""
        return self.properties.get("RecycleBinRetentionPeriod", None)

    @property
    def reduce_temp_token_lifetime_enabled(self) -> Optional[bool]:
        """Gets the ReduceTempTokenLifetimeEnabled property"""
        return self.properties.get("ReduceTempTokenLifetimeEnabled", None)

    @property
    def reduce_temp_token_lifetime_value(self) -> Optional[int]:
        """Gets the ReduceTempTokenLifetimeValue property"""
        return self.properties.get("ReduceTempTokenLifetimeValue", None)

    @property
    def require_accepting_account_match_invited_account(self) -> Optional[bool]:
        """Gets the RequireAcceptingAccountMatchInvitedAccount property"""
        return self.properties.get("RequireAcceptingAccountMatchInvitedAccount", None)

    @property
    def require_anonymous_links_expire_in_days(self) -> Optional[int]:
        """Gets the RequireAnonymousLinksExpireInDays property"""
        return self.properties.get("RequireAnonymousLinksExpireInDays", None)

    @property
    def resource_quota(self) -> Optional[float]:
        """Gets the ResourceQuota property"""
        return self.properties.get("ResourceQuota", None)

    @property
    def resource_quota_allocated(self) -> Optional[float]:
        """Gets the ResourceQuotaAllocated property"""
        return self.properties.get("ResourceQuotaAllocated", None)

    @property
    def restricted_access_control_for_onedrive_error_help_link(self) -> Optional[str]:
        """Gets the RestrictedAccessControlForOneDriveErrorHelpLink property"""
        return self.properties.get("RestrictedAccessControlForOneDriveErrorHelpLink", None)

    @property
    def restricted_access_controlfor_sites_error_help_link(self) -> Optional[str]:
        """Gets the RestrictedAccessControlforSitesErrorHelpLink property"""
        return self.properties.get("RestrictedAccessControlforSitesErrorHelpLink", None)

    @property
    def restricted_onedrive_license(self) -> Optional[bool]:
        """Gets the RestrictedOneDriveLicense property"""
        return self.properties.get("RestrictedOneDriveLicense", None)

    @property
    def restricted_sharepoint_license(self) -> Optional[bool]:
        """Gets the RestrictedSharePointLicense property"""
        return self.properties.get("RestrictedSharePointLicense", None)

    @property
    def restrict_external_sharing(self) -> GuidCollection:
        """Gets the RestrictExternalSharing property"""
        return self.properties.get("RestrictExternalSharing", GuidCollection())

    @property
    def restrict_external_sharing_for_agents(self) -> Optional[bool]:
        """Gets the RestrictExternalSharingForAgents property"""
        return self.properties.get("RestrictExternalSharingForAgents", None)

    @property
    def restrict_resource_account_access(self) -> Optional[bool]:
        """Gets the RestrictResourceAccountAccess property"""
        return self.properties.get("RestrictResourceAccountAccess", None)

    @property
    def search_resolve_exact_email_or_upn(self) -> Optional[bool]:
        """Gets the SearchResolveExactEmailOrUPN property"""
        return self.properties.get("SearchResolveExactEmailOrUPN", None)

    @property
    def self_service_site_creation_disabled(self) -> Optional[bool]:
        """Gets the SelfServiceSiteCreationDisabled property"""
        return self.properties.get("SelfServiceSiteCreationDisabled", None)

    @property
    def sharepoint_add_ins_blocked(self) -> Optional[bool]:
        """Gets the SharePointAddInsBlocked property"""
        return self.properties.get("SharePointAddInsBlocked", None)

    @property
    def sharepoint_add_ins_disabled(self) -> Optional[bool]:
        """Gets the SharePointAddInsDisabled property"""
        return self.properties.get("SharePointAddInsDisabled", None)

    @property
    def sharing_allowed_domain_list(self) -> Optional[str]:
        """Gets the SharingAllowedDomainList property"""
        return self.properties.get("SharingAllowedDomainList", None)

    @property
    def sharing_blocked_domain_list(self) -> Optional[str]:
        """Gets the SharingBlockedDomainList property"""
        return self.properties.get("SharingBlockedDomainList", None)

    @property
    def sharing_capability(self) -> Optional[int]:
        """Gets the SharingCapability property"""
        return self.properties.get("SharingCapability", None)

    @property
    def sharing_domain_restriction_mode(self) -> Optional[int]:
        """Gets the SharingDomainRestrictionMode property"""
        return self.properties.get("SharingDomainRestrictionMode", None)

    @property
    def show_all_users_claim(self) -> Optional[bool]:
        """Gets the ShowAllUsersClaim property"""
        return self.properties.get("ShowAllUsersClaim", None)

    @property
    def show_everyone_claim(self) -> Optional[bool]:
        """Gets the ShowEveryoneClaim property"""
        return self.properties.get("ShowEveryoneClaim", None)

    @property
    def show_everyone_except_external_users_claim(self) -> Optional[bool]:
        """Gets the ShowEveryoneExceptExternalUsersClaim property"""
        return self.properties.get("ShowEveryoneExceptExternalUsersClaim", None)

    @property
    def show_ngsc_dialog_for_sync_on_odb(self) -> Optional[bool]:
        """Gets the ShowNGSCDialogForSyncOnODB property"""
        return self.properties.get("ShowNGSCDialogForSyncOnODB", None)

    @property
    def show_open_in_desktop_option_for_synced_files(self) -> Optional[bool]:
        """Gets the ShowOpenInDesktopOptionForSyncedFiles property"""
        return self.properties.get("ShowOpenInDesktopOptionForSyncedFiles", None)

    @property
    def show_people_picker_group_suggestions_for_ib(self) -> Optional[bool]:
        """Gets the ShowPeoplePickerGroupSuggestionsForIB property"""
        return self.properties.get("ShowPeoplePickerGroupSuggestionsForIB", None)

    @property
    def show_people_picker_suggestions_for_guest_users(self) -> Optional[bool]:
        """Gets the ShowPeoplePickerSuggestionsForGuestUsers property"""
        return self.properties.get("ShowPeoplePickerSuggestionsForGuestUsers", None)

    @property
    def sign_in_acceleration_domain(self) -> Optional[str]:
        """Gets the SignInAccelerationDomain property"""
        return self.properties.get("SignInAccelerationDomain", None)

    @property
    def site_owner_manage_legacy_service_principal_enabled(self) -> Optional[bool]:
        """Gets the SiteOwnerManageLegacyServicePrincipalEnabled property"""
        return self.properties.get("SiteOwnerManageLegacyServicePrincipalEnabled", None)

    @property
    def site_owners_can_access_missing_content(self) -> Optional[bool]:
        """Gets the SiteOwnersCanAccessMissingContent property"""
        return self.properties.get("SiteOwnersCanAccessMissingContent", None)

    @property
    def social_bar_on_site_pages_disabled(self) -> Optional[bool]:
        """Gets the SocialBarOnSitePagesDisabled property"""
        return self.properties.get("SocialBarOnSitePagesDisabled", None)

    @property
    def special_characters_state_in_file_folder_names(self) -> Optional[int]:
        """Gets the SpecialCharactersStateInFileFolderNames property"""
        return self.properties.get("SpecialCharactersStateInFileFolderNames", None)

    @property
    def sp_jit_dlp_policy_data(self) -> SPJitDlpPolicyData:
        """Gets the SPJitDlpPolicyData property"""
        from office365.sharepoint.authpolicy.spjitdlppolicydata import (
            SPJitDlpPolicyData,
        )

        return self.properties.get("SPJitDlpPolicyData", SPJitDlpPolicyData())

    @property
    def start_a_site_form_url(self) -> Optional[str]:
        """Gets the StartASiteFormUrl property"""
        return self.properties.get("StartASiteFormUrl", None)

    @property
    def stop_alerts(self) -> Optional[bool]:
        """Gets the StopAlerts property"""
        return self.properties.get("StopAlerts", None)

    @property
    def stop_new2010_workflows(self) -> Optional[bool]:
        """Gets the StopNew2010Workflows property"""
        return self.properties.get("StopNew2010Workflows", None)

    @property
    def stop_new2013_workflows(self) -> Optional[bool]:
        """Gets the StopNew2013Workflows property"""
        return self.properties.get("StopNew2013Workflows", None)

    @property
    def storage_quota(self) -> Optional[int]:
        """Gets the StorageQuota property"""
        return self.properties.get("StorageQuota", None)

    @property
    def storage_quota_allocated(self) -> Optional[int]:
        """Gets the StorageQuotaAllocated property"""
        return self.properties.get("StorageQuotaAllocated", None)

    @property
    def stream_launch_config(self) -> Optional[int]:
        """Gets the StreamLaunchConfig property"""
        return self.properties.get("StreamLaunchConfig", None)

    @property
    def stream_launch_config_last_updated(self) -> Optional[datetime]:
        """Gets the StreamLaunchConfigLastUpdated property"""
        return self.properties.get("StreamLaunchConfigLastUpdated", datetime.min)

    @property
    def stream_launch_config_update_count(self) -> Optional[int]:
        """Gets the StreamLaunchConfigUpdateCount property"""
        return self.properties.get("StreamLaunchConfigUpdateCount", None)

    @property
    def sync_privacy_profile_properties(self) -> Optional[bool]:
        """Gets the SyncPrivacyProfileProperties property"""
        return self.properties.get("SyncPrivacyProfileProperties", None)

    @property
    def syntex_media_analytics_settings(self) -> SyntexPremiumFeatureSettings:
        """Gets the SyntexMediaAnalyticsSettings property"""
        from office365.sharepoint.tenant.administration.syntex.premiumfeaturesettings import (
            SyntexPremiumFeatureSettings,
        )

        return self.properties.get("SyntexMediaAnalyticsSettings", SyntexPremiumFeatureSettings())

    @property
    def syntex_playback_transcript_translation_settings(self) -> SyntexPremiumFeatureSettings:
        """Gets the SyntexPlaybackTranscriptTranslationSettings property"""
        from office365.sharepoint.tenant.administration.syntex.premiumfeaturesettings import (
            SyntexPremiumFeatureSettings,
        )

        return self.properties.get("SyntexPlaybackTranscriptTranslationSettings", SyntexPremiumFeatureSettings())

    @property
    def taxonomy_tagging_site_info_list(self) -> ClientValueCollection[SiteInfoForSitePicker]:
        """Gets the TaxonomyTaggingSiteInfoList property"""
        from office365.sharepoint.tenant.administration.siteinfo_for_site_picker import (
            SiteInfoForSitePicker,
        )

        return self.properties.get(
            "TaxonomyTaggingSiteInfoList", ClientValueCollection[SiteInfoForSitePicker](SiteInfoForSitePicker)
        )

    @property
    def taxonomy_tagging_site_list(self) -> GuidCollection:
        """Gets the TaxonomyTaggingSiteList property"""
        return self.properties.get("TaxonomyTaggingSiteList", GuidCollection())

    @property
    def taxonomy_tagging_site_list_file_name(self) -> Optional[str]:
        """Gets the TaxonomyTaggingSiteListFileName property"""
        return self.properties.get("TaxonomyTaggingSiteListFileName", None)

    @property
    def tls_token_binding_policy_value(self) -> Optional[int]:
        """Gets the TlsTokenBindingPolicyValue property"""
        return self.properties.get("TlsTokenBindingPolicyValue", None)

    @property
    def translation_enabled(self) -> Optional[bool]:
        """Gets the TranslationEnabled property"""
        return self.properties.get("TranslationEnabled", None)

    @property
    def translation_site_info_list(self) -> ClientValueCollection[SiteInfoForSitePicker]:
        """Gets the TranslationSiteInfoList property"""
        from office365.sharepoint.tenant.administration.siteinfo_for_site_picker import (
            SiteInfoForSitePicker,
        )

        return self.properties.get(
            "TranslationSiteInfoList", ClientValueCollection[SiteInfoForSitePicker](SiteInfoForSitePicker)
        )

    @property
    def translation_site_list(self) -> GuidCollection:
        """Gets the TranslationSiteList property"""
        return self.properties.get("TranslationSiteList", GuidCollection())

    @property
    def translation_site_list_file_name(self) -> Optional[str]:
        """Gets the TranslationSiteListFileName property"""
        return self.properties.get("TranslationSiteListFileName", None)

    @property
    def universal_annotation_disabled(self) -> Optional[bool]:
        """Gets the UniversalAnnotationDisabled property"""
        return self.properties.get("UniversalAnnotationDisabled", None)

    @property
    def unlicensed_odb_active_storage_retention_period(self) -> Optional[int]:
        """Gets the UnlicensedOdbActiveStorageRetentionPeriod property"""
        return self.properties.get("UnlicensedOdbActiveStorageRetentionPeriod", None)

    @property
    def unlicensed_odb_storage_billing_mode(self) -> Optional[int]:
        """Gets the UnlicensedOdbStorageBillingMode property"""
        return self.properties.get("UnlicensedOdbStorageBillingMode", None)

    @property
    def unlicensed_odb_syntex_billing_enabled(self) -> Optional[bool]:
        """Gets the UnlicensedOdbSyntexBillingEnabled property"""
        return self.properties.get("UnlicensedOdbSyntexBillingEnabled", None)

    @property
    def unlicensed_onedrive_for_business_tenant_metrics_data(self) -> UnlicensedOdbTenantMetrics:
        """Gets the UnlicensedOneDriveForBusinessTenantMetricsData property"""
        from office365.sharepoint.administration.unlicensedodbtenantmetrics import (
            UnlicensedOdbTenantMetrics,
        )

        return self.properties.get("UnlicensedOneDriveForBusinessTenantMetricsData", UnlicensedOdbTenantMetrics())

    @property
    def use_find_people_in_people_picker(self) -> Optional[bool]:
        """Gets the UseFindPeopleInPeoplePicker property"""
        return self.properties.get("UseFindPeopleInPeoplePicker", None)

    @property
    def use_persistent_cookies_for_explorer_view(self) -> Optional[bool]:
        """Gets the UsePersistentCookiesForExplorerView property"""
        return self.properties.get("UsePersistentCookiesForExplorerView", None)

    @property
    def version_policy_file_type_override(self) -> ClientValueCollection[SPOFileVersionFileTypePolicySettings]:
        """Gets the VersionPolicyFileTypeOverride property"""
        from office365.sharepoint.tenant.administration.spofileversionfiletypepolicysettings import (
            SPOFileVersionFileTypePolicySettings,
        )

        return self.properties.get(
            "VersionPolicyFileTypeOverride",
            ClientValueCollection[SPOFileVersionFileTypePolicySettings](SPOFileVersionFileTypePolicySettings),
        )

    @property
    def viewers_can_comment_on_media_disabled(self) -> Optional[bool]:
        """Gets the ViewersCanCommentOnMediaDisabled property"""
        return self.properties.get("ViewersCanCommentOnMediaDisabled", None)

    @property
    def view_in_file_explorer_enabled(self) -> Optional[bool]:
        """Gets the ViewInFileExplorerEnabled property"""
        return self.properties.get("ViewInFileExplorerEnabled", None)

    @property
    def who_can_share_allow_list_in_tenant(self) -> Optional[str]:
        """Gets the WhoCanShareAllowListInTenant property"""
        return self.properties.get("WhoCanShareAllowListInTenant", None)

    @property
    def who_can_share_allow_list_in_tenant_by_group_id(self) -> StringCollection:
        """Gets the WhoCanShareAllowListInTenantByGroupId property"""
        return self.properties.get("WhoCanShareAllowListInTenantByGroupId", StringCollection())

    @property
    def who_can_share_allow_list_in_tenant_by_principal_identity(self) -> StringCollection:
        """Gets the WhoCanShareAllowListInTenantByPrincipalIdentity property"""
        return self.properties.get("WhoCanShareAllowListInTenantByPrincipalIdentity", StringCollection())

    @property
    def workflow2010_disabled(self) -> Optional[bool]:
        """Gets the Workflow2010Disabled property"""
        return self.properties.get("Workflow2010Disabled", None)

    @property
    def workflows2013_state(self) -> Optional[int]:
        """Gets the Workflows2013State property"""
        return self.properties.get("Workflows2013State", None)

    @property
    def catalog_management(self) -> CatalogManagementCollection:
        """Gets the CatalogManagement property"""
        from office365.sharepoint.tenantadministration.catalog_management_collection import (
            CatalogManagementCollection,
        )

        return self.properties.get(
            "CatalogManagement",
            CatalogManagementCollection(self.context, ResourcePath("CatalogManagement", self.resource_path)),
        )

    @property
    def catalog_management_custom_properties(self) -> CatalogManagementCustomPropertiesCollection:
        """Gets the CatalogManagementCustomProperties property"""
        from office365.sharepoint.tenantadministration.catalog_management_custom_properties_collection import (
            CatalogManagementCustomPropertiesCollection,
        )

        return self.properties.get(
            "CatalogManagementCustomProperties",
            CatalogManagementCustomPropertiesCollection(
                self.context, ResourcePath("CatalogManagementCustomProperties", self.resource_path)
            ),
        )

    @property
    def catalog_management_restricted_content_discovery(self) -> CatalogManagementRestrictedContentDiscoveryCollection:
        """Gets the CatalogManagementRestrictedContentDiscovery property"""
        from office365.sharepoint.tenantadministration.catalog_management_restricted_content_discovery_collection import (  # noqa: E501
            CatalogManagementRestrictedContentDiscoveryCollection,
        )

        return self.properties.get(
            "CatalogManagementRestrictedContentDiscovery",
            CatalogManagementRestrictedContentDiscoveryCollection(
                self.context, ResourcePath("CatalogManagementRestrictedContentDiscovery", self.resource_path)
            ),
        )

    @property
    def tenant_data_loss_prevention_quarantine_settings(self) -> TenantDataLossPreventionQuarantineSettings:
        """Gets the TenantDataLossPreventionQuarantineSettings property"""
        from office365.sharepoint.tenant.administration.tenant_data_loss_prevention_quarantine_settings import (
            TenantDataLossPreventionQuarantineSettings,
        )

        return self.properties.get(
            "TenantDataLossPreventionQuarantineSettings",
            TenantDataLossPreventionQuarantineSettings(
                self.context, ResourcePath("TenantDataLossPreventionQuarantineSettings", self.resource_path)
            ),
        )

    def add_company_home_site(
        self, home_site_url: str, order: int, audiences: list[UUID]
    ) -> ClientResult[TargetedSiteDetails]:
        """AddCompanyHomeSite operation.

        Args:
            home_site_url (str):
                homeSiteUrl parameter
            order (int):
                order parameter
            audiences (list[UUID]):
                audiences parameter
        """
        from office365.sharepoint.viva.targetedsitedetails import TargetedSiteDetails

        return_type = ClientResult(self.context, TargetedSiteDetails())
        qry = ServiceOperationQuery(
            self,
            "AddCompanyHomeSite",
            None,
            {"homeSiteUrl": home_site_url, "order": order, "audiences": GuidCollection(audiences)},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def add_home_site(self, home_site_url: str, order: int, audiences: list[UUID]) -> ClientResult[TargetedSiteDetails]:
        """AddHomeSite operation.

        Args:
            home_site_url (str):
                homeSiteUrl parameter
            order (int):
                order parameter
            audiences (list[UUID]):
                audiences parameter
        """
        from office365.sharepoint.viva.targetedsitedetails import TargetedSiteDetails

        return_type = ClientResult(self.context, TargetedSiteDetails())
        qry = ServiceOperationQuery(
            self,
            "AddHomeSite",
            None,
            {"homeSiteUrl": home_site_url, "order": order, "audiences": GuidCollection(audiences)},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def add_pre_auth_allow_deny_list_item_setting(self, allow_pre_auth: bool, new_setting: str) -> Self:
        """AddPreAuthAllowDenyListItemSetting operation.

        Args:
            allow_pre_auth (bool):
                allowPreAuth parameter
            new_setting (str):
                newSetting parameter
        """
        qry = ServiceOperationQuery(
            self,
            "AddPreAuthAllowDenyListItemSetting",
            None,
            {"allowPreAuth": allow_pre_auth, "newSetting": new_setting},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def add_recent_admin_action(self, payload: TenantAdminRecentActionPayload) -> ClientResult[TenantAdminRecentAction]:
        """AddRecentAdminAction operation.

        Args:
            payload (TenantAdminRecentActionPayload):
                payload parameter
        """
        from office365.sharepoint.tenant.administration.recent_action import (
            TenantAdminRecentAction,
        )

        return_type = ClientResult(self.context, TenantAdminRecentAction())
        qry = ServiceOperationQuery(self, "AddRecentAdminAction", None, {"payload": payload}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add_recent_admin_actions(
        self, payload: ClientValueCollection[TenantAdminRecentActionPayload]
    ) -> ClientResult[ClientValueCollection[TenantAdminRecentAction]]:
        """AddRecentAdminActions operation.

        Args:
            payload (ClientValueCollection[TenantAdminRecentActionPayload]):
                payload parameter
        """
        from office365.sharepoint.tenant.administration.recent_action import (
            TenantAdminRecentAction,
        )

        return_type = ClientResult(self.context, ClientValueCollection[TenantAdminRecentAction]())
        qry = ServiceOperationQuery(self, "AddRecentAdminActions", None, {"payload": payload}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add_site_to_file_archive_policy(self, policy_id: UUID, site_url: str, is_excluded: bool) -> Self:
        """AddSiteToFileArchivePolicy operation.

        Args:
            policy_id (UUID):
                policyId parameter
            site_url (str):
                siteUrl parameter
            is_excluded (bool):
                isExcluded parameter
        """
        qry = ServiceOperationQuery(
            self,
            "AddSiteToFileArchivePolicy",
            None,
            {"policyId": policy_id, "siteUrl": site_url, "isExcluded": is_excluded},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def add_spo_container_user_role(self, container_id: str, login_name: str, role: str) -> Self:
        """AddSPOContainerUserRole operation.

        Args:
            container_id (str):
                ContainerId parameter
            login_name (str):
                loginName parameter
            role (str):
                role parameter
        """
        qry = ServiceOperationQuery(
            self,
            "AddSPOContainerUserRole",
            None,
            {"ContainerId": container_id, "loginName": login_name, "role": role},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def add_spo_restricted_search_allowed_list(self, site_urls: list[str]) -> Self:
        """AddSPORestrictedSearchAllowedList operation.

        Args:
            site_urls (list[str]):
                siteUrls parameter
        """
        qry = ServiceOperationQuery(
            self, "AddSPORestrictedSearchAllowedList", None, {"siteUrls": StringCollection(site_urls)}, None, None
        )
        self.context.add_query(qry)
        return self

    def add_spo_service_prioritization_app_registration(
        self, app_id: UUID, policy_id: UUID, quota_multiplier: int
    ) -> Self:
        """AddSPOServicePrioritizationAppRegistration operation.

        Args:
            app_id (UUID):
                appId parameter
            policy_id (UUID):
                policyId parameter
            quota_multiplier (int):
                quotaMultiplier parameter
        """
        qry = ServiceOperationQuery(
            self,
            "AddSPOServicePrioritizationAppRegistration",
            None,
            {"appId": app_id, "policyId": policy_id, "quotaMultiplier": quota_multiplier},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def add_syntex_custom_model_setting(self, model_setting: SyntexCustomModelSetting, scenario: int) -> Self:
        """AddSyntexCustomModelSetting operation.

        Args:
            model_setting (SyntexCustomModelSetting):
                modelSetting parameter
            scenario (int):
                scenario parameter
        """
        qry = ServiceOperationQuery(
            self, "AddSyntexCustomModelSetting", None, {"modelSetting": model_setting, "scenario": scenario}, None, None
        )
        self.context.add_query(qry)
        return self

    def add_to_org_assets_lib_and_cdn_v2(
        self, cdn_type: int, lib_url: str, thumbnail_url: str, org_asset_type: int, default_origin_added: bool
    ) -> Self:
        """AddToOrgAssetsLibAndCdnV2 operation.

        Args:
            cdn_type (int):
                cdnType parameter
            lib_url (str):
                libUrl parameter
            thumbnail_url (str):
                thumbnailUrl parameter
            org_asset_type (int):
                orgAssetType parameter
            default_origin_added (bool):
                defaultOriginAdded parameter
        """
        qry = ServiceOperationQuery(
            self,
            "AddToOrgAssetsLibAndCdnV2",
            None,
            {
                "cdnType": cdn_type,
                "libUrl": lib_url,
                "thumbnailUrl": thumbnail_url,
                "orgAssetType": org_asset_type,
                "defaultOriginAdded": default_origin_added,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def add_to_org_assets_lib_and_cdn_with_type(
        self, cdn_type: int, lib_url: str, thumbnail_url: str, org_asset_type: int
    ) -> Self:
        """AddToOrgAssetsLibAndCdnWithType operation.

        Args:
            cdn_type (int):
                cdnType parameter
            lib_url (str):
                libUrl parameter
            thumbnail_url (str):
                thumbnailUrl parameter
            org_asset_type (int):
                orgAssetType parameter
        """
        qry = ServiceOperationQuery(
            self,
            "AddToOrgAssetsLibAndCdnWithType",
            None,
            {"cdnType": cdn_type, "libUrl": lib_url, "thumbnailUrl": thumbnail_url, "orgAssetType": org_asset_type},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def add_to_org_assets_lib_with_config(
        self,
        cdn_type: int,
        lib_url: str,
        thumbnail_url: str,
        org_asset_type: int,
        default_origin_added: bool,
        config_param: OrgAssetsLibraryConfigParam,
    ) -> Self:
        """AddToOrgAssetsLibWithConfig operation.

        Args:
            cdn_type (int):
                cdnType parameter
            lib_url (str):
                libUrl parameter
            thumbnail_url (str):
                thumbnailUrl parameter
            org_asset_type (int):
                orgAssetType parameter
            default_origin_added (bool):
                defaultOriginAdded parameter
            config_param (OrgAssetsLibraryConfigParam):
                configParam parameter
        """
        qry = ServiceOperationQuery(
            self,
            "AddToOrgAssetsLibWithConfig",
            None,
            {
                "cdnType": cdn_type,
                "libUrl": lib_url,
                "thumbnailUrl": thumbnail_url,
                "orgAssetType": org_asset_type,
                "defaultOriginAdded": default_origin_added,
                "configParam": config_param,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def archive_container(self, container_id: str) -> Self:
        """ArchiveContainer operation.

        Args:
            container_id (str):
                containerId parameter
        """
        qry = ServiceOperationQuery(self, "ArchiveContainer", None, {"containerId": container_id}, None, None)
        self.context.add_query(qry)
        return self

    def bootstrap_policy_automation_resources(self) -> ClientResult[bool]:
        """BootstrapPolicyAutomationResources operation."""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "BootstrapPolicyAutomationResources", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def bulk_remove_resource_as_authoritative(
        self, site_ids: list[UUID]
    ) -> ClientResult[ClientValueCollection[BulkInsertOperationResult]]:
        """BulkRemoveResourceAsAuthoritative operation.

        Args:
            site_ids (list[UUID]):
                siteIds parameter
        """
        from office365.sharepoint.tenant.administration.bulk_insert_operation_result import (
            BulkInsertOperationResult,
        )

        return_type = ClientResult(self.context, ClientValueCollection[BulkInsertOperationResult]())
        qry = ServiceOperationQuery(
            self, "BulkRemoveResourceAsAuthoritative", None, {"siteIds": GuidCollection(site_ids)}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def bulk_set_resource_as_authoritative(
        self, site_ids: list[UUID]
    ) -> ClientResult[ClientValueCollection[BulkInsertOperationResult]]:
        """BulkSetResourceAsAuthoritative operation.

        Args:
            site_ids (list[UUID]):
                siteIds parameter
        """
        from office365.sharepoint.tenant.administration.bulk_insert_operation_result import (
            BulkInsertOperationResult,
        )

        return_type = ClientResult(self.context, ClientValueCollection[BulkInsertOperationResult]())
        qry = ServiceOperationQuery(
            self, "BulkSetResourceAsAuthoritative", None, {"siteIds": GuidCollection(site_ids)}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def clear_pre_auth_allow_deny_list_settings(self, should_clear_allow_list: bool) -> Self:
        """ClearPreAuthAllowDenyListSettings operation.

        Args:
            should_clear_allow_list (bool):
                shouldClearAllowList parameter
        """
        qry = ServiceOperationQuery(
            self,
            "ClearPreAuthAllowDenyListSettings",
            None,
            {"shouldClearAllowList": should_clear_allow_list},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def clear_restricted_access_control_onedrive(self) -> Self:
        """ClearRestrictedAccessControlOneDrive operation."""
        qry = ServiceOperationQuery(self, "ClearRestrictedAccessControlOneDrive", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def clear_restricted_access_control_sharepoint(self) -> Self:
        """ClearRestrictedAccessControlSharePoint operation."""
        qry = ServiceOperationQuery(self, "ClearRestrictedAccessControlSharePoint", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def create_application_billing_policy_validation(self, application_id: str) -> ClientResult[bool]:
        """CreateApplicationBillingPolicyValidation operation.

        Args:
            application_id (str):
                applicationId parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self, "CreateApplicationBillingPolicyValidation", None, {"applicationId": application_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def create_file_archive_policy(
        self,
        policy_name: str,
        policy_type: str,
        months_since_last_access_criteria: int,
        file_type_criteria: list[str],
        is_what_if_mode: bool,
        file_type_exclusion_criteria: list[str],
    ) -> ClientResult[SPOFileArchivePolicyInfo]:
        """CreateFileArchivePolicy operation.

        Args:
            policy_name (str):
                policyName parameter
            policy_type (str):
                policyType parameter
            months_since_last_access_criteria (int):
                monthsSinceLastAccessCriteria parameter
            file_type_criteria (list[str]):
                fileTypeCriteria parameter
            is_what_if_mode (bool):
                isWhatIfMode parameter
            file_type_exclusion_criteria (list[str]):
                fileTypeExclusionCriteria parameter
        """
        from office365.sharepoint.tenantadministration.spo_file_archive_policy_info import (
            SPOFileArchivePolicyInfo,
        )

        return_type = ClientResult(self.context, SPOFileArchivePolicyInfo())
        qry = ServiceOperationQuery(
            self,
            "CreateFileArchivePolicy",
            None,
            {
                "policyName": policy_name,
                "policyType": policy_type,
                "monthsSinceLastAccessCriteria": months_since_last_access_criteria,
                "fileTypeCriteria": StringCollection(file_type_criteria),
                "isWhatIfMode": is_what_if_mode,
                "fileTypeExclusionCriteria": StringCollection(file_type_exclusion_criteria),
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def delete_spo_service_prioritization_app_registration(self, app_id: UUID) -> Self:
        """DeleteSPOServicePrioritizationAppRegistration operation.

        Args:
            app_id (UUID):
                appId parameter
        """
        qry = ServiceOperationQuery(
            self, "DeleteSPOServicePrioritizationAppRegistration", None, {"appId": app_id}, None, None
        )
        self.context.add_query(qry)
        return self

    def delete_spo_service_prioritization_app_registrations_by_policy(self, policy_id: UUID) -> ClientResult[int]:
        """DeleteSPOServicePrioritizationAppRegistrationsByPolicy operation.

        Args:
            policy_id (UUID):
                policyId parameter
        """
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(
            self,
            "DeleteSPOServicePrioritizationAppRegistrationsByPolicy",
            None,
            {"policyId": policy_id},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def delete_syntex_custom_model_setting(self, unique_id: str, scenario: int) -> Self:
        """DeleteSyntexCustomModelSetting operation.

        Args:
            unique_id (str):
                uniqueId parameter
            scenario (int):
                scenario parameter
        """
        qry = ServiceOperationQuery(
            self, "DeleteSyntexCustomModelSetting", None, {"uniqueId": unique_id, "scenario": scenario}, None, None
        )
        self.context.add_query(qry)
        return self

    def download_high_volume_component_impacted_assets_report(self, category: int, document_key: str) -> Self:
        """DownloadHighVolumeComponentImpactedAssetsReport operation.

        Args:
            category (int):
                category parameter
            document_key (str):
                documentKey parameter
        """
        qry = FunctionQuery(self, "DownloadHighVolumeComponentImpactedAssetsReport", [category, document_key], None)
        self.context.add_query(qry)
        return self

    def download_ransomware_impacted_assets_report(self, drive_id: str, file_name: str, report_name_type: int) -> Self:
        """DownloadRansomwareImpactedAssetsReport operation.

        Args:
            drive_id (str):
                driveId parameter
            file_name (str):
                fileName parameter
            report_name_type (int):
                reportNameType parameter
        """
        qry = FunctionQuery(
            self, "DownloadRansomwareImpactedAssetsReport", [drive_id, file_name, report_name_type], None
        )
        self.context.add_query(qry)
        return self

    def download_spo_containers(self, active: bool) -> Self:
        """DownloadSPOContainers operation.

        Args:
            active (bool):
                active parameter
        """
        qry = FunctionQuery(self, "DownloadSPOContainers", [active], None)
        self.context.add_query(qry)
        return self

    def enable_brand_center_public_cdn(self) -> Self:
        """EnableBrandCenterPublicCdn operation."""
        qry = ServiceOperationQuery(self, "EnableBrandCenterPublicCdn", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def enqueue_insights(
        self, insights_scenario: int, report_id: str, report_data_file: str, report_creation_time: datetime
    ) -> ClientResult[InsightsQueueItem]:
        """EnqueueInsights operation.

        Args:
            insights_scenario (int):
                insightsScenario parameter
            report_id (str):
                reportId parameter
            report_data_file (str):
                reportDataFile parameter
            report_creation_time (datetime):
                reportCreationTime parameter
        """
        from office365.sharepoint.tenant.administration.insights.queueitem import (
            InsightsQueueItem,
        )

        return_type = ClientResult(self.context, InsightsQueueItem())
        qry = ServiceOperationQuery(
            self,
            "EnqueueInsights",
            None,
            {
                "insightsScenario": insights_scenario,
                "reportId": report_id,
                "reportDataFile": report_data_file,
                "reportCreationTime": report_creation_time,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def execute_transpiler_request(self, payload: CopilotTranspilerPayload) -> ClientResult[CopilotTranspilerResponse]:
        """ExecuteTranspilerRequest operation.

        Args:
            payload (CopilotTranspilerPayload):
                payload parameter
        """
        from office365.sharepoint.tenant.administration.copilot.transpilerresponse import (
            CopilotTranspilerResponse,
        )

        return_type = ClientResult(self.context, CopilotTranspilerResponse())
        qry = ServiceOperationQuery(self, "ExecuteTranspilerRequest", None, {"payload": payload}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def export_admin_list_to_csv(self, view_xml: str, list_name: str) -> ClientResult[str]:
        """ExportAdminListToCSV operation.

        Args:
            view_xml (str):
                viewXml parameter
            list_name (str):
                listName parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "ExportAdminListToCSV", None, {"viewXml": view_xml, "listName": list_name}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def export_containers_to_csv(self) -> ClientResult[str]:
        """ExportContainersToCSV operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "ExportContainersToCSV", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def export_csv_file(self, time_zone_id: int) -> ClientResult[str]:
        """ExportCSVFile operation.

        Args:
            time_zone_id (int):
                timeZoneId parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "ExportCSVFile", None, {"timeZoneId": time_zone_id}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def export_unlicensed_onedrive_for_business_list_to_csv(self) -> ClientResult[str]:
        """ExportUnlicensedOneDriveForBusinessListToCSV operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "ExportUnlicensedOneDriveForBusinessListToCSV", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_admin_report_data(
        self, feature_id: str, dataset_metadata: ClientValueCollection[DatasetMetadataRequestInfo], query: str
    ) -> ClientResult[bytes]:
        """GetAdminReportData operation.

        Args:
            feature_id (str):
                featureId parameter
            dataset_metadata (ClientValueCollection[DatasetMetadataRequestInfo]):
                datasetMetadata parameter
            query (str):
                query parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self,
            "GetAdminReportData",
            None,
            {"featureId": feature_id, "datasetMetadata": dataset_metadata, "query": query},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_admin_report_data_json(
        self,
        feature_id: str,
        dataset_metadata: ClientValueCollection[DatasetMetadataRequestInfo],
        query: str,
        top_records: int,
    ) -> ClientResult[ReportQueryResponse]:
        """GetAdminReportDataJson operation.

        Args:
            feature_id (str):
                featureId parameter
            dataset_metadata (ClientValueCollection[DatasetMetadataRequestInfo]):
                datasetMetadata parameter
            query (str):
                query parameter
            top_records (int):
                topRecords parameter
        """
        from office365.sharepoint.tenant.administration.report_query_response import (
            ReportQueryResponse,
        )

        return_type = ClientResult(self.context, ReportQueryResponse())
        qry = ServiceOperationQuery(
            self,
            "GetAdminReportDataJson",
            None,
            {"featureId": feature_id, "datasetMetadata": dataset_metadata, "query": query, "topRecords": top_records},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_admin_report_metadata(self, dataset: list[str]) -> ClientResult[DatasetMetadataResponse]:
        """GetAdminReportMetadata operation.

        Args:
            dataset (list[str]):
                dataset parameter
        """
        from office365.sharepoint.tenant.administration.dataset_metadata_response import (
            DatasetMetadataResponse,
        )

        return_type = ClientResult(self.context, DatasetMetadataResponse())
        qry = ServiceOperationQuery(
            self, "GetAdminReportMetadata", None, {"dataset": StringCollection(dataset)}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_all_spo_containers_from_admin_list(
        self, query_params: SPOContainerQueryParams
    ) -> ClientResult[SPContainerCollection]:
        """GetAllSPOContainersFromAdminList operation.

        Args:
            query_params (SPOContainerQueryParams):
                queryParams parameter
        """
        from office365.sharepoint.tenant.administration.container.collection import (
            SPContainerCollection,
        )

        return_type = ClientResult(self.context, SPContainerCollection())
        qry = ServiceOperationQuery(
            self, "GetAllSPOContainersFromAdminList", None, {"queryParams": query_params}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_archivable_container_types(self) -> ClientResult[ClientValueCollection[SPContainerTypeStatus]]:
        """GetArchivableContainerTypes operation."""
        from office365.sharepoint.tenant.administration.container.type.status import (
            SPContainerTypeStatus,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPContainerTypeStatus]())
        qry = ServiceOperationQuery(self, "GetArchivableContainerTypes", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_authoritative_resources(self) -> ClientResult[ClientValueCollection[AuthoritativeResourceProperties]]:
        """GetAuthoritativeResources operation."""
        from office365.sharepoint.tenant.administration.authoritative_resource_properties import (
            AuthoritativeResourceProperties,
        )

        return_type = ClientResult(self.context, ClientValueCollection[AuthoritativeResourceProperties]())
        qry = FunctionQuery(self, "GetAuthoritativeResources", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_baseline_security_mode_pre_auth_settings(self) -> ClientResult[str]:
        """GetBaselineSecurityModePreAuthSettings operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetBaselineSecurityModePreAuthSettings", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_brand_center_configuration(self) -> ClientResult[BrandCenterConfiguration]:
        """GetBrandCenterConfiguration operation."""
        from office365.sharepoint.brandcenter.configuration import (
            BrandCenterConfiguration,
        )

        return_type = ClientResult(self.context, BrandCenterConfiguration())
        qry = FunctionQuery(self, "GetBrandCenterConfiguration", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_catalog_management_schema(self) -> ClientResult[CatalogManagementSchema]:
        """GetCatalogManagementSchema operation."""
        from office365.sharepoint.tenant.administration.catalog_management_schema import (
            CatalogManagementSchema,
        )

        return_type = ClientResult(self.context, CatalogManagementSchema())
        qry = FunctionQuery(self, "GetCatalogManagementSchema", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_catalog_management_settings(self) -> ClientResult[CatalogManagementSettings]:
        """GetCatalogManagementSettings operation."""
        from office365.sharepoint.tenant.administration.catalog_management_settings import (
            CatalogManagementSettings,
        )

        return_type = ClientResult(self.context, CatalogManagementSettings())
        qry = FunctionQuery(self, "GetCatalogManagementSettings", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_catalog_management_status(self) -> ClientResult[CatalogManagementStatus]:
        """GetCatalogManagementStatus operation."""
        from office365.sharepoint.tenant.administration.catalog_management_status import (
            CatalogManagementStatus,
        )

        return_type = ClientResult(self.context, CatalogManagementStatus())
        qry = FunctionQuery(self, "GetCatalogManagementStatus", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_container_type_exists(self, billing_type: int) -> ClientResult[bool]:
        """GetContainerTypeExists operation.

        Args:
            billing_type (int):
                billingType parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self, "GetContainerTypeExists", None, {"billingType": billing_type}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_content_management_assessment_results(self) -> ClientResult[ContentManagementAssessmentResults]:
        """GetContentManagementAssessmentResults operation."""
        from office365.sharepoint.tenant.administration.contentmanagementassessmentresults import (
            ContentManagementAssessmentResults,
        )

        return_type = ClientResult(self.context, ContentManagementAssessmentResults())
        qry = FunctionQuery(self, "GetContentManagementAssessmentResults", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_copilot_promo_opt_in_status(self) -> ClientResult[bool]:
        """GetCopilotPromoOptInStatus operation."""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "GetCopilotPromoOptInStatus", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_file_archive_policies(
        self, policy_id: UUID
    ) -> ClientResult[ClientValueCollection[SPOFileArchivePolicyInfo]]:
        """GetFileArchivePolicies operation.

        Args:
            policy_id (UUID):
                policyId parameter
        """
        from office365.sharepoint.tenantadministration.spo_file_archive_policy_info import (
            SPOFileArchivePolicyInfo,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPOFileArchivePolicyInfo]())
        qry = ServiceOperationQuery(self, "GetFileArchivePolicies", None, {"policyId": policy_id}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_file_archive_policy_reports(
        self, policy_id: UUID
    ) -> ClientResult[ClientValueCollection[SPOFileArchivePolicyReportInfo]]:
        """GetFileArchivePolicyReports operation.

        Args:
            policy_id (UUID):
                policyId parameter
        """
        from office365.sharepoint.tenantadministration.spo_file_archive_policy_report_info import (
            SPOFileArchivePolicyReportInfo,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPOFileArchivePolicyReportInfo]())
        qry = ServiceOperationQuery(
            self, "GetFileArchivePolicyReports", None, {"policyId": policy_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_file_archive_policy_sites(
        self, policy_id: UUID
    ) -> ClientResult[ClientValueCollection[SPOFileArchivePolicySiteInfo]]:
        """GetFileArchivePolicySites operation.

        Args:
            policy_id (UUID):
                policyId parameter
        """
        from office365.sharepoint.tenantadministration.spo_file_archive_policy_site_info import (
            SPOFileArchivePolicySiteInfo,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPOFileArchivePolicySiteInfo]())
        qry = ServiceOperationQuery(self, "GetFileArchivePolicySites", None, {"policyId": policy_id}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_file_request_branding_profiles(self) -> ClientResult[FileRequestBrandingAssetConfig]:
        """GetFileRequestBrandingProfiles operation."""
        from office365.sharepoint.administration.filerequestbrandingassetconfig import (
            FileRequestBrandingAssetConfig,
        )

        return_type = ClientResult(self.context, FileRequestBrandingAssetConfig())
        qry = FunctionQuery(self, "GetFileRequestBrandingProfiles", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_file_version_batch_delete_job_progress(self, site_url: str) -> ClientResult[str]:
        """GetFileVersionBatchDeleteJobProgress operation.

        Args:
            site_url (str):
                siteUrl parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "GetFileVersionBatchDeleteJobProgress", None, {"siteUrl": site_url}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_file_version_expiration_report_job_progress(self, site_url: str, report_url: str) -> ClientResult[str]:
        """GetFileVersionExpirationReportJobProgress operation.

        Args:
            site_url (str):
                siteUrl parameter
            report_url (str):
                reportUrl parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "GetFileVersionExpirationReportJobProgress",
            None,
            {"siteUrl": site_url, "reportUrl": report_url},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_file_version_expiration_report_job_progress_for_library(
        self, site_url: str, list_params: SPOListParameters, report_url: str
    ) -> ClientResult[SPOFileVersionExpirationReportJobProgress]:
        """GetFileVersionExpirationReportJobProgressForLibrary operation.

        Args:
            site_url (str):
                siteUrl parameter
            list_params (SPOListParameters):
                listParams parameter
            report_url (str):
                reportUrl parameter
        """
        from office365.sharepoint.tenant.administration.spofileversionexpirationreportjobprogress import (
            SPOFileVersionExpirationReportJobProgress,
        )

        return_type = ClientResult(self.context, SPOFileVersionExpirationReportJobProgress())
        qry = ServiceOperationQuery(
            self,
            "GetFileVersionExpirationReportJobProgressForLibrary",
            None,
            {"siteUrl": site_url, "listParams": list_params, "reportUrl": report_url},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_generated_insights_summary(
        self, insights_scenario: int, data_file_name: str, page_index: int
    ) -> ClientResult[InsightsSummaryResponse]:
        """GetGeneratedInsightsSummary operation.

        Args:
            insights_scenario (int):
                insightsScenario parameter
            data_file_name (str):
                dataFileName parameter
            page_index (int):
                pageIndex parameter
        """
        from office365.sharepoint.tenant.administration.insights.summary_response import (
            InsightsSummaryResponse,
        )

        return_type = ClientResult(self.context, InsightsSummaryResponse())
        qry = ServiceOperationQuery(
            self,
            "GetGeneratedInsightsSummary",
            None,
            {"insightsScenario": insights_scenario, "dataFileName": data_file_name, "pageIndex": page_index},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_ib_version_for_tenant(self) -> ClientResult[str]:
        """GetIBVersionForTenant operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetIBVersionForTenant", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_idle_session_sign_out_for_unmanaged_devices(self) -> ClientResult[str]:
        """GetIdleSessionSignOutForUnmanagedDevices operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetIdleSessionSignOutForUnmanagedDevices", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_insights_summary(
        self,
        insights_scenario: int,
        data_file_name: str,
        page_index: int,
        model_name: str,
        max_token_size: int,
        max_content_size: int,
        timeout_ms: int,
    ) -> ClientResult[InsightsSummaryResponse]:
        """GetInsightsSummary operation.

        Args:
            insights_scenario (int):
                insightsScenario parameter
            data_file_name (str):
                dataFileName parameter
            page_index (int):
                pageIndex parameter
            model_name (str):
                modelName parameter
            max_token_size (int):
                maxTokenSize parameter
            max_content_size (int):
                maxContentSize parameter
            timeout_ms (int):
                timeoutMS parameter
        """
        from office365.sharepoint.tenant.administration.insights.summary_response import (
            InsightsSummaryResponse,
        )

        return_type = ClientResult(self.context, InsightsSummaryResponse())
        qry = ServiceOperationQuery(
            self,
            "GetInsightsSummary",
            None,
            {
                "insightsScenario": insights_scenario,
                "dataFileName": data_file_name,
                "pageIndex": page_index,
                "modelName": model_name,
                "maxTokenSize": max_token_size,
                "maxContentSize": max_content_size,
                "timeoutMS": timeout_ms,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_manage_version_policy_job_progress(self, site_url: str) -> ClientResult[str]:
        """GetManageVersionPolicyJobProgress operation.

        Args:
            site_url (str):
                siteUrl parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "GetManageVersionPolicyJobProgress", None, {"siteUrl": site_url}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_org_assets(self) -> ClientResult[OrgAssets]:
        """GetOrgAssets operation."""
        from office365.sharepoint.administration.orgassets.org_assets import OrgAssets

        return_type = ClientResult(self.context, OrgAssets())
        qry = FunctionQuery(self, "GetOrgAssets", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_pre_auth_settings(self) -> ClientResult[str]:
        """GetPreAuthSettings operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetPreAuthSettings", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_ransomware_activities_overview(self, event_id: str) -> ClientResult[TenantAdminRansomwareActivitiesOverview]:
        """GetRansomwareActivitiesOverview operation.

        Args:
            event_id (str):
                eventId parameter
        """
        from office365.sharepoint.tenant.administration.ransomware.activitiesoverview import (
            TenantAdminRansomwareActivitiesOverview,
        )

        return_type = ClientResult(self.context, TenantAdminRansomwareActivitiesOverview())
        qry = ServiceOperationQuery(
            self, "GetRansomwareActivitiesOverview", None, {"eventId": event_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_ransomware_events(self, parameters: RenderListDataParameters) -> ClientResult[bytes]:
        """GetRansomwareEvents operation.

        Args:
            parameters (RenderListDataParameters):
                parameters parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(self, "GetRansomwareEvents", None, {"parameters": parameters}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_ransomware_site_restore_points(self, parameters: RenderListDataParameters) -> ClientResult[bytes]:
        """GetRansomwareSiteRestorePoints operation.

        Args:
            parameters (RenderListDataParameters):
                parameters parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self, "GetRansomwareSiteRestorePoints", None, {"parameters": parameters}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_sharepoint_setting_data(self, category: int) -> ClientResult[ClientValueCollection[SettingDataProperty]]:
        """GetSharePointSettingData operation.

        Args:
            category (int):
                category parameter
        """
        from office365.sharepoint.tenant.administration.settings.dataproperty import (
            SettingDataProperty,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SettingDataProperty]())
        qry = ServiceOperationQuery(self, "GetSharePointSettingData", None, {"category": category}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_site_cohorts_summary(self, view: str) -> ClientResult[SiteCohortsSummary]:
        """GetSiteCohortsSummary operation.

        Args:
            view (str):
                view parameter
        """
        from office365.sharepoint.tenant.administration.sitecohortssummary import (
            SiteCohortsSummary,
        )

        return_type = ClientResult(self.context, SiteCohortsSummary())
        qry = ServiceOperationQuery(self, "GetSiteCohortsSummary", None, {"view": view}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_sites_from_substrate(self, search_text: str) -> ClientResult[str]:
        """GetSitesFromSubstrate operation.

        Args:
            search_text (str):
                searchText parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetSitesFromSubstrate", None, {"searchText": search_text}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_sorted_spo_containers_by_application_id(
        self, owning_application_id: UUID, ascending: bool, paged: bool, paging_token: str, archive_status: int
    ) -> ClientResult[SPContainerCollection]:
        """GetSortedSPOContainersByApplicationId operation.

        Args:
            owning_application_id (UUID):
                owningApplicationId parameter
            ascending (bool):
                ascending parameter
            paged (bool):
                paged parameter
            paging_token (str):
                pagingToken parameter
            archive_status (int):
                archiveStatus parameter
        """
        from office365.sharepoint.tenant.administration.container.collection import (
            SPContainerCollection,
        )

        return_type = ClientResult(self.context, SPContainerCollection())
        qry = ServiceOperationQuery(
            self,
            "GetSortedSPOContainersByApplicationId",
            None,
            {
                "owningApplicationId": owning_application_id,
                "ascending": ascending,
                "paged": paged,
                "pagingToken": paging_token,
                "archiveStatus": archive_status,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_sph_site_url(self) -> ClientResult[str]:
        """GetSPHSiteUrl operation."""
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "GetSPHSiteUrl", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_spo_container_by_container_id(self, container_id: str) -> ClientResult[SPContainerProperties]:
        """GetSPOContainerByContainerId operation.

        Args:
            container_id (str):
                containerId parameter
        """
        from office365.sharepoint.tenant.administration.container.properties import (
            SPContainerProperties,
        )

        return_type = ClientResult(self.context, SPContainerProperties())
        qry = ServiceOperationQuery(
            self, "GetSPOContainerByContainerId", None, {"containerId": container_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_spo_container_by_container_site_url(self, container_site_url: str) -> ClientResult[SPContainerProperties]:
        """GetSPOContainerByContainerSiteUrl operation.

        Args:
            container_site_url (str):
                containerSiteUrl parameter
        """
        from office365.sharepoint.tenant.administration.container.properties import (
            SPContainerProperties,
        )

        return_type = ClientResult(self.context, SPContainerProperties())
        qry = ServiceOperationQuery(
            self, "GetSPOContainerByContainerSiteUrl", None, {"containerSiteUrl": container_site_url}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_spo_containers_by_application_id(
        self, owning_application_id: UUID, paged: bool, paging_token: str, archive_status: int
    ) -> ClientResult[SPContainerCollection]:
        """GetSPOContainersByApplicationId operation.

        Args:
            owning_application_id (UUID):
                owningApplicationId parameter
            paged (bool):
                paged parameter
            paging_token (str):
                pagingToken parameter
            archive_status (int):
                archiveStatus parameter
        """
        from office365.sharepoint.tenant.administration.container.collection import (
            SPContainerCollection,
        )

        return_type = ClientResult(self.context, SPContainerCollection())
        qry = ServiceOperationQuery(
            self,
            "GetSPOContainersByApplicationId",
            None,
            {
                "owningApplicationId": owning_application_id,
                "paged": paged,
                "pagingToken": paging_token,
                "archiveStatus": archive_status,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_spo_container_type_by_id(
        self, container_type_id: UUID, container_tenant_type: int
    ) -> ClientResult[SPContainerTypeProperties]:
        """GetSPOContainerTypeById operation.

        Args:
            container_type_id (UUID):
                containerTypeId parameter
            container_tenant_type (int):
                containerTenantType parameter
        """
        from office365.sharepoint.tenant.administration.container.type.properties import (
            SPContainerTypeProperties,
        )

        return_type = ClientResult(self.context, SPContainerTypeProperties())
        qry = ServiceOperationQuery(
            self,
            "GetSPOContainerTypeById",
            None,
            {"containerTypeId": container_type_id, "containerTenantType": container_tenant_type},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_spo_container_type_configuration_by_container_type_id(
        self, container_type_id: UUID
    ) -> ClientResult[SPContainerTypeConfigurationProperties]:
        """GetSPOContainerTypeConfigurationByContainerTypeId operation.

        Args:
            container_type_id (UUID):
                containerTypeId parameter
        """
        from office365.sharepoint.tenant.administration.container.type.configurationproperties import (
            SPContainerTypeConfigurationProperties,
        )

        return_type = ClientResult(self.context, SPContainerTypeConfigurationProperties())
        qry = ServiceOperationQuery(
            self,
            "GetSPOContainerTypeConfigurationByContainerTypeId",
            None,
            {"containerTypeId": container_type_id},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_spo_container_types(
        self, container_tenant_type: int
    ) -> ClientResult[ClientValueCollection[SPContainerTypeProperties]]:
        """GetSPOContainerTypes operation.

        Args:
            container_tenant_type (int):
                containerTenantType parameter
        """
        from office365.sharepoint.tenant.administration.container.type.properties import (
            SPContainerTypeProperties,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPContainerTypeProperties]())
        qry = ServiceOperationQuery(
            self, "GetSPOContainerTypes", None, {"containerTenantType": container_tenant_type}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_spo_deleted_containers(self) -> ClientResult[ClientValueCollection[SPDeletedContainerProperties]]:
        """GetSPODeletedContainers operation."""
        from office365.sharepoint.tenant.administration.spdeletedcontainerproperties import (
            SPDeletedContainerProperties,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPDeletedContainerProperties]())
        qry = ServiceOperationQuery(self, "GetSPODeletedContainers", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_spo_restricted_search_allowed_list(self) -> ClientResult[StringCollection]:
        """GetSPORestrictedSearchAllowedList operation."""
        return_type = ClientResult(self.context, StringCollection())
        qry = ServiceOperationQuery(self, "GetSPORestrictedSearchAllowedList", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_spo_restricted_search_mode(self) -> ClientResult[int]:
        """GetSPORestrictedSearchMode operation."""
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(self, "GetSPORestrictedSearchMode", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_spo_service_prioritization_app_registrations(self) -> ClientResult[SPOServicePrioritizationAppRegistrations]:
        """GetSPOServicePrioritizationAppRegistrations operation."""
        from office365.sharepoint.tenant.administration.sposerviceprioritizationappregistrations import (
            SPOServicePrioritizationAppRegistrations,
        )

        return_type = ClientResult(self.context, SPOServicePrioritizationAppRegistrations())
        qry = ServiceOperationQuery(self, "GetSPOServicePrioritizationAppRegistrations", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_spo_service_prioritization_app_registrations_by_policy(
        self, policy_id: UUID
    ) -> ClientResult[SPOServicePrioritizationAppRegistrations]:
        """GetSPOServicePrioritizationAppRegistrationsByPolicy operation.

        Args:
            policy_id (UUID):
                policyId parameter
        """
        from office365.sharepoint.tenant.administration.sposerviceprioritizationappregistrations import (
            SPOServicePrioritizationAppRegistrations,
        )

        return_type = ClientResult(self.context, SPOServicePrioritizationAppRegistrations())
        qry = ServiceOperationQuery(
            self, "GetSPOServicePrioritizationAppRegistrationsByPolicy", None, {"policyId": policy_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_spo_service_prioritization_billing_payload(
        self,
        billing_policy_id: str,
        azure_subscription_id: UUID,
        resource_group: str,
        azure_region: str,
        friendly_name: str,
    ) -> ClientResult[SPOServicePrioritizationBillingPayload]:
        """GetSPOServicePrioritizationBillingPayload operation.

        Args:
            billing_policy_id (str):
                billingPolicyId parameter
            azure_subscription_id (UUID):
                azureSubscriptionId parameter
            resource_group (str):
                resourceGroup parameter
            azure_region (str):
                azureRegion parameter
            friendly_name (str):
                friendlyName parameter
        """
        from office365.sharepoint.tenant.administration.sposerviceprioritizationbillingpayload import (
            SPOServicePrioritizationBillingPayload,
        )

        return_type = ClientResult(self.context, SPOServicePrioritizationBillingPayload())
        qry = ServiceOperationQuery(
            self,
            "GetSPOServicePrioritizationBillingPayload",
            None,
            {
                "billingPolicyId": billing_policy_id,
                "azureSubscriptionId": azure_subscription_id,
                "resourceGroup": resource_group,
                "azureRegion": azure_region,
                "friendlyName": friendly_name,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_spo_service_prioritization_billing_policies(
        self,
    ) -> ClientResult[ClientValueCollection[SPOServicePrioritizationPolicyFromTenantStore]]:
        """GetSPOServicePrioritizationBillingPolicies operation."""
        from office365.sharepoint.tenant.administration.sposerviceprioritizationpolicyfromtenantstore import (
            SPOServicePrioritizationPolicyFromTenantStore,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPOServicePrioritizationPolicyFromTenantStore]())
        qry = ServiceOperationQuery(self, "GetSPOServicePrioritizationBillingPolicies", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_spo_site_creation_sources(self) -> ClientResult[ClientValueCollection[SPOSiteCreationSource]]:
        """GetSPOSiteCreationSources operation."""
        from office365.sharepoint.tenant.administration.spositecreationsource import (
            SPOSiteCreationSource,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPOSiteCreationSource]())
        qry = FunctionQuery(self, "GetSPOSiteCreationSources", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_spo_syntex_applications(self) -> ClientResult[ClientValueCollection[SPSyntexApplicationProperties]]:
        """GetSPOSyntexApplications operation."""
        from office365.sharepoint.tenant.administration.syntex.applicationproperties import (
            SPSyntexApplicationProperties,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPSyntexApplicationProperties]())
        qry = ServiceOperationQuery(self, "GetSPOSyntexApplications", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_spo_syntex_consuming_applications(
        self, owning_application_id: UUID, application_id: UUID
    ) -> ClientResult[SPSyntexApplicationProperties]:
        """GetSPOSyntexConsumingApplications operation.

        Args:
            owning_application_id (UUID):
                owningApplicationId parameter
            application_id (UUID):
                applicationId parameter
        """
        from office365.sharepoint.tenant.administration.syntex.applicationproperties import (
            SPSyntexApplicationProperties,
        )

        return_type = ClientResult(self.context, SPSyntexApplicationProperties())
        qry = ServiceOperationQuery(
            self,
            "GetSPOSyntexConsumingApplications",
            None,
            {"owningApplicationId": owning_application_id, "applicationId": application_id},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_syntex_custom_model_settings(
        self, scenario: int
    ) -> ClientResult[ClientValueCollection[SyntexCustomModelSetting]]:
        """GetSyntexCustomModelSettings operation.

        Args:
            scenario (int):
                scenario parameter
        """
        from office365.sharepoint.viva.syntexcustommodelsetting import (
            SyntexCustomModelSetting,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SyntexCustomModelSetting]())
        qry = FunctionQuery(self, "GetSyntexCustomModelSettings", [scenario], return_type)
        self.context.add_query(qry)
        return return_type

    def get_targeted_sites_details(self) -> ClientResult[ClientValueCollection[TargetedSiteDetails]]:
        """GetTargetedSitesDetails operation."""
        from office365.sharepoint.viva.targetedsitedetails import TargetedSiteDetails

        return_type = ClientResult(self.context, ClientValueCollection[TargetedSiteDetails]())
        qry = FunctionQuery(self, "GetTargetedSitesDetails", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_targeted_sites_details_by_user_id(
        self, user_id: str
    ) -> ClientResult[ClientValueCollection[TargetedSiteDetails]]:
        """GetTargetedSitesDetailsByUserId operation.

        Args:
            user_id (str):
                userId parameter
        """
        from office365.sharepoint.viva.targetedsitedetails import TargetedSiteDetails

        return_type = ClientResult(self.context, ClientValueCollection[TargetedSiteDetails]())
        qry = FunctionQuery(self, "GetTargetedSitesDetailsByUserId", [user_id], return_type)
        self.context.add_query(qry)
        return return_type

    def get_tenant_all_or_compatible_ib_segments(
        self, segments: list[UUID]
    ) -> ClientResult[ClientValueCollection[IBSegmentInfo]]:
        """GetTenantAllOrCompatibleIBSegments operation.

        Args:
            segments (list[UUID]):
                segments parameter
        """
        from office365.sharepoint.tenant.administration.ibsegmentinfo import (
            IBSegmentInfo,
        )

        return_type = ClientResult(self.context, ClientValueCollection[IBSegmentInfo]())
        qry = FunctionQuery(self, "GetTenantAllOrCompatibleIBSegments", [GuidCollection(segments)], return_type)
        self.context.add_query(qry)
        return return_type

    def get_tenant_apply_file_version_policy_job_progress(self) -> ClientResult[str]:
        """GetTenantApplyFileVersionPolicyJobProgress operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetTenantApplyFileVersionPolicyJobProgress", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_tenant_send_from_address(self) -> ClientResult[str]:
        """GetTenantSendFromAddress operation."""
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "GetTenantSendFromAddress", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_tenant_site_creation_source(self) -> ClientResult[SiteCreationSource]:
        """GetTenantSiteCreationSource operation."""
        from office365.sharepoint.tenant.administration.sites.creation_source import (
            SiteCreationSource,
        )

        return_type = ClientResult(self.context, SiteCreationSource())
        qry = FunctionQuery(self, "GetTenantSiteCreationSource", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_track_view_feature_always_visible(self) -> ClientResult[bool]:
        """GetTrackViewFeatureAlwaysVisible operation."""
        return_type = ClientResult(self.context, bool())
        qry = FunctionQuery(self, "GetTrackViewFeatureAlwaysVisible", [], return_type)
        self.context.add_query(qry)
        return return_type

    def get_use_graph_url_settings(self) -> ClientResult[str]:
        """GetUseGraphUrlSettings operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "GetUseGraphUrlSettings", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_version_policy_for_doc_libs_job_progress(self, site_url: str) -> ClientResult[str]:
        """GetVersionPolicyForDocLibsJobProgress operation.

        Args:
            site_url (str):
                siteUrl parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "GetVersionPolicyForDocLibsJobProgress", None, {"siteUrl": site_url}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_version_policy_impact(
        self, version_policy: SPOFileVersionPolicySettings
    ) -> ClientResult[SPOTenantVersionPolicyImpact]:
        """GetVersionPolicyImpact operation.

        Args:
            version_policy (SPOFileVersionPolicySettings):
                versionPolicy parameter
        """
        from office365.sharepoint.tenant.administration.spo_tenant_version_policy_impact import (
            SPOTenantVersionPolicyImpact,
        )

        return_type = ClientResult(self.context, SPOTenantVersionPolicyImpact())
        qry = ServiceOperationQuery(
            self, "GetVersionPolicyImpact", None, {"versionPolicy": version_policy}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def get_viva_connections_license(self) -> ClientResult[VivaConnectionsLicense]:
        """GetVivaConnectionsLicense operation."""
        from office365.sharepoint.viva.connections.license import VivaConnectionsLicense

        return_type = ClientResult(self.context, VivaConnectionsLicense())
        qry = FunctionQuery(self, "GetVivaConnectionsLicense", [], return_type)
        self.context.add_query(qry)
        return return_type

    def log_sharepoint_embedded_client_log(self, log_properties: SharePointEmbeddedClientLogProperties) -> Self:
        """LogSharePointEmbeddedClientLog operation.

        Args:
            log_properties (SharePointEmbeddedClientLogProperties):
                logProperties parameter
        """
        qry = ServiceOperationQuery(
            self, "LogSharePointEmbeddedClientLog", None, {"logProperties": log_properties}, None, None
        )
        self.context.add_query(qry)
        return self

    def new_spo_container_type(
        self, container_type_properties: SPContainerTypeProperties
    ) -> ClientResult[SPContainerTypeProperties]:
        """NewSPOContainerType operation.

        Args:
            container_type_properties (SPContainerTypeProperties):
                containerTypeProperties parameter
        """
        from office365.sharepoint.tenant.administration.container.type.properties import (
            SPContainerTypeProperties,
        )

        return_type = ClientResult(self.context, SPContainerTypeProperties())
        qry = ServiceOperationQuery(
            self, "NewSPOContainerType", None, {"containerTypeProperties": container_type_properties}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def purge_container(self, container_id: str) -> Self:
        """PurgeContainer operation.

        Args:
            container_id (str):
                containerId parameter
        """
        qry = ServiceOperationQuery(self, "PurgeContainer", None, {"containerId": container_id}, None, None)
        self.context.add_query(qry)
        return self

    def purge_spo_deleted_container_by_container_id(self, container_id: str) -> ClientResult[bool]:
        """PurgeSPODeletedContainerByContainerId operation.

        Args:
            container_id (str):
                containerId parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self, "PurgeSPODeletedContainerByContainerId", None, {"containerId": container_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def purge_spo_deleted_container_by_container_site_url(self, container_site_url: str) -> ClientResult[bool]:
        """PurgeSPODeletedContainerByContainerSiteUrl operation.

        Args:
            container_site_url (str):
                containerSiteUrl parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self,
            "PurgeSPODeletedContainerByContainerSiteUrl",
            None,
            {"containerSiteUrl": container_site_url},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def recent_admin_action_report_is_audit_enabled(self) -> ClientResult[bool]:
        """RecentAdminActionReportIsAuditEnabled operation."""
        return_type = ClientResult(self.context, bool())
        qry = FunctionQuery(self, "RecentAdminActionReportIsAuditEnabled", [], return_type)
        self.context.add_query(qry)
        return return_type

    def remove_container(self, container_id: str) -> Self:
        """RemoveContainer operation.

        Args:
            container_id (str):
                containerId parameter
        """
        qry = ServiceOperationQuery(self, "RemoveContainer", None, {"containerId": container_id}, None, None)
        self.context.add_query(qry)
        return self

    def remove_file_archive_policy(self, policy_id: UUID) -> Self:
        """RemoveFileArchivePolicy operation.

        Args:
            policy_id (UUID):
                policyId parameter
        """
        qry = ServiceOperationQuery(self, "RemoveFileArchivePolicy", None, {"policyId": policy_id}, None, None)
        self.context.add_query(qry)
        return self

    def remove_file_request_branding_profile(self, profile_type: int) -> Self:
        """RemoveFileRequestBrandingProfile operation.

        Args:
            profile_type (int):
                profileType parameter
        """
        qry = ServiceOperationQuery(
            self, "RemoveFileRequestBrandingProfile", None, {"profileType": profile_type}, None, None
        )
        self.context.add_query(qry)
        return self

    def remove_file_type_version_policy(self, file_types: list[str]) -> Self:
        """RemoveFileTypeVersionPolicy operation.

        Args:
            file_types (list[str]):
                fileTypes parameter
        """
        qry = ServiceOperationQuery(
            self, "RemoveFileTypeVersionPolicy", None, {"fileTypes": StringCollection(file_types)}, None, None
        )
        self.context.add_query(qry)
        return self

    def remove_from_org_assets(self, lib_url: str, list_id: UUID) -> Self:
        """RemoveFromOrgAssets operation.

        Args:
            lib_url (str):
                libUrl parameter
            list_id (UUID):
                listId parameter
        """
        qry = ServiceOperationQuery(
            self, "RemoveFromOrgAssets", None, {"libUrl": lib_url, "listId": list_id}, None, None
        )
        self.context.add_query(qry)
        return self

    def remove_pre_auth_allow_deny_list_item_setting(self, item_id: str) -> Self:
        """RemovePreAuthAllowDenyListItemSetting operation.

        Args:
            item_id (str):
                itemId parameter
        """
        qry = ServiceOperationQuery(self, "RemovePreAuthAllowDenyListItemSetting", None, {"itemId": item_id}, None, None)
        self.context.add_query(qry)
        return self

    def remove_resource_as_authoritative(self, site_id: UUID) -> Self:
        """RemoveResourceAsAuthoritative operation.

        Args:
            site_id (UUID):
                siteId parameter
        """
        qry = ServiceOperationQuery(self, "RemoveResourceAsAuthoritative", None, {"siteId": site_id}, None, None)
        self.context.add_query(qry)
        return self

    def remove_site_from_file_archive_policy(self, policy_id: UUID, site_url: str) -> Self:
        """RemoveSiteFromFileArchivePolicy operation.

        Args:
            policy_id (UUID):
                policyId parameter
            site_url (str):
                siteUrl parameter
        """
        qry = ServiceOperationQuery(
            self, "RemoveSiteFromFileArchivePolicy", None, {"policyId": policy_id, "siteUrl": site_url}, None, None
        )
        self.context.add_query(qry)
        return self

    def remove_sph_site(self) -> ClientResult[str]:
        """RemoveSPHSite operation."""
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "RemoveSPHSite", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def remove_sp_list_item(self, list_item_id: int, list_name: str) -> Self:
        """RemoveSPListItem operation.

        Args:
            list_item_id (int):
                listItemId parameter
            list_name (str):
                listName parameter
        """
        qry = ServiceOperationQuery(
            self, "RemoveSPListItem", None, {"listItemId": list_item_id, "listName": list_name}, None, None
        )
        self.context.add_query(qry)
        return self

    def remove_spo_container_by_container_id(self, container_id: str) -> Self:
        """RemoveSPOContainerByContainerId operation.

        Args:
            container_id (str):
                containerId parameter
        """
        qry = ServiceOperationQuery(
            self, "RemoveSPOContainerByContainerId", None, {"containerId": container_id}, None, None
        )
        self.context.add_query(qry)
        return self

    def remove_spo_container_by_container_site_url(self, container_site_url: str) -> Self:
        """RemoveSPOContainerByContainerSiteUrl operation.

        Args:
            container_site_url (str):
                containerSiteUrl parameter
        """
        qry = ServiceOperationQuery(
            self, "RemoveSPOContainerByContainerSiteUrl", None, {"containerSiteUrl": container_site_url}, None, None
        )
        self.context.add_query(qry)
        return self

    def remove_spo_container_type(self, sp_deleted_container_type_properties: SPDeletedContainerTypeProperties) -> Self:
        """RemoveSPOContainerType operation.

        Args:
            sp_deleted_container_type_properties (SPDeletedContainerTypeProperties):
                spDeletedContainerTypeProperties parameter
        """
        qry = ServiceOperationQuery(
            self,
            "RemoveSPOContainerType",
            None,
            {"spDeletedContainerTypeProperties": sp_deleted_container_type_properties},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def remove_spo_container_user_role(self, container_id: str, login_name: str, role: str) -> Self:
        """RemoveSPOContainerUserRole operation.

        Args:
            container_id (str):
                ContainerId parameter
            login_name (str):
                loginName parameter
            role (str):
                role parameter
        """
        qry = ServiceOperationQuery(
            self,
            "RemoveSPOContainerUserRole",
            None,
            {"ContainerId": container_id, "loginName": login_name, "role": role},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def remove_spo_restricted_search_allowed_list(self, site_urls: list[str]) -> Self:
        """RemoveSPORestrictedSearchAllowedList operation.

        Args:
            site_urls (list[str]):
                siteUrls parameter
        """
        qry = ServiceOperationQuery(
            self, "RemoveSPORestrictedSearchAllowedList", None, {"siteUrls": StringCollection(site_urls)}, None, None
        )
        self.context.add_query(qry)
        return self

    def remove_targeted_site(self, site_id: UUID) -> Self:
        """RemoveTargetedSite operation.

        Args:
            site_id (UUID):
                siteId parameter
        """
        qry = ServiceOperationQuery(self, "RemoveTargetedSite", None, {"siteId": site_id}, None, None)
        self.context.add_query(qry)
        return self

    def remove_tenant_admin_list_view(self, view_id: str) -> Self:
        """RemoveTenantAdminListView operation.

        Args:
            view_id (str):
                viewId parameter
        """
        qry = ServiceOperationQuery(self, "RemoveTenantAdminListView", None, {"viewId": view_id}, None, None)
        self.context.add_query(qry)
        return self

    def render_active_containers(self, container_id: str, view_xml: str) -> ClientResult[bytes]:
        """RenderActiveContainers operation.

        Args:
            container_id (str):
                containerId parameter
            view_xml (str):
                viewXml parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self, "RenderActiveContainers", None, {"containerId": container_id, "viewXml": view_xml}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def render_admin_list_data(
        self, parameters: RenderListDataParameters, override_parameters: RenderListDataOverrideParameters, list_name: str
    ) -> ClientResult[bytes]:
        """RenderAdminListData operation.

        Args:
            parameters (RenderListDataParameters):
                parameters parameter
            override_parameters (RenderListDataOverrideParameters):
                overrideParameters parameter
            list_name (str):
                listName parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self,
            "RenderAdminListData",
            None,
            {"parameters": parameters, "overrideParameters": override_parameters, "listName": list_name},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def render_containers_admin_applications_data(
        self,
    ) -> ClientResult[ClientValueCollection[SPContainerApplicationProperties]]:
        """RenderContainersAdminApplicationsData operation."""
        from office365.sharepoint.tenant.administration.container.applicationproperties import (
            SPContainerApplicationProperties,
        )

        return_type = ClientResult(self.context, ClientValueCollection[SPContainerApplicationProperties]())
        qry = ServiceOperationQuery(self, "RenderContainersAdminApplicationsData", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def render_containers_admin_list_data(
        self,
        order_by_columns_list: ClientValueCollection[SPContainerSortOrder],
        filter_by_columns_list: ClientValueCollection[SPContainerFilterOrder],
        page_size: int,
        paging_token: str,
        container_status: str,
        search_parameters: SPContainerSearchParameters,
    ) -> ClientResult[bytes]:
        """RenderContainersAdminListData operation.

        Args:
            order_by_columns_list (ClientValueCollection[SPContainerSortOrder]):
                orderByColumnsList parameter
            filter_by_columns_list (ClientValueCollection[SPContainerFilterOrder]):
                filterByColumnsList parameter
            page_size (int):
                pageSize parameter
            paging_token (str):
                pagingToken parameter
            container_status (str):
                containerStatus parameter
            search_parameters (SPContainerSearchParameters):
                searchParameters parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self,
            "RenderContainersAdminListData",
            None,
            {
                "orderByColumnsList": order_by_columns_list,
                "filterByColumnsList": filter_by_columns_list,
                "pageSize": page_size,
                "pagingToken": paging_token,
                "containerStatus": container_status,
                "searchParameters": search_parameters,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def render_deleted_containers(self, view_xml: str) -> ClientResult[bytes]:
        """RenderDeletedContainers operation.

        Args:
            view_xml (str):
                viewXml parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(self, "RenderDeletedContainers", None, {"viewXml": view_xml}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def render_filtered_admin_list_data(
        self, parameters: RenderListFilterDataParameters, list_name: str
    ) -> ClientResult[bytes]:
        """RenderFilteredAdminListData operation.

        Args:
            parameters (RenderListFilterDataParameters):
                parameters parameter
            list_name (str):
                listName parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self,
            "RenderFilteredAdminListData",
            None,
            {"parameters": parameters, "listName": list_name},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def render_filtered_admin_list_data_by_group_id(self, group_id: UUID) -> ClientResult[bytes]:
        """RenderFilteredAdminListDataByGroupId operation.

        Args:
            group_id (UUID):
                groupId parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self, "RenderFilteredAdminListDataByGroupId", None, {"groupId": group_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def render_governance_hub_sp_list(
        self, parameters: RenderListDataParameters, override_parameters: RenderListDataOverrideParameters
    ) -> ClientResult[bytes]:
        """RenderGovernanceHubSPList operation.

        Args:
            parameters (RenderListDataParameters):
                parameters parameter
            override_parameters (RenderListDataOverrideParameters):
                overrideParameters parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self,
            "RenderGovernanceHubSPList",
            None,
            {"parameters": parameters, "overrideParameters": override_parameters},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def render_ib_segment_list_filter_data(self, parameters: RenderListFilterDataParameters) -> ClientResult[bytes]:
        """RenderIBSegmentListFilterData operation.

        Args:
            parameters (RenderListFilterDataParameters):
                parameters parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = FunctionQuery(self, "RenderIBSegmentListFilterData", [parameters], return_type, return_raw_content=True)
        self.context.add_query(qry)
        return return_type

    def render_ownership_policy_storage_sp_list(
        self, parameters: RenderListDataParameters, override_parameters: RenderListDataOverrideParameters
    ) -> ClientResult[bytes]:
        """RenderOwnershipPolicyStorageSPList operation.

        Args:
            parameters (RenderListDataParameters):
                parameters parameter
            override_parameters (RenderListDataOverrideParameters):
                overrideParameters parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self,
            "RenderOwnershipPolicyStorageSPList",
            None,
            {"parameters": parameters, "overrideParameters": override_parameters},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def render_policy_definition_list(
        self, parameters: RenderListDataParameters, override_parameters: RenderListDataOverrideParameters
    ) -> ClientResult[bytes]:
        """RenderPolicyDefinitionList operation.

        Args:
            parameters (RenderListDataParameters):
                parameters parameter
            override_parameters (RenderListDataOverrideParameters):
                overrideParameters parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self,
            "RenderPolicyDefinitionList",
            None,
            {"parameters": parameters, "overrideParameters": override_parameters},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def render_policy_executions_history(
        self, parameters: RenderListDataParameters, override_parameters: RenderListDataOverrideParameters
    ) -> ClientResult[bytes]:
        """RenderPolicyExecutionsHistory operation.

        Args:
            parameters (RenderListDataParameters):
                parameters parameter
            override_parameters (RenderListDataOverrideParameters):
                overrideParameters parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = FunctionQuery(
            self,
            "RenderPolicyExecutionsHistory",
            [parameters, override_parameters],
            return_type,
            return_raw_content=True,
        )
        self.context.add_query(qry)
        return return_type

    def render_recent_admin_action_report(
        self, parameters: RenderListDataParameters, override_parameters: RenderListDataOverrideParameters
    ) -> ClientResult[bytes]:
        """RenderRecentAdminActionReport operation.

        Args:
            parameters (RenderListDataParameters):
                parameters parameter
            override_parameters (RenderListDataOverrideParameters):
                overrideParameters parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(
            self,
            "RenderRecentAdminActionReport",
            None,
            {"parameters": parameters, "overrideParameters": override_parameters},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def reorder_targeted_sites(self, site_ids: list[UUID]) -> ClientResult[ClientValueCollection[TargetedSiteDetails]]:
        """ReorderTargetedSites operation.

        Args:
            site_ids (list[UUID]):
                siteIds parameter
        """
        from office365.sharepoint.viva.targetedsitedetails import TargetedSiteDetails

        return_type = ClientResult(self.context, ClientValueCollection[TargetedSiteDetails]())
        qry = ServiceOperationQuery(
            self, "ReorderTargetedSites", None, {"siteIds": GuidCollection(site_ids)}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def request_content_management_assessment(self) -> ClientResult[ContentManagementAssessmentOperationResult]:
        """RequestContentManagementAssessment operation."""
        from office365.sharepoint.tenant.administration.contentmanagementassessmentoperationresult import (
            ContentManagementAssessmentOperationResult,
        )

        return_type = ClientResult(self.context, ContentManagementAssessmentOperationResult())
        qry = ServiceOperationQuery(self, "RequestContentManagementAssessment", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def restore_container(self, container_id: str) -> Self:
        """RestoreContainer operation.

        Args:
            container_id (str):
                containerId parameter
        """
        qry = ServiceOperationQuery(self, "RestoreContainer", None, {"containerId": container_id}, None, None)
        self.context.add_query(qry)
        return self

    def restore_spo_deleted_container_by_container_id(self, container_id: str) -> ClientResult[bool]:
        """RestoreSPODeletedContainerByContainerId operation.

        Args:
            container_id (str):
                containerId parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self, "RestoreSPODeletedContainerByContainerId", None, {"containerId": container_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def restore_spo_deleted_container_by_container_site_url(self, container_site_url: str) -> ClientResult[bool]:
        """RestoreSPODeletedContainerByContainerSiteUrl operation.

        Args:
            container_site_url (str):
                containerSiteUrl parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self,
            "RestoreSPODeletedContainerByContainerSiteUrl",
            None,
            {"containerSiteUrl": container_site_url},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def run_admin_home_post_load_tasks(self) -> Self:
        """RunAdminHomePostLoadTasks operation."""
        qry = ServiceOperationQuery(self, "RunAdminHomePostLoadTasks", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def save_file_request_branding_asset_config(
        self, asset_library_url: str, logo_file_url: str, background_file_url: str, profile_type: int
    ) -> Self:
        """SaveFileRequestBrandingAssetConfig operation.

        Args:
            asset_library_url (str):
                assetLibraryUrl parameter
            logo_file_url (str):
                logoFileUrl parameter
            background_file_url (str):
                backgroundFileUrl parameter
            profile_type (int):
                profileType parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SaveFileRequestBrandingAssetConfig",
            None,
            {
                "assetLibraryUrl": asset_library_url,
                "logoFileUrl": logo_file_url,
                "backgroundFileUrl": background_file_url,
                "profileType": profile_type,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_baseline_security_mode_pre_auth_settings(self, is_disabled: bool, allow_list: list[str]) -> Self:
        """SetBaselineSecurityModePreAuthSettings operation.

        Args:
            is_disabled (bool):
                isDisabled parameter
            allow_list (list[str]):
                allowList parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetBaselineSecurityModePreAuthSettings",
            None,
            {"isDisabled": is_disabled, "allowList": StringCollection(allow_list)},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_catalog_management_type_display_name(
        self, property_type: int, display_name: str
    ) -> ClientResult[CatalogManagementSettings]:
        """SetCatalogManagementTypeDisplayName operation.

        Args:
            property_type (int):
                propertyType parameter
            display_name (str):
                displayName parameter
        """
        from office365.sharepoint.tenant.administration.catalog_management_settings import (
            CatalogManagementSettings,
        )

        return_type = ClientResult(self.context, CatalogManagementSettings())
        qry = ServiceOperationQuery(
            self,
            "SetCatalogManagementTypeDisplayName",
            None,
            {"propertyType": property_type, "displayName": display_name},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def set_catalog_management_value_display_name(
        self, id_: UUID, display_name: str
    ) -> ClientResult[CatalogManagementSettings]:
        """SetCatalogManagementValueDisplayName operation.

        Args:
            id_ (UUID):
                id parameter
            display_name (str):
                displayName parameter
        """
        from office365.sharepoint.tenant.administration.catalog_management_settings import (
            CatalogManagementSettings,
        )

        return_type = ClientResult(self.context, CatalogManagementSettings())
        qry = ServiceOperationQuery(
            self,
            "SetCatalogManagementValueDisplayName",
            None,
            {"id": id_, "displayName": display_name},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def set_copilot_promo_opt_in_status(self, copilot_promo_opt_in_enabled: bool) -> Self:
        """SetCopilotPromoOptInStatus operation.

        Args:
            copilot_promo_opt_in_enabled (bool):
                copilotPromoOptInEnabled parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetCopilotPromoOptInStatus",
            None,
            {"copilotPromoOptInEnabled": copilot_promo_opt_in_enabled},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_file_archive_policy(
        self,
        policy_id: UUID,
        policy_name: str,
        policy_type: str,
        should_update_last_access_criteria: bool,
        months_since_last_access_criteria: int,
        file_type_criteria: list[str],
        should_update_what_if_mode: bool,
        is_what_if_mode: bool,
        state: str,
        file_type_exclusion_criteria: list[str],
    ) -> ClientResult[SPOFileArchivePolicyInfo]:
        """SetFileArchivePolicy operation.

        Args:
            policy_id (UUID):
                policyId parameter
            policy_name (str):
                policyName parameter
            policy_type (str):
                policyType parameter
            should_update_last_access_criteria (bool):
                shouldUpdateLastAccessCriteria parameter
            months_since_last_access_criteria (int):
                monthsSinceLastAccessCriteria parameter
            file_type_criteria (list[str]):
                fileTypeCriteria parameter
            should_update_what_if_mode (bool):
                shouldUpdateWhatIfMode parameter
            is_what_if_mode (bool):
                isWhatIfMode parameter
            state (str):
                state parameter
            file_type_exclusion_criteria (list[str]):
                fileTypeExclusionCriteria parameter
        """
        from office365.sharepoint.tenantadministration.spo_file_archive_policy_info import (
            SPOFileArchivePolicyInfo,
        )

        return_type = ClientResult(self.context, SPOFileArchivePolicyInfo())
        qry = ServiceOperationQuery(
            self,
            "SetFileArchivePolicy",
            None,
            {
                "policyId": policy_id,
                "policyName": policy_name,
                "policyType": policy_type,
                "shouldUpdateLastAccessCriteria": should_update_last_access_criteria,
                "monthsSinceLastAccessCriteria": months_since_last_access_criteria,
                "fileTypeCriteria": StringCollection(file_type_criteria),
                "shouldUpdateWhatIfMode": should_update_what_if_mode,
                "isWhatIfMode": is_what_if_mode,
                "state": state,
                "fileTypeExclusionCriteria": StringCollection(file_type_exclusion_criteria),
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def set_file_type_version_policy(
        self,
        file_types: list[str],
        is_auto_trim_enabled: bool,
        major_version_limit: int,
        expire_versions_after_days: int,
    ) -> Self:
        """SetFileTypeVersionPolicy operation.

        Args:
            file_types (list[str]):
                fileTypes parameter
            is_auto_trim_enabled (bool):
                isAutoTrimEnabled parameter
            major_version_limit (int):
                majorVersionLimit parameter
            expire_versions_after_days (int):
                expireVersionsAfterDays parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetFileTypeVersionPolicy",
            None,
            {
                "fileTypes": StringCollection(file_types),
                "isAutoTrimEnabled": is_auto_trim_enabled,
                "majorVersionLimit": major_version_limit,
                "expireVersionsAfterDays": expire_versions_after_days,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_ib_segments_on_site(self, site_id: UUID, segments: list[UUID], ib_mode: str) -> ClientResult[str]:
        """SetIBSegmentsOnSite operation.

        Args:
            site_id (UUID):
                siteId parameter
            segments (list[UUID]):
                segments parameter
            ib_mode (str):
                ibMode parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "SetIBSegmentsOnSite",
            None,
            {"siteId": site_id, "segments": GuidCollection(segments), "ibMode": ib_mode},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def set_idle_session_sign_out_for_unmanaged_devices(
        self, enabled: bool, warn_after: _dt.time, sign_out_after: _dt.time
    ) -> ClientResult[bool]:
        """SetIdleSessionSignOutForUnmanagedDevices operation.

        Args:
            enabled (bool):
                enabled parameter
            warn_after (time):
                warnAfter parameter
            sign_out_after (time):
                signOutAfter parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self,
            "SetIdleSessionSignOutForUnmanagedDevices",
            None,
            {"enabled": enabled, "warnAfter": warn_after, "signOutAfter": sign_out_after},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def set_jit_dlp_policy_data(
        self,
        mark_all_files_as_sensitive_by_default: bool,
        odb_sensitivity_refresh_window_in_hours: int,
        execution_mode: int,
    ) -> Self:
        """SetJitDlpPolicyData operation.

        Args:
            mark_all_files_as_sensitive_by_default (bool):
                markAllFilesAsSensitiveByDefault parameter
            odb_sensitivity_refresh_window_in_hours (int):
                odbSensitivityRefreshWindowInHours parameter
            execution_mode (int):
                executionMode parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetJitDlpPolicyData",
            None,
            {
                "markAllFilesAsSensitiveByDefault": mark_all_files_as_sensitive_by_default,
                "odbSensitivityRefreshWindowInHours": odb_sensitivity_refresh_window_in_hours,
                "executionMode": execution_mode,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_org_assets_with_config(
        self, lib_url: str, thumbnail_url: str, org_asset_type: int, config_param: OrgAssetsLibraryConfigParam
    ) -> Self:
        """SetOrgAssetsWithConfig operation.

        Args:
            lib_url (str):
                libUrl parameter
            thumbnail_url (str):
                thumbnailUrl parameter
            org_asset_type (int):
                orgAssetType parameter
            config_param (OrgAssetsLibraryConfigParam):
                configParam parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetOrgAssetsWithConfig",
            None,
            {
                "libUrl": lib_url,
                "thumbnailUrl": thumbnail_url,
                "orgAssetType": org_asset_type,
                "configParam": config_param,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_org_assets_with_type(self, lib_url: str, thumbnail_url: str, org_asset_type: int) -> Self:
        """SetOrgAssetsWithType operation.

        Args:
            lib_url (str):
                libUrl parameter
            thumbnail_url (str):
                thumbnailUrl parameter
            org_asset_type (int):
                orgAssetType parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetOrgAssetsWithType",
            None,
            {"libUrl": lib_url, "thumbnailUrl": thumbnail_url, "orgAssetType": org_asset_type},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_pre_auth_is_disabled_setting(self, is_disabled: bool) -> Self:
        """SetPreAuthIsDisabledSetting operation.

        Args:
            is_disabled (bool):
                isDisabled parameter
        """
        qry = ServiceOperationQuery(self, "SetPreAuthIsDisabledSetting", None, {"isDisabled": is_disabled}, None, None)
        self.context.add_query(qry)
        return self

    def set_resource_as_authoritative(self, site_id: UUID) -> ClientResult[AuthoritativeResourceProperties]:
        """SetResourceAsAuthoritative operation.

        Args:
            site_id (UUID):
                siteId parameter
        """
        from office365.sharepoint.tenant.administration.authoritative_resource_properties import (
            AuthoritativeResourceProperties,
        )

        return_type = ClientResult(self.context, AuthoritativeResourceProperties())
        qry = ServiceOperationQuery(self, "SetResourceAsAuthoritative", None, {"siteId": site_id}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def set_sensitivity_label_container(self, container_id: str, sensitivity_label: UUID) -> Self:
        """SetSensitivityLabelContainer operation.

        Args:
            container_id (str):
                containerId parameter
            sensitivity_label (UUID):
                sensitivityLabel parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetSensitivityLabelContainer",
            None,
            {"containerId": container_id, "sensitivityLabel": sensitivity_label},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_site_administrators(self, site_administrators_fields_data: SiteAdministratorsFieldsData) -> Self:
        """SetSiteAdministrators operation.

        Args:
            site_administrators_fields_data (SiteAdministratorsFieldsData):
                siteAdministratorsFieldsData parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetSiteAdministrators",
            None,
            {"siteAdministratorsFieldsData": site_administrators_fields_data},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_site_user_groups(self, site_user_groups_data: SiteUserGroupsData) -> Self:
        """SetSiteUserGroups operation.

        Args:
            site_user_groups_data (SiteUserGroupsData):
                siteUserGroupsData parameter
        """
        qry = ServiceOperationQuery(
            self, "SetSiteUserGroups", None, {"siteUserGroupsData": site_user_groups_data}, None, None
        )
        self.context.add_query(qry)
        return self

    def set_sp_embedded_application_permissions(
        self, sp_syntex_application_properties: SPSyntexApplicationProperties
    ) -> ClientResult[SPSyntexApplicationProperties]:
        """SetSPEmbeddedApplicationPermissions operation.

        Args:
            sp_syntex_application_properties (SPSyntexApplicationProperties):
                spSyntexApplicationProperties parameter
        """
        from office365.sharepoint.tenant.administration.syntex.applicationproperties import (
            SPSyntexApplicationProperties,
        )

        return_type = ClientResult(self.context, SPSyntexApplicationProperties())
        qry = ServiceOperationQuery(
            self,
            "SetSPEmbeddedApplicationPermissions",
            None,
            {"spSyntexApplicationProperties": sp_syntex_application_properties},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def set_sp_embedded_application_properties(
        self, sp_syntex_application_properties: SPSyntexApplicationProperties
    ) -> ClientResult[SPSyntexApplicationProperties]:
        """SetSPEmbeddedApplicationProperties operation.

        Args:
            sp_syntex_application_properties (SPSyntexApplicationProperties):
                spSyntexApplicationProperties parameter
        """
        from office365.sharepoint.tenant.administration.syntex.applicationproperties import (
            SPSyntexApplicationProperties,
        )

        return_type = ClientResult(self.context, SPSyntexApplicationProperties())
        qry = ServiceOperationQuery(
            self,
            "SetSPEmbeddedApplicationProperties",
            None,
            {"spSyntexApplicationProperties": sp_syntex_application_properties},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def set_sph_site(self, sph_site_url: str) -> ClientResult[str]:
        """SetSPHSite operation.

        Args:
            sph_site_url (str):
                sphSiteUrl parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "SetSPHSite", None, {"sphSiteUrl": sph_site_url}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def set_sph_site_with_configuration(
        self, sph_site_url: str, configuration: HomeSiteConfigurationParam
    ) -> ClientResult[str]:
        """SetSPHSiteWithConfiguration operation.

        Args:
            sph_site_url (str):
                sphSiteUrl parameter
            configuration (HomeSiteConfigurationParam):
                configuration parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "SetSPHSiteWithConfiguration",
            None,
            {"sphSiteUrl": sph_site_url, "configuration": configuration},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def set_spo_container_properties(self, sp_container_properties: SPContainerProperties) -> Self:
        """SetSPOContainerProperties operation.

        Args:
            sp_container_properties (SPContainerProperties):
                spContainerProperties parameter
        """
        qry = ServiceOperationQuery(
            self, "SetSPOContainerProperties", None, {"spContainerProperties": sp_container_properties}, None, None
        )
        self.context.add_query(qry)
        return self

    def set_spo_container_type(
        self, container_type_properties: SPContainerTypeProperties
    ) -> ClientResult[SPContainerTypeProperties]:
        """SetSPOContainerType operation.

        Args:
            container_type_properties (SPContainerTypeProperties):
                containerTypeProperties parameter
        """
        from office365.sharepoint.tenant.administration.container.type.properties import (
            SPContainerTypeProperties,
        )

        return_type = ClientResult(self.context, SPContainerTypeProperties())
        qry = ServiceOperationQuery(
            self, "SetSPOContainerType", None, {"containerTypeProperties": container_type_properties}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def set_spo_container_type_configuration(
        self, sp_container_type_configuration_properties: SPContainerTypeConfigurationProperties
    ) -> ClientResult[SPContainerTypeConfigurationProperties]:
        """SetSPOContainerTypeConfiguration operation.

        Args:
            sp_container_type_configuration_properties (SPContainerTypeConfigurationProperties):
                spContainerTypeConfigurationProperties parameter
        """
        from office365.sharepoint.tenant.administration.container.type.configurationproperties import (
            SPContainerTypeConfigurationProperties,
        )

        return_type = ClientResult(self.context, SPContainerTypeConfigurationProperties())
        qry = ServiceOperationQuery(
            self,
            "SetSPOContainerTypeConfiguration",
            None,
            {"spContainerTypeConfigurationProperties": sp_container_type_configuration_properties},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def set_spo_restricted_search_mode(self, mode: int) -> Self:
        """SetSPORestrictedSearchMode operation.

        Args:
            mode (int):
                mode parameter
        """
        qry = ServiceOperationQuery(self, "SetSPORestrictedSearchMode", None, {"mode": mode}, None, None)
        self.context.add_query(qry)
        return self

    def set_spo_service_prioritization_app_registration(
        self,
        app_id: UUID,
        enabled: bool,
        enabled_has_value: bool,
        quota_multiplier: int,
        quota_multiplier_has_value: bool,
    ) -> Self:
        """SetSPOServicePrioritizationAppRegistration operation.

        Args:
            app_id (UUID):
                appId parameter
            enabled (bool):
                enabled parameter
            enabled_has_value (bool):
                enabledHasValue parameter
            quota_multiplier (int):
                quotaMultiplier parameter
            quota_multiplier_has_value (bool):
                quotaMultiplierHasValue parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetSPOServicePrioritizationAppRegistration",
            None,
            {
                "appId": app_id,
                "enabled": enabled,
                "enabledHasValue": enabled_has_value,
                "quotaMultiplier": quota_multiplier,
                "quotaMultiplierHasValue": quota_multiplier_has_value,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_spo_syntex_applications_clear_override_sharing_capability(self, owning_application_id: UUID) -> Self:
        """SetSPOSyntexApplicationsClearOverrideSharingCapability operation.

        Args:
            owning_application_id (UUID):
                owningApplicationId parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetSPOSyntexApplicationsClearOverrideSharingCapability",
            None,
            {"owningApplicationId": owning_application_id},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_spo_syntex_applications_sharing_capability(
        self, owning_application_id: UUID, sharing_capability: int, override_tenant_sharing_capability: bool
    ) -> Self:
        """SetSPOSyntexApplicationsSharingCapability operation.

        Args:
            owning_application_id (UUID):
                owningApplicationId parameter
            sharing_capability (int):
                sharingCapability parameter
            override_tenant_sharing_capability (bool):
                overrideTenantSharingCapability parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetSPOSyntexApplicationsSharingCapability",
            None,
            {
                "owningApplicationId": owning_application_id,
                "sharingCapability": sharing_capability,
                "overrideTenantSharingCapability": override_tenant_sharing_capability,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_storage_maximum_level_container(self, container_id: str, storage_maximum_level: int) -> Self:
        """SetStorageMaximumLevelContainer operation.

        Args:
            container_id (str):
                containerId parameter
            storage_maximum_level (int):
                storageMaximumLevel parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetStorageMaximumLevelContainer",
            None,
            {"containerId": container_id, "storageMaximumLevel": storage_maximum_level},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_syntex_payg_feature_activation(self, feature_name: str, activation_status: str) -> Self:
        """SetSyntexPaygFeatureActivation operation.

        Args:
            feature_name (str):
                featureName parameter
            activation_status (str):
                activationStatus parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetSyntexPaygFeatureActivation",
            None,
            {"featureName": feature_name, "activationStatus": activation_status},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_tenant_data_loss_prevention_quarantine_settings(self, serialized_value: str) -> Self:
        """SetTenantDataLossPreventionQuarantineSettings operation.

        Args:
            serialized_value (str):
                serializedValue parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetTenantDataLossPreventionQuarantineSettings",
            None,
            {"serializedValue": serialized_value},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def set_track_view_feature_always_visible(self) -> ClientResult[bool]:
        """SetTrackViewFeatureAlwaysVisible operation."""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "SetTrackViewFeatureAlwaysVisible", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def set_use_graph_url_apps_list_setting(self, use_graph_url_apps_list: str) -> Self:
        """SetUseGraphUrlAppsListSetting operation.

        Args:
            use_graph_url_apps_list (str):
                useGraphUrlAppsList parameter
        """
        qry = ServiceOperationQuery(
            self, "SetUseGraphUrlAppsListSetting", None, {"useGraphUrlAppsList": use_graph_url_apps_list}, None, None
        )
        self.context.add_query(qry)
        return self

    def set_use_graph_url_is_enabled_setting(self, use_graph_url_is_enabled: bool) -> Self:
        """SetUseGraphUrlIsEnabledSetting operation.

        Args:
            use_graph_url_is_enabled (bool):
                useGraphUrlIsEnabled parameter
        """
        qry = ServiceOperationQuery(
            self, "SetUseGraphUrlIsEnabledSetting", None, {"useGraphUrlIsEnabled": use_graph_url_is_enabled}, None, None
        )
        self.context.add_query(qry)
        return self

    def set_use_graph_url_settings(self, use_graph_url_is_enabled: bool, use_graph_url_apps_list: str) -> Self:
        """SetUseGraphUrlSettings operation.

        Args:
            use_graph_url_is_enabled (bool):
                useGraphUrlIsEnabled parameter
            use_graph_url_apps_list (str):
                useGraphUrlAppsList parameter
        """
        qry = ServiceOperationQuery(
            self,
            "SetUseGraphUrlSettings",
            None,
            {"useGraphUrlIsEnabled": use_graph_url_is_enabled, "useGraphUrlAppsList": use_graph_url_apps_list},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def switch_file_request_branding_profiles(self) -> Self:
        """SwitchFileRequestBrandingProfiles operation."""
        qry = ServiceOperationQuery(self, "SwitchFileRequestBrandingProfiles", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def test_check_if_file_exists_in_adls(
        self, upload_to_adls_type: str, upload_to_adls_subtype: str
    ) -> ClientResult[bool]:
        """TestCheckIfFileExistsInADLS operation.

        Args:
            upload_to_adls_type (str):
                uploadToADLSType parameter
            upload_to_adls_subtype (str):
                uploadToADLSSubtype parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self,
            "TestCheckIfFileExistsInADLS",
            None,
            {"uploadToADLSType": upload_to_adls_type, "uploadToADLSSubtype": upload_to_adls_subtype},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def test_generate_report_insights(
        self, insights_scenario: int, report_url: str, model_name: str
    ) -> ClientResult[str]:
        """TestGenerateReportInsights operation.

        Args:
            insights_scenario (int):
                insightsScenario parameter
            report_url (str):
                reportUrl parameter
            model_name (str):
                modelName parameter
        """
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "TestGenerateReportInsights", [insights_scenario, report_url, model_name], return_type)
        self.context.add_query(qry)
        return return_type

    def test_get_insight_generation_response_async(
        self, job_id: str, report_url: str, model_name: str
    ) -> ClientResult[str]:
        """TestGetInsightGenerationResponseAsync operation.

        Args:
            job_id (str):
                jobId parameter
            report_url (str):
                reportUrl parameter
            model_name (str):
                modelName parameter
        """
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "TestGetInsightGenerationResponseAsync", [job_id, report_url, model_name], return_type)
        self.context.add_query(qry)
        return return_type

    def test_get_insight_generation_status_async(
        self, job_id: str, report_url: str, model_name: str
    ) -> ClientResult[str]:
        """TestGetInsightGenerationStatusAsync operation.

        Args:
            job_id (str):
                jobId parameter
            report_url (str):
                reportUrl parameter
            model_name (str):
                modelName parameter
        """
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "TestGetInsightGenerationStatusAsync", [job_id, report_url, model_name], return_type)
        self.context.add_query(qry)
        return return_type

    def test_queue_insight_generation_async(
        self, insights_scenario: int, report_url: str, model_name: str, max_token_size: int
    ) -> ClientResult[str]:
        """TestQueueInsightGenerationAsync operation.

        Args:
            insights_scenario (int):
                insightsScenario parameter
            report_url (str):
                reportUrl parameter
            model_name (str):
                modelName parameter
            max_token_size (int):
                maxTokenSize parameter
        """
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(
            self,
            "TestQueueInsightGenerationAsync",
            [insights_scenario, report_url, model_name, max_token_size],
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def test_resync_to_adls(self, skip_validation: bool) -> Self:
        """TestResyncToADLS operation.

        Args:
            skip_validation (bool):
                skipValidation parameter
        """
        qry = ServiceOperationQuery(self, "TestResyncToADLS", None, {"skipValidation": skip_validation}, None, None)
        self.context.add_query(qry)
        return self

    def test_upload_file_to_adls(self, upload_to_adls_type: str, upload_to_adls_subtype: str) -> Self:
        """TestUploadFileToADLS operation.

        Args:
            upload_to_adls_type (str):
                uploadToADLSType parameter
            upload_to_adls_subtype (str):
                uploadToADLSSubtype parameter
        """
        qry = ServiceOperationQuery(
            self,
            "TestUploadFileToADLS",
            None,
            {"uploadToADLSType": upload_to_adls_type, "uploadToADLSSubtype": upload_to_adls_subtype},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def test_upload_test_report_file_to_adls(
        self, file_url: str, upload_to_adls_type: str, upload_to_adls_subtype: str
    ) -> Self:
        """TestUploadTestReportFileToADLS operation.

        Args:
            file_url (str):
                fileUrl parameter
            upload_to_adls_type (str):
                uploadToADLSType parameter
            upload_to_adls_subtype (str):
                uploadToADLSSubtype parameter
        """
        qry = ServiceOperationQuery(
            self,
            "TestUploadTestReportFileToADLS",
            None,
            {
                "fileUrl": file_url,
                "uploadToADLSType": upload_to_adls_type,
                "uploadToADLSSubtype": upload_to_adls_subtype,
            },
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def transfer_container_principal_owner(self, container_id: str, new_principal_owner_upn: str) -> Self:
        """TransferContainerPrincipalOwner operation.

        Args:
            container_id (str):
                containerId parameter
            new_principal_owner_upn (str):
                newPrincipalOwnerUpn parameter
        """
        qry = ServiceOperationQuery(
            self,
            "TransferContainerPrincipalOwner",
            None,
            {"containerId": container_id, "newPrincipalOwnerUpn": new_principal_owner_upn},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def trigger_owner_odb_provisioning(self, user_object_id: UUID) -> ClientResult[int]:
        """TriggerOwnerOdbProvisioning operation.

        Args:
            user_object_id (UUID):
                userObjectId parameter
        """
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(
            self, "TriggerOwnerOdbProvisioning", None, {"userObjectId": user_object_id}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def un_archive_container(self, container_id: str) -> Self:
        """UnArchiveContainer operation.

        Args:
            container_id (str):
                containerId parameter
        """
        qry = ServiceOperationQuery(self, "UnArchiveContainer", None, {"containerId": container_id}, None, None)
        self.context.add_query(qry)
        return self

    def unarchive_odb_by_id(self, site_id: UUID, keep_unarchived_until: datetime) -> Self:
        """UnarchiveOdbById operation.

        Args:
            site_id (UUID):
                siteId parameter
            keep_unarchived_until (datetime):
                keepUnarchivedUntil parameter
        """
        qry = ServiceOperationQuery(
            self, "UnarchiveOdbById", None, {"siteId": site_id, "keepUnarchivedUntil": keep_unarchived_until}, None, None
        )
        self.context.add_query(qry)
        return self

    def unlock_sensitivity_label_encrypted_file(self, file_url: str, justification_text: str) -> Self:
        """UnlockSensitivityLabelEncryptedFile operation.

        Args:
            file_url (str):
                fileUrl parameter
            justification_text (str):
                justificationText parameter
        """
        qry = ServiceOperationQuery(
            self,
            "UnlockSensitivityLabelEncryptedFile",
            None,
            {"fileUrl": file_url, "justificationText": justification_text},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def update_file_search_visibility(self, url: str, is_hidden: bool) -> ClientResult[bool]:
        """UpdateFileSearchVisibility operation.

        Args:
            url (str):
                url parameter
            is_hidden (bool):
                isHidden parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self, "UpdateFileSearchVisibility", None, {"url": url, "isHidden": is_hidden}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def update_jobs_work_items(self, job_ids: list[UUID]) -> Self:
        """UpdateJobsWorkItems operation.

        Args:
            job_ids (list[UUID]):
                jobIds parameter
        """
        qry = ServiceOperationQuery(self, "UpdateJobsWorkItems", None, {"jobIds": GuidCollection(job_ids)}, None, None)
        self.context.add_query(qry)
        return self

    def update_policy_definition(
        self, item_id: int, policy_input_parameters: CreatePolicyRequest, policy_operation: str
    ) -> Self:
        """UpdatePolicyDefinition operation.

        Args:
            item_id (int):
                itemId parameter
            policy_input_parameters (CreatePolicyRequest):
                policyInputParameters parameter
            policy_operation (str):
                policyOperation parameter
        """
        qry = ServiceOperationQuery(
            self,
            "UpdatePolicyDefinition",
            None,
            {"itemId": item_id, "policyInputParameters": policy_input_parameters, "policyOperation": policy_operation},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def update_ransomware_activity(
        self, list_item_id: int, column_values: ClientValueCollection[TenantAdminListItemColumnValue], category: int
    ) -> ClientResult[TenantAdminRansomwareActivity]:
        """UpdateRansomwareActivity operation.

        Args:
            list_item_id (int):
                listItemId parameter
            column_values (ClientValueCollection[TenantAdminListItemColumnValue]):
                columnValues parameter
            category (int):
                category parameter
        """
        from office365.sharepoint.tenant.administration.ransomware.activity import (
            TenantAdminRansomwareActivity,
        )

        return_type = ClientResult(self.context, TenantAdminRansomwareActivity())
        qry = ServiceOperationQuery(
            self,
            "UpdateRansomwareActivity",
            None,
            {"listItemId": list_item_id, "columnValues": column_values, "category": category},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def update_ransomware_event(
        self,
        list_item_id: int,
        column_values: ClientValueCollection[TenantAdminListItemColumnValue],
        force_resolve_activity: bool,
        category: int,
    ) -> ClientResult[TenantAdminRansomwareEvent]:
        """UpdateRansomwareEvent operation.

        Args:
            list_item_id (int):
                listItemId parameter
            column_values (ClientValueCollection[TenantAdminListItemColumnValue]):
                columnValues parameter
            force_resolve_activity (bool):
                forceResolveActivity parameter
            category (int):
                category parameter
        """
        from office365.sharepoint.tenant.administration.ransomware.event import (
            TenantAdminRansomwareEvent,
        )

        return_type = ClientResult(self.context, TenantAdminRansomwareEvent())
        qry = ServiceOperationQuery(
            self,
            "UpdateRansomwareEvent",
            None,
            {
                "listItemId": list_item_id,
                "columnValues": column_values,
                "forceResolveActivity": force_resolve_activity,
                "category": category,
            },
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def update_spo_container_user_role(self, container_id: str, login_name: str, role: str) -> Self:
        """UpdateSPOContainerUserRole operation.

        Args:
            container_id (str):
                ContainerId parameter
            login_name (str):
                loginName parameter
            role (str):
                role parameter
        """
        qry = ServiceOperationQuery(
            self,
            "UpdateSPOContainerUserRole",
            None,
            {"ContainerId": container_id, "loginName": login_name, "role": role},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def update_syntex_custom_model_setting(self, model_setting: SyntexCustomModelSetting, scenario: int) -> Self:
        """UpdateSyntexCustomModelSetting operation.

        Args:
            model_setting (SyntexCustomModelSetting):
                modelSetting parameter
            scenario (int):
                scenario parameter
        """
        qry = ServiceOperationQuery(
            self,
            "UpdateSyntexCustomModelSetting",
            None,
            {"modelSetting": model_setting, "scenario": scenario},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def update_targeted_site(
        self, site_url: str, configuration_param: HomeSiteConfigurationParam
    ) -> ClientResult[TargetedSiteDetails]:
        """UpdateTargetedSite operation.

        Args:
            site_url (str):
                siteUrl parameter
            configuration_param (HomeSiteConfigurationParam):
                configurationParam parameter
        """
        from office365.sharepoint.viva.targetedsitedetails import TargetedSiteDetails

        return_type = ClientResult(self.context, TargetedSiteDetails())
        qry = ServiceOperationQuery(
            self,
            "UpdateTargetedSite",
            None,
            {"siteUrl": site_url, "configurationParam": configuration_param},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def update_tenant_admin_list_item(
        self, list_item_id: int, column_values: ClientValueCollection[TenantAdminListItemColumnValue], list_name: str
    ) -> Self:
        """UpdateTenantAdminListItem operation.

        Args:
            list_item_id (int):
                listItemId parameter
            column_values (ClientValueCollection[TenantAdminListItemColumnValue]):
                columnValues parameter
            list_name (str):
                listName parameter
        """
        qry = ServiceOperationQuery(
            self,
            "UpdateTenantAdminListItem",
            None,
            {"listItemId": list_item_id, "columnValues": column_values, "listName": list_name},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def update_tenant_admin_list_view(self, view_id: str, view_xml: str) -> Self:
        """UpdateTenantAdminListView operation.

        Args:
            view_id (str):
                viewId parameter
            view_xml (str):
                viewXml parameter
        """
        qry = ServiceOperationQuery(
            self, "UpdateTenantAdminListView", None, {"viewId": view_id, "viewXml": view_xml}, None, None
        )
        self.context.add_query(qry)
        return self

    def update_unlicensed_odb_active_storage_date_by_id(self, site_id: UUID, keep_unarchived_until: datetime) -> Self:
        """UpdateUnlicensedOdbActiveStorageDateById operation.

        Args:
            site_id (UUID):
                siteId parameter
            keep_unarchived_until (datetime):
                keepUnarchivedUntil parameter
        """
        qry = ServiceOperationQuery(
            self,
            "UpdateUnlicensedOdbActiveStorageDateById",
            None,
            {"siteId": site_id, "keepUnarchivedUntil": keep_unarchived_until},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def validate_home_site(self, validation_action_type: int, site_url: str) -> Self:
        """ValidateHomeSite operation.

        Args:
            validation_action_type (int):
                validationActionType parameter
            site_url (str):
                siteUrl parameter
        """
        qry = ServiceOperationQuery(
            self,
            "ValidateHomeSite",
            None,
            {"validationActionType": validation_action_type, "siteUrl": site_url},
            None,
            None,
        )
        self.context.add_query(qry)
        return self

    def validate_multiple_home_sites_parameter_exists(self, has_parameters: bool) -> Self:
        """ValidateMultipleHomeSitesParameterExists operation.

        Args:
            has_parameters (bool):
                hasParameters parameter
        """
        qry = ServiceOperationQuery(
            self, "ValidateMultipleHomeSitesParameterExists", None, {"hasParameters": has_parameters}, None, None
        )
        self.context.add_query(qry)
        return self

    @property
    def onedrives_summary_metrics_data(self) -> Optional[OneDrivesSummaryMetrics]:
        """Gets the OneDrivesSummaryMetricsData property"""
        return self.properties.get("OneDrivesSummaryMetricsData", None)

    @property
    def smart_wiki_entry_scope(self) -> Optional[int]:
        """Gets the SmartWikiEntryScope property"""
        return self.properties.get("SmartWikiEntryScope", None)

    @property
    def smart_wiki_entry_site_info_list(self) -> ClientValueCollection[SiteInfoForSitePicker]:
        """Gets the SmartWikiEntrySiteInfoList property"""
        from office365.sharepoint.tenant.administration.siteinfo_for_site_picker import (
            SiteInfoForSitePicker,
        )

        return self.properties.get(
            "SmartWikiEntrySiteInfoList", ClientValueCollection[SiteInfoForSitePicker](SiteInfoForSitePicker)
        )

    @property
    def smart_wiki_entry_site_list(self) -> GuidCollection:
        """Gets the SmartWikiEntrySiteList property"""
        return self.properties.get("SmartWikiEntrySiteList", GuidCollection())

    def get_onedrives_summary_metrics_data(self) -> ClientResult[OneDrivesSummaryMetrics]:
        """GetOneDrivesSummaryMetricsData operation."""
        from office365.sharepoint.tenant.administration.onedrives_summary_metrics import (
            OneDrivesSummaryMetrics,
        )

        return_type = ClientResult(self.context, OneDrivesSummaryMetrics())
        qry = ServiceOperationQuery(self, "GetOneDrivesSummaryMetricsData", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_spo_container_type_file_version_policy_job_impact(
        self, container_type_id: UUID, version_policy: SPOFileVersionPolicySettings
    ) -> ClientResult[SPOTenantVersionPolicyImpact]:
        """GetSPOContainerTypeFileVersionPolicyJobImpact operation.

        Args:
            container_type_id (UUID):
                containerTypeId parameter
            version_policy (SPOFileVersionPolicySettings):
                versionPolicy parameter
        """
        from office365.sharepoint.tenant.administration.spo_tenant_version_policy_impact import (
            SPOTenantVersionPolicyImpact,
        )

        return_type = ClientResult(self.context, SPOTenantVersionPolicyImpact())
        qry = ServiceOperationQuery(
            self,
            "GetSPOContainerTypeFileVersionPolicyJobImpact",
            None,
            {"containerTypeId": container_type_id, "versionPolicy": version_policy},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def get_spo_container_type_file_version_policy_job_progress(self, container_type_id: UUID) -> ClientResult[str]:
        """GetSPOContainerTypeFileVersionPolicyJobProgress operation.

        Args:
            container_type_id (UUID):
                containerTypeId parameter
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self,
            "GetSPOContainerTypeFileVersionPolicyJobProgress",
            None,
            {"containerTypeId": container_type_id},
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def set_smart_wiki_entry_settings(self, scope: int, site_ids: list[UUID]) -> Self:
        """SetSmartWikiEntrySettings operation.

        Args:
            scope (int):
                scope parameter
            site_ids (list[UUID]):
                siteIds parameter
        """
        qry = ServiceOperationQuery(
            self, "SetSmartWikiEntrySettings", None, {"scope": scope, "siteIds": GuidCollection(site_ids)}, None, None
        )
        self.context.add_query(qry)
        return self
