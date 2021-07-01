from office365.calendar.emailAddress import EmailAddress
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


class Recipient(ClientValue):
    """Represents information about a user in the sending or receiving end of an event, message or group post."""

    def __init__(self, emailAddress=EmailAddress()):
        """

        :param EmailAddress emailAddress: The recipient's email address.
        """
        super(Recipient, self).__init__()
        self.emailAddress = emailAddress


class RecipientCollection(ClientValueCollection):

    def __init__(self, default_values=None):
        super(RecipientCollection,self).__init__(Recipient, default_values)

    @staticmethod
    def from_emails(values):
        recipients = [Recipient(EmailAddress(email)) for email in values]
        return RecipientCollection(recipients)
