from office365.runtime.client_value import ClientValue


class DriveRecipient(ClientValue):

    def __init__(self):
        super(DriveRecipient, self).__init__()
        self.alias = None
        self.email = None
        self.objectId = None
