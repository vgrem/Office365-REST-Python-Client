from office365.runtime.client_value import ClientValue


class PasswordCredential(ClientValue):
    """Represents a password credential associated with an application or a service principal.
    The passwordCredentials property of the application entity is a collection of passwordCredential objects."""

    def __init__(self, displayName=None, keyId=None):
        super(PasswordCredential, self).__init__()
        self.displayName = displayName
        self.secretText = None
        self.keyId = keyId
