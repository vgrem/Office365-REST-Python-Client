from office365.runtime.clientValue import ClientValue


class GroupProfile(ClientValue):
    def __init__(self, name):
        """

        :param str name: Group name
        """
        super(GroupProfile, self).__init__()
        self.mailNickname = name
        self.displayName = name
        self.description = None
        self.mailEnabled = False
        self.securityEnabled = True
        self.owners = []
        self.members = []
        self.groupTypes = []
