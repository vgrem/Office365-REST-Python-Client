from office365.runtime.client_value import ClientValue


class UserIdInfo(ClientValue):

    def __init__(self):
        """Represents an identity providers unique identifier information"""
        super(UserIdInfo, self).__init__()
        self.NameId = None
        self.NameIdIssuer = None
