from office365.runtime.client_value_object import ClientValueObject


class UserIdInfo(ClientValueObject):

    def __init__(self):
        """Represents an identity provider’s unique identifier information."""
        super(UserIdInfo, self).__init__()
        self.NameId = None
        self.NameIdIssuer = None
