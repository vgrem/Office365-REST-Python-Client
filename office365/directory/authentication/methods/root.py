from office365.directory.authentication.methods.details import UserRegistrationDetails
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath


class AuthenticationMethodsRoot(Entity):
    """Container for navigation properties for Azure AD authentication methods resources."""

    @property
    def user_registration_details(self):
        """Represents the state of a user's authentication methods, including which methods are registered and which
        features the user is registered and capable of (such as multi-factor authentication, self-service password
        reset, and passwordless authentication)."""
        return self.properties.get('userRegistrationDetails',
                                   EntityCollection(self.context, UserRegistrationDetails,
                                                    ResourcePath("userRegistrationDetails", self.resource_path)))
