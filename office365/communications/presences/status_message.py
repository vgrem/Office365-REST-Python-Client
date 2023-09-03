from office365.outlook.mail.item_body import ItemBody
from office365.runtime.client_value import ClientValue


class PresenceStatusMessage(ClientValue):
    """Represents a presence status message related to the presence of a user in Microsoft Teams."""

    def __init__(self, message=ItemBody()):
        """
        :param ItemBody message: Status message item.
        """
        self.message = message
