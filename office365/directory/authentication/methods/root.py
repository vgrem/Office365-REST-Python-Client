from office365.directory.authentication.methods.details import UserRegistrationDetails
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.reports.userregistration.method_summary import (
    UserRegistrationMethodSummary,
)
from office365.runtime.client_result import ClientResult
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery


class AuthenticationMethodsRoot(Entity):
    """Container for navigation properties for Azure AD authentication methods resources."""

    def users_registered_by_method(self):
        """Get the number of users registered for each authentication method."""
        return_type = ClientResult(self.context, UserRegistrationMethodSummary())
        qry = FunctionQuery(self, "usersRegisteredByMethod", None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def user_registration_details(self):
        """Represents the state of a user's authentication methods, including which methods are registered and which
        features the user is registered and capable of (such as multi-factor authentication, self-service password
        reset, and passwordless authentication)."""
        return self.properties.get(
            "userRegistrationDetails",
            EntityCollection(
                self.context,
                UserRegistrationDetails,
                ResourcePath("userRegistrationDetails", self.resource_path),
            ),
        )
