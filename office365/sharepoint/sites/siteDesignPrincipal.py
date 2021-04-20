from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.base_entity_collection import BaseEntityCollection


class SiteDesignPrincipal(BaseEntity):
    pass


class SiteDesignPrincipalCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(SiteDesignPrincipalCollection, self).__init__(context, SiteDesignPrincipal, resource_path)
