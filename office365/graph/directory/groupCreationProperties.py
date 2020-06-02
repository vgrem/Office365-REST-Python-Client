from office365.runtime.client_value_object import ClientValueObject


class GroupCreationProperties(ClientValueObject):
    def __init__(self, name):
        super(GroupCreationProperties, self).__init__()
        self.mailNickname = name
        self.displayName = name
        self.description = None
        self.mailEnabled = False
        self.securityEnabled = True
        self.owners = []
        self.members = []
        self.groupTypes = []
