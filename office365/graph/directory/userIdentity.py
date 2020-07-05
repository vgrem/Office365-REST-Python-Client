from office365.runtime.clientValue import ClientValue


class UserIdentity(ClientValue):

    def __init__(self):
        super().__init__()
        self.displayName = None
        self.ipAddress = None
        self.userPrincipalName = None
