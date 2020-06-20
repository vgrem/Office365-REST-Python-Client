from office365.runtime.clientValue import ClientValue


class DriveRecipient(ClientValue):

    def __init__(self):
        super(DriveRecipient, self).__init__()
        self.alias = None
        self.email = None
        self.objectId = None
