from office365.runtime.client_value import ClientValue


class GroupProfile(ClientValue):
    def __init__(self, name, description=None, mail_enabled=False, security_enabled=True):
        """

        :param str name: Group name
        """
        super(GroupProfile, self).__init__()
        self.mailNickname = name
        self.displayName = name
        self.description = description
        self.mailEnabled = mail_enabled
        self.securityEnabled = security_enabled
        self.owners = None
        self.members = None
        self.groupTypes = None
