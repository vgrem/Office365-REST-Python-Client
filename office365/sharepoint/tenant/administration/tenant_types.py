from office365.runtime.client_value import ClientValue
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sites.site_types import SiteCollectionAppCatalogAllowedItems


class TenantWebTemplate(ClientValue):

    def __init__(self):
        super(TenantWebTemplate, self).__init__()

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.SPOTenantWebTemplate"


class TenantAdminEndpoints(BaseEntity):
    pass


class TenantCorporateCatalogAccessor(BaseEntity):

    @property
    def site_collection_app_catalogs_sites(self):
        """Get recycle bin"""
        return self.properties.get('SiteCollectionAppCatalogsSites',
                                   SiteCollectionAppCatalogAllowedItems(self.context,
                                                                        ResourcePath("SiteCollectionAppCatalogsSites",
                                                                                     self.resource_path)))
