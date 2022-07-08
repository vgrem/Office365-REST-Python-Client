from office365.entity import Entity
from office365.onedrive.driveitems.publication_facet import PublicationFacet


class BaseItemVersion(Entity):
    """Represents a previous version of an item or entity."""

    @property
    def last_modified_datetime(self):
        """Gets date and time the item was last modified."""
        return self.properties.get('lastModifiedDateTime', 	None)

    @property
    def publication(self):
        """Indicates the publication status of this particular version. Read-only."""
        return self.properties.get('publication', PublicationFacet())
