from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.tenant.administration.hub_site import HubSite


class HubSiteCollection(ClientObjectCollection):
    """Represents a collection of HubSite resources."""

    def __init__(self, context, resource_path=None):
        super(HubSiteCollection, self).__init__(context, HubSite, resource_path)
