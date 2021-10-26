from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.publishing.site_page_metadata import SitePageMetadata


class SitePageMetadataCollection(BaseEntityCollection):
    """Specifies a collection of site pages."""

    def __init__(self, context, resource_path=None):
        """Specifies a collection of site pages."""
        super(SitePageMetadataCollection, self).__init__(context, SitePageMetadata, resource_path)
