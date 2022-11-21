from office365.directory.authentication.methods.method import AuthenticationMethod


class PasswordAuthenticationMethod(AuthenticationMethod):
    """A representation of a user's password. For security, the password itself will never be returned in the object,
    but action can be taken to reset a password."""
