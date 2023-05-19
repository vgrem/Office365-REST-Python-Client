from office365.entity import Entity
from office365.runtime.types.collections import StringCollection


class SharepointSettings(Entity):
    """Represents the tenant-level settings for SharePoint and OneDrive."""

    @property
    def allowed_domain_guids_for_sync_app(self):
        """Collection of trusted domain GUIDs for the OneDrive sync app."""
        return self.properties.get("allowedDomainGuidsForSyncApp", StringCollection())

    @property
    def available_managed_paths_for_site_creation(self):
        """Collection of managed paths available for site creation. """
        return self.properties.get("availableManagedPathsForSiteCreation", StringCollection())

    @property
    def excluded_file_extensions_for_sync_app(self):
        """Collection of file extensions not uploaded by the OneDrive sync app. """
        return self.properties.get("excludedFileExtensionsForSyncApp", StringCollection())

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "allowedDomainGuidsForSyncApp": self.allowed_domain_guids_for_sync_app,
                "availableManagedPathsForSiteCreation": self.available_managed_paths_for_site_creation,
                "excludedFileExtensionsForSyncApp": self.excluded_file_extensions_for_sync_app
            }
            default_value = property_mapping.get(name, None)
        return super(SharepointSettings, self).get_property(name, default_value)
