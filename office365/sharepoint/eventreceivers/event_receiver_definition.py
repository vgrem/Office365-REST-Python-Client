from office365.runtime.client_value import ClientValue
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.base_entity_collection import BaseEntityCollection


class EventReceiverDefinitionCreationInformation(ClientValue):
    """Represents the properties that can be set when creating a client-side event receiver definition."""
    pass


class EventReceiverDefinition(BaseEntity):
    """Abstract base class that defines general properties of an event receiver for list items, lists,
    websites, and workflows."""

    @property
    def receiver_url(self):
        """Gets the URL of the receiver for the event.

        :rtype: str or None
        """
        return self.properties.get('ReceiverUrl', None)


class EventReceiverDefinitionCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None, parent=None):
        super(EventReceiverDefinitionCollection, self).__init__(context, EventReceiverDefinition, resource_path, parent)
