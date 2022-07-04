from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.marketplace.sitecollection.appcatalog.allowed_items import \
    SiteCollectionAppCatalogAllowedItems
from office365.sharepoint.marketplace.app_metadata import CorporateCatalogAppMetadata


class TenantCorporateCatalogAccessor(BaseEntity):
    """Accessor for the tenant corporate catalog."""

    def get_app_by_id(self, item_unique_id):
        """
        :param str item_unique_id:
        """
        payload = {"itemUniqueId": item_unique_id}
        return_type = CorporateCatalogAppMetadata(self.context)
        qry = ServiceOperationQuery(self, "GetAppById", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def site_collection_app_catalogs_sites(self):
        """Get recycle bin"""
        return self.properties.get('SiteCollectionAppCatalogsSites',
                                   SiteCollectionAppCatalogAllowedItems(self.context,
                                                                        ResourcePath("SiteCollectionAppCatalogsSites",
                                                                                     self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "SiteCollectionAppCatalogsSites": self.site_collection_app_catalogs_sites
            }
            default_value = property_mapping.get(name, None)
        return super(TenantCorporateCatalogAccessor, self).get_property(name, default_value)
