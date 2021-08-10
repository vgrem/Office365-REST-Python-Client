from office365.directory.identities.identity_user_flow import IdentityUserFlow


class B2XIdentityUserFlow(IdentityUserFlow):
    """
    Represents a self-service sign up user flow within an Azure Active Directory tenant.

    User flows are used to enable a self-service sign up experience for guest users on an application.
    User flows define the experience the end user sees while signing up, including which identity providers they can
    use to authenticate, along with which attributes are collected as part of the sign up process.
    """

    @property
    def user_flow_type(self):
        """
        The type of user flow. For self-service sign-up user flows,
        the value can only be signUpOrSignIn and cannot be modified after creation.

        :rtype: str or None
        """
        return self.properties.get('userFlowType', None)
