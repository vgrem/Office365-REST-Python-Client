from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.sharing.invitation.link import LinkInvitation


class SharingLinkInfo(ClientValue):

    def __init__(self, allows_anonymous_access=None, application_id=None):
        """
        Specifies the information about the tokenized sharing link.

        :param bool allows_anonymous_access:
        :param str application_id:
        """
        super(SharingLinkInfo, self).__init__()
        self.AllowsAnonymousAccess = allows_anonymous_access
        self.ApplicationId = application_id
        self.CreatedBy = None
        self.PasswordProtected = None
        self.Invitations = ClientValueCollection(LinkInvitation)

    @property
    def entity_type_name(self):
        return "SP.Sharing.LinkInvitation"
