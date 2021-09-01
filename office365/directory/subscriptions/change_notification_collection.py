from office365.runtime.client_value import ClientValue


class ChangeNotificationCollection(ClientValue):
    """Represents a collection of resource change notifications sent to the subscriber."""

    def __init__(self, validation_tokens=None, value=None):
        super(ChangeNotificationCollection, self).__init__()
        self.validationTokens = validation_tokens
        self.value = value
