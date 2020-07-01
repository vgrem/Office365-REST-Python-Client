from office365.runtime.clientValue import ClientValue


class SharingLinkInfo(ClientValue):

    def __init__(self):
        super().__init__()
        self.AllowsAnonymousAccess = None
        self.ApplicationId = None
        self.CreatedBy = None
        self.PasswordProtected = None
