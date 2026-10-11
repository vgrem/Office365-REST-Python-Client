from __future__ import annotations

from typing import TYPE_CHECKING

from office365.directory.authentication.conditions.event_listener import (
    AuthenticationEventListener,
)
from office365.directory.identities.api_connector import IdentityApiConnector
from office365.directory.identities.conditional_access_root import ConditionalAccessRoot
from office365.directory.identities.providers.base_collection import (
    IdentityProviderBaseCollection,
)
from office365.directory.identities.userflows.attribute import IdentityUserFlowAttribute
from office365.directory.identities.userflows.b2x.user_flow import B2XIdentityUserFlow
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata
from office365.security.health_issue import HealthIssue
from office365.security.identity_accounts import IdentityAccounts
from office365.security.sensor import Sensor
from office365.security.sensor_candidate import SensorCandidate
from office365.security.sensor_candidate_activation_configuration import (
    SensorCandidateActivationConfiguration,
)
from office365.security.settings_container import SettingsContainer

if TYPE_CHECKING:
    from office365.common.custom_authentication_extension import (
        CustomAuthenticationExtension,
    )
    from office365.directory.identities.authentication_events_flow import (
        AuthenticationEventsFlow,
    )
    from office365.directory.identities.riskPrevention.container import (
        RiskPreventionContainer,
    )
    from office365.directory.identities.verified_id_root import IdentityVerifiedIdRoot


class IdentityContainer(Entity):
    """
    Represents the entry point to different features in External Identities for
    both Azure Active Directory (Azure AD) and Azure AD B2C tenants.
    """

    @odata(name="apiConnectors")
    @property
    def api_connectors(self) -> EntityCollection[IdentityApiConnector]:
        """Represents entry point for API connectors."""
        return self.properties.get(
            "apiConnectors",
            EntityCollection(self.context, IdentityApiConnector, ResourcePath("apiConnectors", self.resource_path)),
        )

    @odata(name="authenticationEventListeners")
    @property
    def authentication_event_listeners(self) -> EntityCollection[AuthenticationEventListener]:
        """Get the collection of authenticationListener resources supported by the onSignupStart event."""
        return self.properties.get(
            "authenticationEventListeners",
            EntityCollection(
                self.context,
                AuthenticationEventListener,
                ResourcePath("authenticationEventListeners", self.resource_path),
            ),
        )

    @odata(name="conditionalAccess")
    @property
    def conditional_access(self) -> ConditionalAccessRoot:
        """The entry point for the Conditional Access (CA) object model."""
        return self.properties.get(
            "conditionalAccess",
            ConditionalAccessRoot(self.context, ResourcePath("conditionalAccess", self.resource_path)),
        )

    @odata(name="identityProviders")
    @property
    def identity_providers(self) -> IdentityProviderBaseCollection:
        """Represents entry point for identity provider base."""
        return self.properties.get(
            "identityProviders",
            IdentityProviderBaseCollection(self.context, ResourcePath("identityProviders", self.resource_path)),
        )

    @odata(name="b2xUserFlows")
    @property
    def b2x_user_flows(self) -> EntityCollection[B2XIdentityUserFlow]:
        """Represents entry point for B2X/self-service sign-up identity userflows."""
        return self.properties.get(
            "b2xUserFlows",
            EntityCollection(self.context, B2XIdentityUserFlow, ResourcePath("b2xUserFlows", self.resource_path)),
        )

    @odata(name="userFlowAttributes")
    @property
    def user_flow_attributes(self) -> EntityCollection[IdentityUserFlowAttribute]:
        """Represents entry point for identity userflow attributes."""
        return self.properties.get(
            "userFlowAttributes",
            EntityCollection(
                self.context, IdentityUserFlowAttribute, ResourcePath("userFlowAttributes", self.resource_path)
            ),
        )

    @property
    def health_issues(self) -> EntityCollection[HealthIssue]:
        """Gets the healthIssues property"""
        return self.properties.get(
            "healthIssues",
            EntityCollection[HealthIssue](self.context, HealthIssue, ResourcePath("healthIssues", self.resource_path)),
        )

    @property
    def identity_accounts(self) -> EntityCollection[IdentityAccounts]:
        """Gets the identityAccounts property"""
        return self.properties.get(
            "identityAccounts",
            EntityCollection[IdentityAccounts](
                self.context, IdentityAccounts, ResourcePath("identityAccounts", self.resource_path)
            ),
        )

    @property
    def sensor_candidate_activation_configuration(self) -> SensorCandidateActivationConfiguration:
        """Gets the sensorCandidateActivationConfiguration property"""
        return self.properties.get(
            "sensorCandidateActivationConfiguration",
            SensorCandidateActivationConfiguration(
                self.context, ResourcePath("sensorCandidateActivationConfiguration", self.resource_path)
            ),
        )

    @property
    def sensor_candidates(self) -> EntityCollection[SensorCandidate]:
        """Gets the sensorCandidates property"""
        return self.properties.get(
            "sensorCandidates",
            EntityCollection[SensorCandidate](
                self.context, SensorCandidate, ResourcePath("sensorCandidates", self.resource_path)
            ),
        )

    @property
    def sensors(self) -> EntityCollection[Sensor]:
        """Gets the sensors property"""
        return self.properties.get(
            "sensors", EntityCollection[Sensor](self.context, Sensor, ResourcePath("sensors", self.resource_path))
        )

    @property
    def settings(self) -> SettingsContainer:
        """Gets the settings property"""
        return self.properties.get(
            "settings", SettingsContainer(self.context, ResourcePath("settings", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.IdentityContainer"

    @property
    def authentication_events_flows(self) -> EntityCollection[AuthenticationEventsFlow]:
        """Gets the authenticationEventsFlows property"""
        from office365.directory.identities.authentication_events_flow import (
            AuthenticationEventsFlow,
        )

        return self.properties.get(
            "authenticationEventsFlows",
            EntityCollection[AuthenticationEventsFlow](
                self.context, AuthenticationEventsFlow, ResourcePath("authenticationEventsFlows", self.resource_path)
            ),
        )

    @property
    def custom_authentication_extensions(self) -> EntityCollection[CustomAuthenticationExtension]:
        """Gets the customAuthenticationExtensions property"""
        from office365.common.custom_authentication_extension import (
            CustomAuthenticationExtension,
        )

        return self.properties.get(
            "customAuthenticationExtensions",
            EntityCollection[CustomAuthenticationExtension](
                self.context,
                CustomAuthenticationExtension,
                ResourcePath("customAuthenticationExtensions", self.resource_path),
            ),
        )

    @property
    def risk_prevention(self) -> RiskPreventionContainer:
        """Gets the riskPrevention property"""
        from office365.directory.identities.riskPrevention.container import (
            RiskPreventionContainer,
        )

        return self.properties.get(
            "riskPrevention", RiskPreventionContainer(self.context, ResourcePath("riskPrevention", self.resource_path))
        )

    @property
    def verified_id(self) -> IdentityVerifiedIdRoot:
        """Gets the verifiedId property"""
        from office365.directory.identities.verified_id_root import IdentityVerifiedIdRoot

        return self.properties.get(
            "verifiedId", IdentityVerifiedIdRoot(self.context, ResourcePath("verifiedId", self.resource_path))
        )
