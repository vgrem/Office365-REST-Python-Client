from office365.runtime.client_value import ClientValue


class GroupProfile(ClientValue):
    def __init__(self, name, description=None, mailEnabled=False, securityEnabled=True):
        """

        :param str name: Group name
        """
        super(GroupProfile, self).__init__()
        self.mailNickname = name
        self.displayName = name
        self.description = description
        self.mailEnabled = mailEnabled
        self.securityEnabled = securityEnabled
        self.owners = []
        self.members = []
        self.groupTypes = []
