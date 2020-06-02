from office365.runtime.client_value_object import ClientValueObject


class PasswordProfile(ClientValueObject):
    """Contains the password profile associated with a user. The passwordProfile property of the user entity is a
    passwordProfile object. """
    def __init__(self, password):
        super(PasswordProfile, self).__init__()
        self.password = password
        self.forceChangePasswordNextSignIn = True
