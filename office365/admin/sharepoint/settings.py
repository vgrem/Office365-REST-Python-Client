from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from office365.admin.sharepoint.idle_session_signout import IdleSessionSignOut
from office365.entity import Entity
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.admin.sharepoint.imagetaggingchoice import ImageTaggingChoice


class SharepointSettings(Entity):
    """Represents the tenant-level settings for SharePoint and OneDrive."""

    @odata(name="allowedDomainGuidsForSyncApp")
    @property
    def allowed_domain_guids_for_sync_app(self) -> StringCollection:
        """Collection of trusted domain GUIDs for the OneDrive sync app."""
        return self.properties.get("allowedDomainGuidsForSyncApp", StringCollection())

    @odata(name="availableManagedPathsForSiteCreation")
    @property
    def available_managed_paths_for_site_creation(self) -> StringCollection:
        """Collection of managed paths available for site creation."""
        return self.properties.get("availableManagedPathsForSiteCreation", StringCollection())

    @odata(name="excludedFileExtensionsForSyncApp")
    @property
    def excluded_file_extensions_for_sync_app(self) -> StringCollection:
        """Collection of file extensions not uploaded by the OneDrive sync app."""
        return self.properties.get("excludedFileExtensionsForSyncApp", StringCollection())

    @odata(name="idleSessionSignOut")
    @property
    def idle_session_sign_out(self) -> IdleSessionSignOut:
        """Specifies the idle session sign-out policies for the tenant."""
        return self.properties.get("idleSessionSignOut", IdleSessionSignOut())

    @property
    def is_commenting_on_site_pages_enabled(self) -> Optional[bool]:
        """Indicates whether comments are allowed on modern site pages in SharePoint."""
        return self.properties.get("isCommentingOnSitePagesEnabled", None)

    @property
    def is_legacy_auth_protocols_enabled(self) -> Optional[bool]:
        """Indicates whether legacy authentication protocols are enabled for the tenant."""
        return self.properties.get("isLegacyAuthProtocolsEnabled", None)

    @odata(name="sharingAllowedDomainList")
    @property
    def sharing_allowed_domain_list(self) -> StringCollection:
        """
        Collection of email domains that are allowed for sharing outside the organization.
        """
        return self.properties.get("sharingAllowedDomainList", StringCollection())

    @odata(name="sharingBlockedDomainList")
    @property
    def sharing_blocked_domain_list(self) -> StringCollection:
        """
        Collection of email domains that are blocked for sharing outside the organization.
        """
        return self.properties.get("sharingBlockedDomainList", StringCollection())

    @sharing_blocked_domain_list.setter
    def sharing_blocked_domain_list(self, value: List[str]) -> None:
        """Sets the collection of email domains that are blocked for sharing outside the organization."""
        self.set_property("sharingBlockedDomainList", value)

    @property
    def sharing_capability(self) -> Optional[str]:
        """
        Sharing capability for the tenant.
        Possible values are:
            disabled,
            externalUserSharingOnly,
            externalUserAndGuestSharing,
            existingExternalUserSharingOnly.
        """
        return self.properties.get("sharingCapability", None)

    @property
    def sharing_domain_restriction_mode(self) -> Optional[str]:
        """
        Specifies the external sharing mode for domains. Possible values are: none, allowList, blockList.
        """
        return self.properties.get("sharingDomainRestrictionMode", None)

    @property
    def site_creation_default_managed_path(self) -> Optional[str]:
        """
        The value of the team site managed path. This is the path under which new team sites will be created.
        """
        return self.properties.get("siteCreationDefaultManagedPath", None)

    @property
    def site_creation_default_storage_limit_in_mb(self) -> Optional[int]:
        """The default storage quota for a new site upon creation. Measured in megabytes (MB)."""
        return self.properties.get("siteCreationDefaultStorageLimitInMB", None)

    @property
    def tenant_default_timezone(self) -> Optional[str]:
        """
        The default timezone of a tenant for newly created sites. For a list of possible values,
        see SPRegionalSettings.TimeZones property.
        """
        return self.properties.get("tenantDefaultTimezone", None)

    @property
    def entity_type_name(self) -> str:
        return None  # type: ignore

    @property
    def deleted_user_personal_site_retention_period_in_days(self) -> Optional[int]:
        """Gets the deletedUserPersonalSiteRetentionPeriodInDays property"""
        return self.properties.get("deletedUserPersonalSiteRetentionPeriodInDays", None)

    @property
    def image_tagging_option(self) -> ImageTaggingChoice:
        """Gets the imageTaggingOption property"""
        from office365.admin.sharepoint.imagetaggingchoice import ImageTaggingChoice

        return self.properties.get("imageTaggingOption", ImageTaggingChoice.disabled)

    @property
    def is_file_activity_notification_enabled(self) -> Optional[bool]:
        """Gets the isFileActivityNotificationEnabled property"""
        return self.properties.get("isFileActivityNotificationEnabled", None)

    @property
    def is_loop_enabled(self) -> Optional[bool]:
        """Gets the isLoopEnabled property"""
        return self.properties.get("isLoopEnabled", None)

    @property
    def is_mac_sync_app_enabled(self) -> Optional[bool]:
        """Gets the isMacSyncAppEnabled property"""
        return self.properties.get("isMacSyncAppEnabled", None)

    @property
    def is_require_accepting_user_to_match_invited_user_enabled(self) -> Optional[bool]:
        """Gets the isRequireAcceptingUserToMatchInvitedUserEnabled property"""
        return self.properties.get("isRequireAcceptingUserToMatchInvitedUserEnabled", None)

    @property
    def is_resharing_by_external_users_enabled(self) -> Optional[bool]:
        """Gets the isResharingByExternalUsersEnabled property"""
        return self.properties.get("isResharingByExternalUsersEnabled", None)

    @property
    def is_sharepoint_mobile_notification_enabled(self) -> Optional[bool]:
        """Gets the isSharePointMobileNotificationEnabled property"""
        return self.properties.get("isSharePointMobileNotificationEnabled", None)

    @property
    def is_sharepoint_newsfeed_enabled(self) -> Optional[bool]:
        """Gets the isSharePointNewsfeedEnabled property"""
        return self.properties.get("isSharePointNewsfeedEnabled", None)

    @property
    def is_site_creation_enabled(self) -> Optional[bool]:
        """Gets the isSiteCreationEnabled property"""
        return self.properties.get("isSiteCreationEnabled", None)

    @property
    def is_site_creation_ui_enabled(self) -> Optional[bool]:
        """Gets the isSiteCreationUIEnabled property"""
        return self.properties.get("isSiteCreationUIEnabled", None)

    @property
    def is_site_pages_creation_enabled(self) -> Optional[bool]:
        """Gets the isSitePagesCreationEnabled property"""
        return self.properties.get("isSitePagesCreationEnabled", None)

    @property
    def is_sites_storage_limit_automatic(self) -> Optional[bool]:
        """Gets the isSitesStorageLimitAutomatic property"""
        return self.properties.get("isSitesStorageLimitAutomatic", None)

    @property
    def is_sync_button_hidden_on_personal_site(self) -> Optional[bool]:
        """Gets the isSyncButtonHiddenOnPersonalSite property"""
        return self.properties.get("isSyncButtonHiddenOnPersonalSite", None)

    @property
    def is_unmanaged_sync_app_for_tenant_restricted(self) -> Optional[bool]:
        """Gets the isUnmanagedSyncAppForTenantRestricted property"""
        return self.properties.get("isUnmanagedSyncAppForTenantRestricted", None)

    @property
    def personal_site_default_storage_limit_in_mb(self) -> Optional[int]:
        """Gets the personalSiteDefaultStorageLimitInMB property"""
        return self.properties.get("personalSiteDefaultStorageLimitInMB", None)
