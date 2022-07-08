from office365.sharepoint.base_entity import BaseEntity


class EventReceiverDefinition(BaseEntity):
    """Abstract base class that defines general properties of an event receiver for list items, lists,
    websites, and workflows."""

    @property
    def receiver_assembly(self):
        """Specifies the strong name of the assembly that is used for the event receiver.

        :rtype: str or None
        """
        return self.properties.get('ReceiverAssembly', None)

    @property
    def receiver_class(self):
        """Specifies the strong name of the assembly that is used for the event receiver.

        :rtype: str or None
        """
        return self.properties.get('ReceiverClass', None)

    @property
    def receiver_url(self):
        """Gets the URL of the receiver for the event.

        :rtype: str or None
        """
        return self.properties.get('ReceiverUrl', None)


