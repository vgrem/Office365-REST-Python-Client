from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.policies.self_service_sign_up_authentication_flow_configuration import (
        SelfServiceSignUpAuthenticationFlowConfiguration,
    )


class AuthenticationFlowsPolicy(Entity):
    """
    Represents the policy configuration of self-service sign-up experience at a tenant level that lets external
    users request to sign up for approval. It contains information, such as the identifier, display name, and
    description, and indicates whether self-service sign-up is enabled for the policy.
    """

    @property
    def display_name(self) -> Optional[str]:
        """The human-readable name of the policy."""
        return self.properties.get("displayName", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def self_service_sign_up(self) -> SelfServiceSignUpAuthenticationFlowConfiguration:
        """Gets the selfServiceSignUp property"""
        from office365.directory.policies.self_service_sign_up_authentication_flow_configuration import (
            SelfServiceSignUpAuthenticationFlowConfiguration,
        )

        return self.properties.get("selfServiceSignUp", SelfServiceSignUpAuthenticationFlowConfiguration())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AuthenticationFlowsPolicy"
