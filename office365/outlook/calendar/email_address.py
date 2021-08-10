from office365.runtime.client_value import ClientValue


class EmailAddress(ClientValue):
    """The name and email address of a contact or message recipient."""

    def __init__(self, address=None, name=None):
        super(EmailAddress, self).__init__()
        self.address = address
        self.name = name
