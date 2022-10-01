from office365.runtime.client_value import ClientValue


class DriveRecipient(ClientValue):
    """
    The DriveRecipient resource represents a person, group, or other recipient to
    share with using the invite action.
    """

    def __init__(self, alias=None, email=None, object_id=None):
        """

        """
        super(DriveRecipient, self).__init__()
        self.alias = alias
        self.email = email
        self.objectId = object_id

    @staticmethod
    def from_email(value):
        return DriveRecipient(email=value)
