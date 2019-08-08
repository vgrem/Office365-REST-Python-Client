from office365.onedrive.base_item import BaseItem


class Site(BaseItem):
    """The site resource provides metadata and relationships for a SharePoint site. """

    @property
    def sharepointids(self):
        """Returns identifiers useful for SharePoint REST compatibility."""
        if self.is_property_available("sharepointIds"):
            return self.properties['sharepointIds']
        return None
