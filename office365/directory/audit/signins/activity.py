from office365.runtime.client_value import ClientValue


class SignInActivity(ClientValue):
    """Provides the last interactive or non-interactive sign-in time for a specific user. Since signInActivity
    describes a property of the user object, Azure AD stores sign in activity for your users for as long as the
    user object exists."""
