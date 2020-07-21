from office365.runtime.clientValue import ClientValue


class UserIdInfo(ClientValue):

    def __init__(self):
        """Represents an identity provider’s unique identifier information."""
        super().__init__()
        self.NameId = None
        self.NameIdIssuer = None
