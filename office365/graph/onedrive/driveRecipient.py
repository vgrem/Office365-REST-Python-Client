from office365.runtime.client_value_object import ClientValueObject


class DriveRecipient(ClientValueObject):

    def __init__(self):
        super(DriveRecipient, self).__init__()
        self.alias = None
        self.email = None
        self.objectId = None
