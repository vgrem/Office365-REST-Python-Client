from office365.runtime.client_value import ClientValue


class SharingLinkAccessRequest(ClientValue):
    """Represents extended values to include in a request for access to an object exposed through a tokenized
    sharing link."""

    def __init__(self):
        super(SharingLinkAccessRequest, self).__init__()
        self.ensureAccess = None
        self.password = None
