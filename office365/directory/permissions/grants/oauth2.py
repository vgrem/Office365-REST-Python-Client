from office365.entity import Entity


class OAuth2PermissionGrant(Entity):
    """
    Represents the delegated permissions that have been granted to an application's service principal.

    Delegated permissions grants can be created as a result of a user consenting the an application's request
    to access an API, or created directly.

    Delegated permissions are sometimes referred to as "OAuth 2.0 scopes" or "scopes".
    """
