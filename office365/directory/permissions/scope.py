from office365.runtime.client_value import ClientValue


class PermissionScope(ClientValue):
    """
    Represents the definition of a delegated permission.

    Delegated permissions can be requested by client applications needing an access token to the API which defined the
    permissions. Delegated permissions can be requested dynamically, using the scopes parameter in an authorization
    request to the Microsoft identity platform, or statically, through the requiredResourceAccess collection on the
    application object.
    """
