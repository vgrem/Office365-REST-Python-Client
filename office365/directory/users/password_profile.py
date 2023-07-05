from office365.runtime.client_value import ClientValue


class PasswordProfile(ClientValue):
    """Contains the password profile associated with a user. The passwordProfile property of the user entity is a
    passwordProfile object. """
    def __init__(self, password=None, force_change_password_next_sign_in=None):
        """
        :param str password:
        :param bool force_change_password_next_sign_in:
        """
        super(PasswordProfile, self).__init__()
        self.password = password
        self.forceChangePasswordNextSignIn = force_change_password_next_sign_in
