from office365.entity import Entity


class UserRegistrationDetails(Entity):
    """Represents the state of a user's authentication methods, including which methods are registered and which
    features the user is registered and capable of (such as multi-factor authentication, self-service password reset,
    and passwordless authentication)."""

    @property
    def is_admin(self):
        """
        Indicates whether the user has an admin role in the tenant. This value can be used to check the authentication
        methods that privileged accounts are registered for and capable of.
        :rtype: bool
        """
        return self.properties.get("isAdmin", None)

    @property
    def is_mfa_registered(self):
        """
        Indicates whether the user has registered a strong authentication method for multi-factor authentication.
        The method may not necessarily be allowed by the authentication methods policy.
        :rtype: bool
        """
        return self.properties.get("isMfaRegistered", None)
