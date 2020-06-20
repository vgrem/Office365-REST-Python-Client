from office365.runtime.clientValue import ClientValue


class SharingLinkInfo(ClientValue):

    def __init__(self):
        self.AllowsAnonymousAccess = None
        self.ApplicationId = None
        self.CreatedBy = None
