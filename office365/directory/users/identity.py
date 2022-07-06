from office365.runtime.client_value import ClientValue


class UserIdentity(ClientValue):
    """
    In the context of an Azure AD audit log, this represents the user information that initiated or
    was affected by an audit activity.
    """

    def __init__(self):
        super(UserIdentity, self).__init__()
        self.displayName = None
        self.ipAddress = None
        self.userPrincipalName = None
