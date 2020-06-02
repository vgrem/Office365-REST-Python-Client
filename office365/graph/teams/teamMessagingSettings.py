from office365.runtime.client_value_object import ClientValueObject


class TeamMessagingSettings(ClientValueObject):

    def __init__(self):
        self.allowUserEditMessages = True
