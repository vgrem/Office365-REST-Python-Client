from office365.runtime.client_value import ClientValue


class DriveRecipient(ClientValue):
    """
    The DriveRecipient resource represents a person, group, or other recipient to
    share with using the invite action.
    """

    def __init__(self):
        super(DriveRecipient, self).__init__()
        self.alias = None
        self.email = None
        self.objectId = None
