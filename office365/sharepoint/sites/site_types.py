from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.base_entity_collection import BaseEntityCollection


class SiteCollectionCorporateCatalogAccessor(BaseEntity):
    pass


class SiteCollectionAppCatalogAllowedItem(BaseEntity):
    pass


class SiteCollectionAppCatalogAllowedItems(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(SiteCollectionAppCatalogAllowedItems, self).__init__(context, SiteCollectionAppCatalogAllowedItem,
                                                                   resource_path)
