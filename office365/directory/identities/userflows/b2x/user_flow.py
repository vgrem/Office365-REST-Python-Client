from office365.directory.identities.provider import IdentityProvider
from office365.directory.identities.userflows.language_configuration import (
    UserFlowLanguageConfiguration,
)
from office365.directory.identities.userflows.user_attribute_assignment import (
    IdentityUserFlowAttributeAssignmentCollection,
)
from office365.directory.identities.userflows.user_flow import IdentityUserFlow
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata


class B2XIdentityUserFlow(IdentityUserFlow):
    """
    Represents a self-service sign up user flow within an Azure Active Directory tenant.

    User flows are used to enable a self-service sign up experience for guest users on an application.
    User flows define the experience the end user sees while signing up, including which identity providers they can
    use to authenticate, along with which attributes are collected as part of the sign up process.
    """

    @odata(name="identityProviders")
    @property
    def identity_providers(self) -> EntityCollection[IdentityProvider]:
        """TThe identity providers included in the user flow."""
        return self.properties.get(
            "identityProviders",
            EntityCollection(
                self.context,
                IdentityProvider,
                ResourcePath("identityProviders", self.resource_path),
            ),
        )

    @property
    def languages(self) -> EntityCollection[UserFlowLanguageConfiguration]:
        """The languages supported for customization within the user flow. Language customization is enabled by default
        in self-service sign-up user flow. You cannot create custom languages in self-service sign-up user flows.
        """
        return self.properties.get(
            "languages",
            EntityCollection(
                self.context,
                UserFlowLanguageConfiguration,
                ResourcePath("languages", self.resource_path),
            ),
        )

    @odata(name="userAttributeAssignments")
    @property
    def user_attribute_assignments(
        self,
    ) -> IdentityUserFlowAttributeAssignmentCollection:
        """The user attribute assignments included in the user flow."""
        return self.properties.get(
            "userAttributeAssignments",
            IdentityUserFlowAttributeAssignmentCollection(
                self.context,
                ResourcePath("userAttributeAssignments", self.resource_path),
            ),
        )
