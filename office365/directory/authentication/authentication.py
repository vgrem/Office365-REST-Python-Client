from office365.directory.authentication.method import AuthenticationMethod
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath


class Authentication(Entity):
    """
    Exposes relationships that represent the authentication methods supported by Azure AD and that can configured
    for users.
    """

    @property
    def methods(self):
        """Represents all authentication methods registered to a user."""
        return self.properties.get('methods',
                                   EntityCollection(self.context, AuthenticationMethod,
                                                    ResourcePath("drives", self.resource_path)))

