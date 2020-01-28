from office365.onedrive.baseItem import BaseItem
from office365.onedrive.drive import Drive
from office365.onedrive.listCollection import ListCollection
from office365.runtime.resource_path_entity import ResourcePathEntity


class Site(BaseItem):
    """The site resource provides metadata and relationships for a SharePoint site. """

    @property
    def lists(self):
        """The collection of lists under this site."""
        if self.is_property_available('lists'):
            return self.properties['lists']
        else:
            return ListCollection(self.context, ResourcePathEntity(self.context, self.resourcePath, "lists"))

    @property
    def drive(self):
        """The default drive (document library) for this site."""
        if self.is_property_available('drive'):
            return self.properties['drive']
        else:
            return Drive(self.context, ResourcePathEntity(self.context, self.resourcePath, "drive"))

    @property
    def sharepointids(self):
        """Returns identifiers useful for SharePoint REST compatibility."""
        if self.is_property_available("sharepointIds"):
            return self.properties['sharepointIds']
        return None
