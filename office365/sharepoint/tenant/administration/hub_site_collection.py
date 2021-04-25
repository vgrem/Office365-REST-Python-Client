from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.tenant.administration.hub_site import HubSite


class HubSiteCollection(BaseEntityCollection):
    """Represents a collection of HubSite resources."""

    def __init__(self, context, resource_path=None):
        super(HubSiteCollection, self).__init__(context, HubSite, resource_path)
