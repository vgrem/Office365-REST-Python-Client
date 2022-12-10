from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.pushnotifications.subscriber import PushNotificationSubscriber


class PushNotificationSubscriberCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(PushNotificationSubscriberCollection, self).__init__(context, PushNotificationSubscriber, resource_path)

    def get_by_store_id(self, _id):
        """
        Returns the push notification subscriber from the specified store identifier.

        :param str _id: Store identifier for the notification subscriber.
        """
        return PushNotificationSubscriber(self.context, ServiceOperationPath("GetByStoreId", [_id], self.resource_path))
