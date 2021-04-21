from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.webhooks.subscription import Subscription


class SubscriptionCollection(BaseEntityCollection):
    """Represents a collection of Subscription (WebHook) resources."""

    def __init__(self, context, resource_path=None):
        super(SubscriptionCollection, self).__init__(context, Subscription, resource_path)

    def get_by_id(self, _id):
        """Gets the subscription with the specified ID."""
        return Subscription(self.context, ResourcePathServiceOperation("getById", [_id], self.resource_path))

    def add(self, information):
        """
        :type information: office365.sharepoint.webhooks.subscription_information.SubscriptionInformation
        """
        return_type = Subscription(self.context)
        qry = ServiceOperationQuery(self, "Add", None, information, "parameters", return_type)
        self.context.add_query(qry)
        return return_type

    def remove(self, subscription_id):
        """Removes the subscription with the specified subscriptionId from the collection.

        :param str subscription_id: The ID of the subscription.
        """
        payload = {
            "subscriptionId": subscription_id,
        }
        qry = ServiceOperationQuery(self, "Remove", payload, None, None, None)
        self.context.add_query(qry)
        return self
