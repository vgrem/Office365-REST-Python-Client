from office365.runtime.client_value import ClientValue


class PasswordCredential(ClientValue):
    """Represents a password credential associated with an application or a service principal.
    The passwordCredentials property of the application entity is a collection of passwordCredential objects."""

    def __init__(self, display_name=None, key_id=None):
        super(PasswordCredential, self).__init__()
        self.displayName = display_name
        self.secretText = None
        self.keyId = key_id
