from office365.outlook.calendar.email_address import EmailAddress
from office365.runtime.client_value import ClientValue


class Recipient(ClientValue):
    """Represents information about a user in the sending or receiving end of an event, message or group post."""

    def __init__(self, email_address=EmailAddress()):
        """
        :param EmailAddress email_address: The recipient's email address.
        """
        super(Recipient, self).__init__()
        self.emailAddress = email_address

    @staticmethod
    def from_email(value):
        """
        :type value: str or EmailAddress
        """
        if isinstance(value, EmailAddress):
            return Recipient(value)
        else:
            return Recipient(EmailAddress(value))
