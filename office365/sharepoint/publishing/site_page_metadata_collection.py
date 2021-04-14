from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.publishing.site_page_metadata import SitePageMetadata


class SitePageMetadataCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        """Specifies a collection of site pages."""
        super(SitePageMetadataCollection, self).__init__(context, SitePageMetadata, resource_path)
