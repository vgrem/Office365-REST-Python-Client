from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.webhooks.subscription import Subscription


class SubscriptionCollection(ClientObjectCollection):
    """Represents a collection of View resources."""

    def __init__(self, context, resource_path=None):
        super(SubscriptionCollection, self).__init__(context, Subscription, resource_path)
