from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import GuidCollection, StringCollection
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.entity import Entity
from office365.sharepoint.tenant.administration.deny_add_and_customize_pages_status import (
    DenyAddAndCustomizePagesStatus,
)
from office365.sharepoint.tenant.administration.jobs.spo_operation import SpoOperation
from office365.sharepoint.tenant.administration.sharing_capabilities import (
    SharingCapabilities,
)
from office365.sharepoint.tenant.administration.spofileversionfiletypepolicysettings import (
    SPOFileVersionFileTypePolicySettings,
)
from office365.sharepoint.translation.resource_entry import SPResourceEntry


class SiteProperties(Entity):
    """Contains a property bag of information about a site."""

    def __repr__(self):
        return self.url or self.entity_type_name

    @staticmethod
    def clear_sharing_lock_down(context: ClientContext, site_url: str) -> SiteProperties:
        payload = {"siteUrl": site_url}
        binding_type = SiteProperties(context)
        qry = ServiceOperationQuery(binding_type, "ClearSharingLockDown", None, payload, None, None, True)
        context.add_query(qry)
        return binding_type

    def update_ex(self) -> SpoOperation:
        """Updates the site collection properties with the new properties specified in the SiteProperties object."""
        return_type = SpoOperation(self.context)
        qry = ServiceOperationQuery(self, "Update", parameters_type=self, return_type=return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def allow_downloading_non_web_viewable_files(self) -> Optional[bool]:
        """Specifies if non web viewable files can be downloaded."""
        return self.properties.get("AllowDownloadingNonWebViewableFiles", None)

    @property
    def allow_editing(self) -> Optional[bool]:
        """Prevents users from editing Office files in the browser and copying and pasting Office file contents
        out of the browser window."""
        return self.properties.get("AllowEditing", None)

    @property
    def allow_self_service_upgrade(self) -> Optional[bool]:
        """Whether version to version upgrade is allowed on this site."""
        return self.properties.get("AllowSelfServiceUpgrade", None)

    @property
    def anonymous_link_expiration_in_days(self) -> Optional[int]:
        """Specifies all anonymous/anyone links that have been created
        (or will be created) will expire after the set number of days."""
        return self.properties.get("AnonymousLinkExpirationInDays", None)

    @property
    def apply_to_existing_document_libraries(self) -> Optional[bool]:
        """Create a job to apply the version history limits setting to existing document libraries."""
        return self.properties.get("ApplyToExistingDocumentLibraries", None)

    @property
    def apply_to_new_document_libraries(self) -> Optional[bool]:
        """Gets site version policy for new document libraries."""
        return self.properties.get("ApplyToNewDocumentLibraries", None)

    @property
    def archived_by(self) -> Optional[str]:
        """Gets site version policy for new document libraries."""
        return self.properties.get("ArchivedBy", None)

    @property
    def archived_time(self) -> Optional[datetime]:
        """Gets the time when site was archived."""
        return self.properties.get("ArchivedTime", datetime.min)

    @property
    def block_download_links_file_type(self) -> Optional[int]:
        """Block downloads for view-only files in SharePoint and OneDrive."""
        return self.properties.get("BlockDownloadLinksFileType", None)

    @property
    def block_download_microsoft365_group_ids(self) -> Optional[StringCollection]:
        """Block downloads for view-only files in SharePoint and OneDrive."""
        return self.properties.get("BlockDownloadMicrosoft365GroupIds", StringCollection())

    @property
    def block_download_policy_file_type_ids(self) -> Optional[StringCollection]:
        """"""
        return self.properties.get("BlockDownloadPolicyFileTypeIds", StringCollection())

    @property
    def created_time(self) -> Optional[datetime]:
        """Gets the time when the site was created."""
        return self.properties.get("CreatedTime", datetime.min)

    @property
    def deny_add_and_customize_pages(self) -> DenyAddAndCustomizePagesStatus:
        """Represents the status of the [DenyAddAndCustomizePages] feature on a site collection."""
        return self.properties.get("DenyAddAndCustomizePages", DenyAddAndCustomizePagesStatus.Unknown)

    @deny_add_and_customize_pages.setter
    def deny_add_and_customize_pages(self, value: DenyAddAndCustomizePagesStatus) -> None:
        """Sets the status of the [DenyAddAndCustomizePages] feature on a site collection."""
        self.set_property("DenyAddAndCustomizePages", value.value)

    @property
    def last_content_modified_date(self) -> Optional[datetime]:
        """Gets the last time content was modified on the site."""
        return self.properties.get("LastContentModifiedDate", datetime.min)

    @property
    def group_owner_login_name(self) -> Optional[str]:
        """Gets the Group Owner login name."""
        return self.properties.get("GroupOwnerLoginName", None)

    @property
    def is_hub_site(self) -> Optional[bool]:
        """"""
        return self.properties.get("IsHubSite", None)

    @property
    def title(self) -> Optional[str]:
        """Site title"""
        return self.properties.get("Title", None)

    @property
    def title_translations(self) -> ClientValueCollection[SPResourceEntry]:
        """Site titles"""
        return self.properties.get("TitleTranslations", ClientValueCollection(SPResourceEntry))

    @property
    def owner_login_name(self) -> Optional[str]:
        """ """
        return self.properties.get("OwnerLoginName", None)

    @property
    def webs_count(self) -> Optional[str]:
        """Gets the number of Web objects in the site."""
        return self.properties.get("WebsCount", None)

    @property
    def url(self) -> Optional[str]:
        """Gets the URL of the site."""
        return self.properties.get("Url", None)

    @property
    def compatibility_level(self) -> Optional[str]:
        """Gets the compatibility level of the site."""
        return self.properties.get("CompatibilityLevel", None)

    @property
    def lock_state(self) -> Optional[str]:
        """Gets or sets the lock state of the site."""
        return self.properties.get("LockState", None)

    @property
    def sharing_capability(self) -> Optional[SharingCapabilities]:
        """
        Determines what level of sharing is available for the site.

        The valid values are:
            - ExternalUserAndGuestSharing (default) - External user sharing (share by email) and guest link sharing
                 are both enabled.
            - Disabled - External user sharing (share by email) and guest link sharing are both disabled.
            - ExternalUserSharingOnly - External user sharing (share by email) is enabled, but guest link sharing
                 is disabled.
            - ExistingExternalUserSharingOnly - Only guests already in your organization's directory.
        """
        return self.properties.get("SharingCapability", SharingCapabilities.None_)

    @sharing_capability.setter
    def sharing_capability(self, value: SharingCapabilities) -> None:
        """Sets the level of sharing for the site."""
        self.set_property("SharingCapability", value)

    @property
    def time_zone_id(self) -> Optional[str]:
        """Gets the time zone ID of the site."""
        return self.properties.get("TimeZoneId", None)

    @property
    def entity_type_name(self) -> str:
        return "Microsoft.Online.SharePoint.TenantAdministration.SiteProperties"

    @property
    def property_ref_name(self) -> str:
        return "SiteId"

    @property
    def allow_file_archive(self) -> Optional[bool]:
        """Gets the AllowFileArchive property"""
        return self.properties.get("AllowFileArchive", None)

    @property
    def allow_web_property_bag_update_when_deny_add_and_customize_pages_is_enabled(self) -> Optional[bool]:
        """Gets the AllowWebPropertyBagUpdateWhenDenyAddAndCustomizePagesIsEnabled property"""
        return self.properties.get("AllowWebPropertyBagUpdateWhenDenyAddAndCustomizePagesIsEnabled", None)

    @property
    def anyone_link_recommended_expiration_in_days(self) -> Optional[int]:
        """Gets the AnyoneLinkRecommendedExpirationInDays property"""
        return self.properties.get("AnyoneLinkRecommendedExpirationInDays", None)

    @property
    def archived_file_disk_used(self) -> Optional[int]:
        """Gets the ArchivedFileDiskUsed property"""
        return self.properties.get("ArchivedFileDiskUsed", None)

    @property
    def archive_status(self) -> Optional[str]:
        """Gets the ArchiveStatus property"""
        return self.properties.get("ArchiveStatus", None)

    @property
    def auth_context_strength(self) -> Optional[str]:
        """Gets the AuthContextStrength property"""
        return self.properties.get("AuthContextStrength", None)

    @property
    def authentication_context_limited_access(self) -> Optional[bool]:
        """Gets the AuthenticationContextLimitedAccess property"""
        return self.properties.get("AuthenticationContextLimitedAccess", None)

    @property
    def authentication_context_name(self) -> Optional[str]:
        """Gets the AuthenticationContextName property"""
        return self.properties.get("AuthenticationContextName", None)

    @property
    def average_resource_usage(self) -> Optional[float]:
        """Gets the AverageResourceUsage property"""
        return self.properties.get("AverageResourceUsage", None)

    @property
    def block_download_policy(self) -> Optional[bool]:
        """Gets the BlockDownloadPolicy property"""
        return self.properties.get("BlockDownloadPolicy", None)

    @property
    def block_guests_as_site_admin(self) -> Optional[int]:
        """Gets the BlockGuestsAsSiteAdmin property"""
        return self.properties.get("BlockGuestsAsSiteAdmin", None)

    @property
    def bonus_disk_quota(self) -> Optional[int]:
        """Gets the BonusDiskQuota property"""
        return self.properties.get("BonusDiskQuota", None)

    @property
    def clear_group_id(self) -> Optional[bool]:
        """Gets the ClearGroupId property"""
        return self.properties.get("ClearGroupId", None)

    @property
    def clear_restricted_access_control(self) -> Optional[bool]:
        """Gets the ClearRestrictedAccessControl property"""
        return self.properties.get("ClearRestrictedAccessControl", None)

    @property
    def comments_on_site_pages_disabled(self) -> Optional[bool]:
        """Gets the CommentsOnSitePagesDisabled property"""
        return self.properties.get("CommentsOnSitePagesDisabled", None)

    @property
    def conditional_access_policy(self) -> Optional[int]:
        """Gets the ConditionalAccessPolicy property"""
        return self.properties.get("ConditionalAccessPolicy", None)

    @property
    def current_resource_usage(self) -> Optional[float]:
        """Gets the CurrentResourceUsage property"""
        return self.properties.get("CurrentResourceUsage", None)

    @property
    def default_link_permission(self) -> Optional[int]:
        """Gets the DefaultLinkPermission property"""
        return self.properties.get("DefaultLinkPermission", None)

    @property
    def default_link_to_existing_access(self) -> Optional[bool]:
        """Gets the DefaultLinkToExistingAccess property"""
        return self.properties.get("DefaultLinkToExistingAccess", None)

    @property
    def default_link_to_existing_access_reset(self) -> Optional[bool]:
        """Gets the DefaultLinkToExistingAccessReset property"""
        return self.properties.get("DefaultLinkToExistingAccessReset", None)

    @property
    def default_main_link_scope(self) -> Optional[int]:
        """Gets the DefaultMainLinkScope property"""
        return self.properties.get("DefaultMainLinkScope", None)

    @property
    def default_share_link_role(self) -> Optional[int]:
        """Gets the DefaultShareLinkRole property"""
        return self.properties.get("DefaultShareLinkRole", None)

    @property
    def default_share_link_scope(self) -> Optional[int]:
        """Gets the DefaultShareLinkScope property"""
        return self.properties.get("DefaultShareLinkScope", None)

    @property
    def default_sharing_link_type(self) -> Optional[int]:
        """Gets the DefaultSharingLinkType property"""
        return self.properties.get("DefaultSharingLinkType", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the Description property"""
        return self.properties.get("Description", None)

    @property
    def disable_app_views(self) -> Optional[int]:
        """Gets the DisableAppViews property"""
        return self.properties.get("DisableAppViews", None)

    @property
    def disable_classic_page_baseline_security_mode(self) -> Optional[bool]:
        """Gets the DisableClassicPageBaselineSecurityMode property"""
        return self.properties.get("DisableClassicPageBaselineSecurityMode", None)

    @property
    def disable_company_wide_sharing_links(self) -> Optional[int]:
        """Gets the DisableCompanyWideSharingLinks property"""
        return self.properties.get("DisableCompanyWideSharingLinks", None)

    @property
    def disable_flows(self) -> Optional[int]:
        """Gets the DisableFlows property"""
        return self.properties.get("DisableFlows", None)

    @property
    def disable_site_branding(self) -> Optional[bool]:
        """Gets the DisableSiteBranding property"""
        return self.properties.get("DisableSiteBranding", None)

    @property
    def enable_auto_expiration_version_trim(self) -> Optional[bool]:
        """Gets the EnableAutoExpirationVersionTrim property"""
        return self.properties.get("EnableAutoExpirationVersionTrim", None)

    @property
    def exclude_block_download_policy_site_owners(self) -> Optional[bool]:
        """Gets the ExcludeBlockDownloadPolicySiteOwners property"""
        return self.properties.get("ExcludeBlockDownloadPolicySiteOwners", None)

    @property
    def exclude_block_download_share_point_groups(self) -> StringCollection:
        """Gets the ExcludeBlockDownloadSharePointGroups property"""
        return self.properties.get("ExcludeBlockDownloadSharePointGroups", StringCollection())

    @property
    def excluded_block_download_group_ids(self) -> GuidCollection:
        """Gets the ExcludedBlockDownloadGroupIds property"""
        return self.properties.get("ExcludedBlockDownloadGroupIds", GuidCollection())

    @property
    def expire_versions_after_days(self) -> Optional[int]:
        """Gets the ExpireVersionsAfterDays property"""
        return self.properties.get("ExpireVersionsAfterDays", None)

    @property
    def external_user_expiration_in_days(self) -> Optional[int]:
        """Gets the ExternalUserExpirationInDays property"""
        return self.properties.get("ExternalUserExpirationInDays", None)

    @property
    def file_types_for_version_expiration(self) -> StringCollection:
        """Gets the FileTypesForVersionExpiration property"""
        return self.properties.get("FileTypesForVersionExpiration", StringCollection())

    @property
    def group_id(self) -> Optional[UUID]:
        """Gets the GroupId property"""
        return self.properties.get("GroupId", None)

    @property
    def has_holds(self) -> Optional[bool]:
        """Gets the HasHolds property"""
        return self.properties.get("HasHolds", None)

    @property
    def hide_people_previewing_files(self) -> Optional[bool]:
        """Gets the HidePeoplePreviewingFiles property"""
        return self.properties.get("HidePeoplePreviewingFiles", None)

    @property
    def hide_people_who_have_lists_open(self) -> Optional[bool]:
        """Gets the HidePeopleWhoHaveListsOpen property"""
        return self.properties.get("HidePeopleWhoHaveListsOpen", None)

    @property
    def hub_site_id(self) -> Optional[UUID]:
        """Gets the HubSiteId property"""
        return self.properties.get("HubSiteId", None)

    @property
    def ib_mode(self) -> Optional[str]:
        """Gets the IBMode property"""
        return self.properties.get("IBMode", None)

    @property
    def ib_segments(self) -> GuidCollection:
        """Gets the IBSegments property"""
        return self.properties.get("IBSegments", GuidCollection())

    @property
    def ib_segments_to_add(self) -> GuidCollection:
        """Gets the IBSegmentsToAdd property"""
        return self.properties.get("IBSegmentsToAdd", GuidCollection())

    @property
    def ib_segments_to_remove(self) -> GuidCollection:
        """Gets the IBSegmentsToRemove property"""
        return self.properties.get("IBSegmentsToRemove", GuidCollection())

    @property
    def inherit_version_policy_from_tenant(self) -> Optional[bool]:
        """Gets the InheritVersionPolicyFromTenant property"""
        return self.properties.get("InheritVersionPolicyFromTenant", None)

    @property
    def is_authoritative(self) -> Optional[bool]:
        """Gets the IsAuthoritative property"""
        return self.properties.get("IsAuthoritative", None)

    @property
    def is_group_owner_site_admin(self) -> Optional[bool]:
        """Gets the IsGroupOwnerSiteAdmin property"""
        return self.properties.get("IsGroupOwnerSiteAdmin", None)

    @property
    def is_teams_channel_connected(self) -> Optional[bool]:
        """Gets the IsTeamsChannelConnected property"""
        return self.properties.get("IsTeamsChannelConnected", None)

    @property
    def is_teams_connected(self) -> Optional[bool]:
        """Gets the IsTeamsConnected property"""
        return self.properties.get("IsTeamsConnected", None)

    @property
    def lcid(self) -> Optional[int]:
        """Gets the Lcid property"""
        return self.properties.get("Lcid", None)

    @property
    def limited_access_file_type(self) -> Optional[int]:
        """Gets the LimitedAccessFileType property"""
        return self.properties.get("LimitedAccessFileType", None)

    @property
    def lists_show_header_and_navigation(self) -> Optional[bool]:
        """Gets the ListsShowHeaderAndNavigation property"""
        return self.properties.get("ListsShowHeaderAndNavigation", None)

    @property
    def lock_issue(self) -> Optional[str]:
        """Gets the LockIssue property"""
        return self.properties.get("LockIssue", None)

    @property
    def lock_reason(self) -> Optional[int]:
        """Gets the LockReason property"""
        return self.properties.get("LockReason", None)

    @property
    def loop_default_sharing_link_role(self) -> Optional[int]:
        """Gets the LoopDefaultSharingLinkRole property"""
        return self.properties.get("LoopDefaultSharingLinkRole", None)

    @property
    def loop_default_sharing_link_scope(self) -> Optional[int]:
        """Gets the LoopDefaultSharingLinkScope property"""
        return self.properties.get("LoopDefaultSharingLinkScope", None)

    @property
    def major_version_limit(self) -> Optional[int]:
        """Gets the MajorVersionLimit property"""
        return self.properties.get("MajorVersionLimit", None)

    @property
    def major_with_minor_versions_limit(self) -> Optional[int]:
        """Gets the MajorWithMinorVersionsLimit property"""
        return self.properties.get("MajorWithMinorVersionsLimit", None)

    @property
    def media_transcription(self) -> Optional[int]:
        """Gets the MediaTranscription property"""
        return self.properties.get("MediaTranscription", None)

    @property
    def organization_link_max_expiration_in_days(self) -> Optional[int]:
        """Gets the OrganizationLinkMaxExpirationInDays property"""
        return self.properties.get("OrganizationLinkMaxExpirationInDays", None)

    @property
    def organization_link_recommended_expiration_in_days(self) -> Optional[int]:
        """Gets the OrganizationLinkRecommendedExpirationInDays property"""
        return self.properties.get("OrganizationLinkRecommendedExpirationInDays", None)

    @property
    def override_block_user_info_visibility(self) -> Optional[int]:
        """Gets the OverrideBlockUserInfoVisibility property"""
        return self.properties.get("OverrideBlockUserInfoVisibility", None)

    @property
    def override_sharing_capability(self) -> Optional[bool]:
        """Gets the OverrideSharingCapability property"""
        return self.properties.get("OverrideSharingCapability", None)

    @property
    def override_tenant_anonymous_link_expiration_policy(self) -> Optional[bool]:
        """Gets the OverrideTenantAnonymousLinkExpirationPolicy property"""
        return self.properties.get("OverrideTenantAnonymousLinkExpirationPolicy", None)

    @property
    def override_tenant_external_user_expiration_policy(self) -> Optional[bool]:
        """Gets the OverrideTenantExternalUserExpirationPolicy property"""
        return self.properties.get("OverrideTenantExternalUserExpirationPolicy", None)

    @property
    def override_tenant_organization_link_expiration_policy(self) -> Optional[bool]:
        """Gets the OverrideTenantOrganizationLinkExpirationPolicy property"""
        return self.properties.get("OverrideTenantOrganizationLinkExpirationPolicy", None)

    @property
    def owner(self) -> Optional[str]:
        """Gets the Owner property"""
        return self.properties.get("Owner", None)

    @property
    def owner_email(self) -> Optional[str]:
        """Gets the OwnerEmail property"""
        return self.properties.get("OwnerEmail", None)

    @property
    def owner_name(self) -> Optional[str]:
        """Gets the OwnerName property"""
        return self.properties.get("OwnerName", None)

    @property
    def pwa_enabled(self) -> Optional[int]:
        """Gets the PWAEnabled property"""
        return self.properties.get("PWAEnabled", None)

    @property
    def read_only_access_policy(self) -> Optional[bool]:
        """Gets the ReadOnlyAccessPolicy property"""
        return self.properties.get("ReadOnlyAccessPolicy", None)

    @property
    def read_only_for_block_download_policy(self) -> Optional[bool]:
        """Gets the ReadOnlyForBlockDownloadPolicy property"""
        return self.properties.get("ReadOnlyForBlockDownloadPolicy", None)

    @property
    def read_only_for_unmanaged_devices(self) -> Optional[bool]:
        """Gets the ReadOnlyForUnmanagedDevices property"""
        return self.properties.get("ReadOnlyForUnmanagedDevices", None)

    @property
    def related_group_id(self) -> Optional[UUID]:
        """Gets the RelatedGroupId property"""
        return self.properties.get("RelatedGroupId", None)

    @property
    def remove_version_expiration_file_type_override(self) -> StringCollection:
        """Gets the RemoveVersionExpirationFileTypeOverride property"""
        return self.properties.get("RemoveVersionExpirationFileTypeOverride", StringCollection())

    @property
    def request_files_link_enabled(self) -> Optional[bool]:
        """Gets the RequestFilesLinkEnabled property"""
        return self.properties.get("RequestFilesLinkEnabled", None)

    @property
    def request_files_link_expiration_in_days(self) -> Optional[int]:
        """Gets the RequestFilesLinkExpirationInDays property"""
        return self.properties.get("RequestFilesLinkExpirationInDays", None)

    @property
    def restrict_content_org_wide_search(self) -> Optional[bool]:
        """Gets the RestrictContentOrgWideSearch property"""
        return self.properties.get("RestrictContentOrgWideSearch", None)

    @property
    def restricted_access_control(self) -> Optional[bool]:
        """Gets the RestrictedAccessControl property"""
        return self.properties.get("RestrictedAccessControl", None)

    @property
    def restricted_access_control_groups(self) -> GuidCollection:
        """Gets the RestrictedAccessControlGroups property"""
        return self.properties.get("RestrictedAccessControlGroups", GuidCollection())

    @property
    def restricted_access_control_groups_to_add(self) -> GuidCollection:
        """Gets the RestrictedAccessControlGroupsToAdd property"""
        return self.properties.get("RestrictedAccessControlGroupsToAdd", GuidCollection())

    @property
    def restricted_access_control_groups_to_remove(self) -> GuidCollection:
        """Gets the RestrictedAccessControlGroupsToRemove property"""
        return self.properties.get("RestrictedAccessControlGroupsToRemove", GuidCollection())

    @property
    def restricted_content_discoveryfor_copilot_and_agents(self) -> Optional[bool]:
        """Gets the RestrictedContentDiscoveryforCopilotAndAgents property"""
        return self.properties.get("RestrictedContentDiscoveryforCopilotAndAgents", None)

    @property
    def restricted_to_region(self) -> Optional[int]:
        """Gets the RestrictedToRegion property"""
        return self.properties.get("RestrictedToRegion", None)

    @property
    def sandboxed_code_activation_capability(self) -> Optional[int]:
        """Gets the SandboxedCodeActivationCapability property"""
        return self.properties.get("SandboxedCodeActivationCapability", None)

    @property
    def sensitivity_label(self) -> Optional[UUID]:
        """Gets the SensitivityLabel property"""
        return self.properties.get("SensitivityLabel", None)

    @property
    def sensitivity_label2(self) -> Optional[str]:
        """Gets the SensitivityLabel2 property"""
        return self.properties.get("SensitivityLabel2", None)

    @property
    def set_owner_without_updating_secondary_admin(self) -> Optional[bool]:
        """Gets the SetOwnerWithoutUpdatingSecondaryAdmin property"""
        return self.properties.get("SetOwnerWithoutUpdatingSecondaryAdmin", None)

    @property
    def sharing_allowed_domain_list(self) -> Optional[str]:
        """Gets the SharingAllowedDomainList property"""
        return self.properties.get("SharingAllowedDomainList", None)

    @property
    def sharing_blocked_domain_list(self) -> Optional[str]:
        """Gets the SharingBlockedDomainList property"""
        return self.properties.get("SharingBlockedDomainList", None)

    @property
    def sharing_domain_restriction_mode(self) -> Optional[int]:
        """Gets the SharingDomainRestrictionMode property"""
        return self.properties.get("SharingDomainRestrictionMode", None)

    @property
    def sharing_lock_down_can_be_cleared(self) -> Optional[bool]:
        """Gets the SharingLockDownCanBeCleared property"""
        return self.properties.get("SharingLockDownCanBeCleared", None)

    @property
    def sharing_lock_down_enabled(self) -> Optional[bool]:
        """Gets the SharingLockDownEnabled property"""
        return self.properties.get("SharingLockDownEnabled", None)

    @property
    def show_people_picker_suggestions_for_guest_users(self) -> Optional[bool]:
        """Gets the ShowPeoplePickerSuggestionsForGuestUsers property"""
        return self.properties.get("ShowPeoplePickerSuggestionsForGuestUsers", None)

    @property
    def site_defined_sharing_capability(self) -> Optional[int]:
        """Gets the SiteDefinedSharingCapability property"""
        return self.properties.get("SiteDefinedSharingCapability", None)

    @property
    def site_id(self) -> Optional[UUID]:
        """Gets the SiteId property"""
        return self.properties.get("SiteId", None)

    @property
    def social_bar_on_site_pages_disabled(self) -> Optional[bool]:
        """Gets the SocialBarOnSitePagesDisabled property"""
        return self.properties.get("SocialBarOnSitePagesDisabled", None)

    @property
    def status(self) -> Optional[str]:
        """Gets the Status property"""
        return self.properties.get("Status", None)

    @property
    def storage_maximum_level(self) -> Optional[int]:
        """Gets the StorageMaximumLevel property"""
        return self.properties.get("StorageMaximumLevel", None)

    @property
    def storage_quota_type(self) -> Optional[str]:
        """Gets the StorageQuotaType property"""
        return self.properties.get("StorageQuotaType", None)

    @property
    def storage_usage(self) -> Optional[int]:
        """Gets the StorageUsage property"""
        return self.properties.get("StorageUsage", None)

    @property
    def storage_warning_level(self) -> Optional[int]:
        """Gets the StorageWarningLevel property"""
        return self.properties.get("StorageWarningLevel", None)

    @property
    def teams_channel_type(self) -> Optional[int]:
        """Gets the TeamsChannelType property"""
        return self.properties.get("TeamsChannelType", None)

    @property
    def template(self) -> Optional[str]:
        """Gets the Template property"""
        return self.properties.get("Template", None)

    @property
    def user_code_maximum_level(self) -> Optional[float]:
        """Gets the UserCodeMaximumLevel property"""
        return self.properties.get("UserCodeMaximumLevel", None)

    @property
    def user_code_warning_level(self) -> Optional[float]:
        """Gets the UserCodeWarningLevel property"""
        return self.properties.get("UserCodeWarningLevel", None)

    @property
    def version_count(self) -> Optional[int]:
        """Gets the VersionCount property"""
        return self.properties.get("VersionCount", None)

    @property
    def version_policy_file_type_override(self) -> ClientValueCollection[SPOFileVersionFileTypePolicySettings]:
        """Gets the VersionPolicyFileTypeOverride property"""
        return self.properties.get(
            "VersionPolicyFileTypeOverride",
            ClientValueCollection[SPOFileVersionFileTypePolicySettings](SPOFileVersionFileTypePolicySettings),
        )

    @property
    def version_size(self) -> Optional[int]:
        """Gets the VersionSize property"""
        return self.properties.get("VersionSize", None)

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "ArchivedTime": self.archived_time,
                "CreatedTime": self.created_time,
                "DenyAddAndCustomizePages": self.deny_add_and_customize_pages,
                "LastContentModifiedDate": self.last_content_modified_date,
                "SharingCapability": self.sharing_capability,
            }
            default_value = property_mapping.get(name, None)
        return super().get_property(name, default_value)

    @property
    def exclude_block_download_sharepoint_groups(self) -> StringCollection:
        """Gets the ExcludeBlockDownloadSharePointGroups property"""
        return self.properties.get("ExcludeBlockDownloadSharePointGroups", StringCollection())

    @property
    def file_anonymous_link_type(self) -> Optional[int]:
        """Gets the FileAnonymousLinkType property"""
        return self.properties.get("FileAnonymousLinkType", None)

    @property
    def folder_anonymous_link_type(self) -> Optional[int]:
        """Gets the FolderAnonymousLinkType property"""
        return self.properties.get("FolderAnonymousLinkType", None)
