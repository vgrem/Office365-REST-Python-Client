from office365.directory.identitygovernance.userconsent.request_collection import UserConsentRequestCollection
from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath


class AppConsentRequest(Entity):
    """
    Represents the request that a user creates when they request the tenant admin for consent to access an app or
    to grant permissions to an app. The details include the app that the user wants access to be granted to on their
    behalf and the permissions that the user is requesting.

    The user can create a consent request when an app or a permission requires admin authorization and only when
    the admin consent workflow is enabled.
    """

    @property
    def user_consent_requests(self):
        """A list of pending user consent requests. """
        return self.properties.get('userConsentRequests',
                                   UserConsentRequestCollection(self.context,
                                                                ResourcePath("userConsentRequests",
                                                                             self.resource_path)))
