from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.publishing.pages.metadata import SitePageMetadata


class SitePageMetadataCollection(BaseEntityCollection):
    """Specifies a collection of site pages."""

    def get_by_id(self, site_page_id):
        """Gets the site page with the specified ID.

        :param int site_page_id: Specifies the identifier of the site page.
        """
        return SitePageMetadata(self.context, ServiceOperationPath("GetById", [site_page_id], self.resource_path))
