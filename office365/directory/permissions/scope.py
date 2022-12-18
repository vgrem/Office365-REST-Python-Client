from office365.runtime.client_value import ClientValue


class PermissionScope(ClientValue):
    """
    Represents the definition of a delegated permission.

    Delegated permissions can be requested by client applications needing an access token to the API which defined the
    permissions. Delegated permissions can be requested dynamically, using the scopes parameter in an authorization
    request to the Microsoft identity platform, or statically, through the requiredResourceAccess collection on the
    application object.
    """

    def __init__(self, admin_consent_display_name=None, admin_consent_description=None):
        """
        :param str admin_consent_display_name: The permission's title, intended to be read by an administrator granting
            the permission on behalf of all users.
        :param str admin_consent_description: A description of the delegated permissions, intended to be read
            by an administrator granting the permission on behalf of all users. This text appears in tenant-wide
            admin consent experiences.
        """
        self.adminConsentDescription = admin_consent_description
        self.adminConsentDisplayName = admin_consent_display_name
