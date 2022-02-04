from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.sharing.link_invitation import LinkInvitation


class SharingLinkInfo(ClientValue):

    def __init__(self):
        """
        Specifies the information about the tokenized sharing link.

        """
        super(SharingLinkInfo, self).__init__()
        self.AllowsAnonymousAccess = None
        self.ApplicationId = None
        self.CreatedBy = None
        self.PasswordProtected = None
        self.Invitations = ClientValueCollection(LinkInvitation)
