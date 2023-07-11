from office365.entity import Entity
from office365.intune.servicecommunications.announcement import ServiceAnnouncement
from office365.onedrive.sharepoint import Sharepoint
from office365.runtime.paths.resource_path import ResourcePath


class Admin(Entity):
    """Entity that acts as a container for administrator functionality."""

    @property
    def sharepoint(self):
        """A container for administrative resources to manage tenant-level settings for SharePoint and OneDrive."""
        return self.properties.get('sharepoint',
                                   Sharepoint(self.context, ResourcePath("sharepoint", self.resource_path)))

    @property
    def service_announcement(self):
        """A container for service communications resources. Read-only."""
        return self.properties.get('serviceAnnouncement',
                                   ServiceAnnouncement(self.context,
                                                       ResourcePath("serviceAnnouncement", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "serviceAnnouncement": self.service_announcement
            }
            default_value = property_mapping.get(name, None)
        return super(Admin, self).get_property(name, default_value)
