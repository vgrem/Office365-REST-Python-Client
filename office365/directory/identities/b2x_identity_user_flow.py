from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identities.provider import IdentityProvider
    from office365.directory.identities.providers.base import IdentityProviderBase
    from office365.directory.identities.userflows.language_configuration import (
        UserFlowLanguageConfiguration,
    )
    from office365.directory.identities.userflows.user_attribute_assignment import (
        IdentityUserFlowAttributeAssignment,
    )
    from office365.directory.identities.userflows.user_flow_api_connector_configuration import (
        UserFlowApiConnectorConfiguration,
    )


class B2xIdentityUserFlow(Entity):
    @property
    def api_connector_configuration(self) -> UserFlowApiConnectorConfiguration:
        """Gets the apiConnectorConfiguration property"""
        from office365.directory.identities.userflows.user_flow_api_connector_configuration import (
            UserFlowApiConnectorConfiguration,
        )

        return self.properties.get("apiConnectorConfiguration", UserFlowApiConnectorConfiguration())

    @property
    def identity_providers(self) -> EntityCollection[IdentityProvider]:
        """Gets the identityProviders property"""
        from office365.directory.identities.provider import IdentityProvider

        return self.properties.get(
            "identityProviders",
            EntityCollection[IdentityProvider](
                self.context, IdentityProvider, ResourcePath("identityProviders", self.resource_path)
            ),
        )

    @property
    def languages(self) -> EntityCollection[UserFlowLanguageConfiguration]:
        """Gets the languages property"""
        from office365.directory.identities.userflows.language_configuration import (
            UserFlowLanguageConfiguration,
        )

        return self.properties.get(
            "languages",
            EntityCollection[UserFlowLanguageConfiguration](
                self.context, UserFlowLanguageConfiguration, ResourcePath("languages", self.resource_path)
            ),
        )

    @property
    def user_attribute_assignments(self) -> EntityCollection[IdentityUserFlowAttributeAssignment]:
        """Gets the userAttributeAssignments property"""
        from office365.directory.identities.userflows.user_attribute_assignment import (
            IdentityUserFlowAttributeAssignment,
        )

        return self.properties.get(
            "userAttributeAssignments",
            EntityCollection[IdentityUserFlowAttributeAssignment](
                self.context,
                IdentityUserFlowAttributeAssignment,
                ResourcePath("userAttributeAssignments", self.resource_path),
            ),
        )

    @property
    def user_flow_identity_providers(self) -> EntityCollection[IdentityProviderBase]:
        """Gets the userFlowIdentityProviders property"""
        from office365.directory.identities.providers.base import IdentityProviderBase

        return self.properties.get(
            "userFlowIdentityProviders",
            EntityCollection[IdentityProviderBase](
                self.context, IdentityProviderBase, ResourcePath("userFlowIdentityProviders", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.B2xIdentityUserFlow"
