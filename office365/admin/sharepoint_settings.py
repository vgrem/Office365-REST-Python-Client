from typing import Optional

from office365.entity import Entity
from office365.onedrive.idle_session_signout import IdleSessionSignOut
from office365.runtime.types.collections import StringCollection


class SharepointSettings(Entity):
    """Represents the tenant-level settings for SharePoint and OneDrive."""

    @property
    def allowed_domain_guids_for_sync_app(self):
        """Collection of trusted domain GUIDs for the OneDrive sync app."""
        return self.properties.get("allowedDomainGuidsForSyncApp", StringCollection())

    @property
    def available_managed_paths_for_site_creation(self):
        """Collection of managed paths available for site creation."""
        return self.properties.get(
            "availableManagedPathsForSiteCreation", StringCollection()
        )

    @property
    def excluded_file_extensions_for_sync_app(self):
        """Collection of file extensions not uploaded by the OneDrive sync app."""
        return self.properties.get(
            "excludedFileExtensionsForSyncApp", StringCollection()
        )

    @property
    def idle_session_sign_out(self):
        # type: () -> IdleSessionSignOut
        """Specifies the idle session sign-out policies for the tenant."""
        return self.properties.get("idleSessionSignOut", IdleSessionSignOut())

    @property
    def is_commenting_on_site_pages_enabled(self):
        # type: () -> Optional[bool]
        """Indicates whether comments are allowed on modern site pages in SharePoint."""
        return self.properties.get("isCommentingOnSitePagesEnabled", None)

    @property
    def site_creation_default_managed_path(self):
        # type: () -> Optional[str]
        """
        The value of the team site managed path. This is the path under which new team sites will be created.
        """
        return self.properties.get("siteCreationDefaultManagedPath", None)

    @property
    def site_creation_default_storage_limit_in_mb(self):
        # type: () -> Optional[int]
        """The default storage quota for a new site upon creation. Measured in megabytes (MB)."""
        return self.properties.get("siteCreationDefaultStorageLimitInMB", None)

    @property
    def tenant_default_timezone(self):
        # type: () -> Optional[str]
        """
        The default timezone of a tenant for newly created sites. For a list of possible values,
        see SPRegionalSettings.TimeZones property.
        """
        return self.properties.get("tenantDefaultTimezone", None)

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "allowedDomainGuidsForSyncApp": self.allowed_domain_guids_for_sync_app,
                "availableManagedPathsForSiteCreation": self.available_managed_paths_for_site_creation,
                "excludedFileExtensionsForSyncApp": self.excluded_file_extensions_for_sync_app,
            }
            default_value = property_mapping.get(name, None)
        return super(SharepointSettings, self).get_property(name, default_value)
