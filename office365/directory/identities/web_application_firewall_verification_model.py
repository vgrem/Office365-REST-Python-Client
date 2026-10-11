from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.identities.riskPrevention.web_application_firewall_provider_type import (
        WebApplicationFirewallProviderType,
    )
    from office365.directory.identities.riskPrevention.web_application_firewall_verification_result import (
        WebApplicationFirewallVerificationResult,
    )
    from office365.directory.identities.riskPrevention.web_application_firewall_verified_details import (
        WebApplicationFirewallVerifiedDetails,
    )
    from office365.directory.identities.web_application_firewall_provider import (
        WebApplicationFirewallProvider,
    )


class WebApplicationFirewallVerificationModel(Entity):
    @property
    def provider_type(self) -> WebApplicationFirewallProviderType:
        """Gets the providerType property"""
        from office365.directory.identities.riskPrevention.web_application_firewall_provider_type import (
            WebApplicationFirewallProviderType,
        )

        return self.properties.get("providerType", WebApplicationFirewallProviderType.akamai)

    @property
    def verification_result(self) -> WebApplicationFirewallVerificationResult:
        """Gets the verificationResult property"""
        from office365.directory.identities.riskPrevention.web_application_firewall_verification_result import (
            WebApplicationFirewallVerificationResult,
        )

        return self.properties.get("verificationResult", WebApplicationFirewallVerificationResult())

    @property
    def verified_details(self) -> WebApplicationFirewallVerifiedDetails:
        """Gets the verifiedDetails property"""
        from office365.directory.identities.riskPrevention.web_application_firewall_verified_details import (
            WebApplicationFirewallVerifiedDetails,
        )

        return self.properties.get("verifiedDetails", WebApplicationFirewallVerifiedDetails())

    @property
    def verified_host(self) -> Optional[str]:
        """Gets the verifiedHost property"""
        return self.properties.get("verifiedHost", None)

    @property
    def provider(self) -> WebApplicationFirewallProvider:
        """Gets the provider property"""
        from office365.directory.identities.web_application_firewall_provider import (
            WebApplicationFirewallProvider,
        )

        return self.properties.get(
            "provider", WebApplicationFirewallProvider(self.context, ResourcePath("provider", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.WebApplicationFirewallVerificationModel"
