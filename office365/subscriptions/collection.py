from office365.entity_collection import EntityCollection
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.subscriptions.subscription import Subscription


class SubscriptionCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(SubscriptionCollection, self).__init__(context, Subscription, resource_path)

    def add(self, change_type, notification_url, resource_path, expiration, client_state=None,
            latest_supported_tls_version=None):
        """
        Subscribes a listener application to receive change notifications when the requested type of changes occur
        to the specified resource in Microsoft Graph.

        :param str change_type:
        :param str notification_url:
        :param ResourcePath resource_path:
        :param datetime.datetime expiration:
        :param str client_state:
        :param str latest_supported_tls_version:
        """
        return_type = Subscription(self.context)
        self.add_child(return_type)
        payload = {
            "changeType": change_type,
            "notificationUrl": notification_url,
            "resource": str(resource_path),
            "expirationDateTime": expiration.isoformat() + "Z",
            "clientState": client_state,
            "latestSupportedTlsVersion": latest_supported_tls_version
        }
        qry = CreateEntityQuery(self, payload, return_type)
        self.context.add_query(qry)
        return return_type
