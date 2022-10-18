from office365.runtime.client_value import ClientValue


class LinkInvitation(ClientValue):
    """This class is used to identify the specific invitees for a tokenized sharing link,
    along with who invited them and when."""

    def __init__(self):
        super(LinkInvitation, self).__init__()
