from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.webhooks.subscription import Subscription
from office365.sharepoint.webhooks.subscription_information import SubscriptionInformation


class SubscriptionCollection(BaseEntityCollection):
    """Represents a collection of Subscription (WebHook) resources."""

    def __init__(self, context, resource_path=None, parent=None):
        super(SubscriptionCollection, self).__init__(context, Subscription, resource_path, parent)

    def get_by_id(self, _id):
        """Gets the subscription with the specified ID."""
        return Subscription(self.context, ServiceOperationPath("getById", [_id], self.resource_path))

    def add(self, information_or_notification):
        """
        :type information_or_notification: SubscriptionInformation or str
        """
        return_type = Subscription(self.context)
        self.add_child(return_type)
        if isinstance(information_or_notification, SubscriptionInformation):
            qry = ServiceOperationQuery(self, "Add", None, information_or_notification, "parameters", return_type)
            self.context.add_query(qry)
        else:
            def _parent_loaded():
                information = SubscriptionInformation(information_or_notification, self._parent.properties["Id"])
                next_qry = ServiceOperationQuery(self, "Add", None, information, "parameters", return_type)
                self.context.add_query(next_qry)
            self._parent.ensure_property("Id", _parent_loaded)
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
