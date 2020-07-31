from office365.runtime.client_value import ClientValue


class SharingLinkInfo(ClientValue):

    def __init__(self):
        """
        Specifies the information about the tokenized sharing link.

        """
        super().__init__()
        self.AllowsAnonymousAccess = None
        self.ApplicationId = None
        self.CreatedBy = None
        self.PasswordProtected = None
