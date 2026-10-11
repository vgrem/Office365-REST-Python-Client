from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.authentication.fraud_protection_provider import (
        FraudProtectionProvider,
    )
    from office365.directory.identities.web_application_firewall_provider import (
        WebApplicationFirewallProvider,
    )
    from office365.directory.identities.web_application_firewall_verification_model import (
        WebApplicationFirewallVerificationModel,
    )


class RiskPreventionContainer(Entity):
    @property
    def fraud_protection_providers(self) -> EntityCollection[FraudProtectionProvider]:
        """Gets the fraudProtectionProviders property"""
        from office365.directory.authentication.fraud_protection_provider import (
            FraudProtectionProvider,
        )

        return self.properties.get(
            "fraudProtectionProviders",
            EntityCollection[FraudProtectionProvider](
                self.context, FraudProtectionProvider, ResourcePath("fraudProtectionProviders", self.resource_path)
            ),
        )

    @property
    def web_application_firewall_providers(self) -> EntityCollection[WebApplicationFirewallProvider]:
        """Gets the webApplicationFirewallProviders property"""
        from office365.directory.identities.web_application_firewall_provider import (
            WebApplicationFirewallProvider,
        )

        return self.properties.get(
            "webApplicationFirewallProviders",
            EntityCollection[WebApplicationFirewallProvider](
                self.context,
                WebApplicationFirewallProvider,
                ResourcePath("webApplicationFirewallProviders", self.resource_path),
            ),
        )

    @property
    def web_application_firewall_verifications(self) -> EntityCollection[WebApplicationFirewallVerificationModel]:
        """Gets the webApplicationFirewallVerifications property"""
        from office365.directory.identities.web_application_firewall_verification_model import (
            WebApplicationFirewallVerificationModel,
        )

        return self.properties.get(
            "webApplicationFirewallVerifications",
            EntityCollection[WebApplicationFirewallVerificationModel](
                self.context,
                WebApplicationFirewallVerificationModel,
                ResourcePath("webApplicationFirewallVerifications", self.resource_path),
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.RiskPreventionContainer"
