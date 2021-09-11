from office365.entity import Entity


class IdentityProviderBase(Entity):
    """
    Represents identity providers with External Identities for both Azure Active Directory tenant and
    an Azure AD B2C tenant.
    """

    @property
    def display_name(self):
        """
        The display name for the identity provider.

        :rtype: str or None
        """
        return self.properties.get('displayName', None)
