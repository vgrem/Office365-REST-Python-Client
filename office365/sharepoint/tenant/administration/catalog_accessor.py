from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sites.site_types import SiteCollectionAppCatalogAllowedItems


class TenantCorporateCatalogAccessor(BaseEntity):
    """Accessor for the tenant corporate catalog."""

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
