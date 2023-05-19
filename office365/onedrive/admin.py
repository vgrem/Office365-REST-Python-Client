from office365.entity import Entity
from office365.onedrive.sharepoint import Sharepoint
from office365.runtime.paths.resource_path import ResourcePath


class Admin(Entity):
    """Entity that acts as a container for administrator functionality."""

    @property
    def sharepoint(self):
        """A container for administrative resources to manage tenant-level settings for SharePoint and OneDrive."""
        return self.properties.get('sharepoint',
                                   Sharepoint(self.context, ResourcePath("sharepoint", self.resource_path)))
