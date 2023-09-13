from office365.entity import Entity


class AppConsentRequest(Entity):
    """
    Represents the request that a user creates when they request the tenant admin for consent to access an app or
    to grant permissions to an app. The details include the app that the user wants access to be granted to on their
    behalf and the permissions that the user is requesting.

    The user can create a consent request when an app or a permission requires admin authorization and only when
    the admin consent workflow is enabled.
    """
