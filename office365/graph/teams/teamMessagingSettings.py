from office365.runtime.clientValue import ClientValue


class TeamMessagingSettings(ClientValue):

    def __init__(self):
        super().__init__()
        self.allowUserEditMessages = True
