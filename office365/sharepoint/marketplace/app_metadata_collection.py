from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.marketplace.app_metadata import CorporateCatalogAppMetadata


class CorporateCatalogAppMetadataCollection(BaseEntityCollection):
    """Collection of app metadata."""

    def __init__(self, context, resource_path=None):
        super(CorporateCatalogAppMetadataCollection, self).__init__(context, CorporateCatalogAppMetadata, resource_path)

    def get_by_id(self, app_id):
        """
        Get app metadata by id.

        :param str app_id: The identifier of the app to retrieve.
        """
        return CorporateCatalogAppMetadata(self.context, ServiceOperationPath("GetById", [app_id], self.resource_path))
