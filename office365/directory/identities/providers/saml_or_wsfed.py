from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.directory.identities.providers.base import IdentityProviderBase

if TYPE_CHECKING:
    from office365.directory.authentication.protocol import AuthenticationProtocol


class SamlOrWsFedProvider(IdentityProviderBase):
    """An abstract type that provides configuration details for setting up a SAML or WS-Fed external domain-based
    identity provider (IdP)."""

    @property
    def issuer_uri(self) -> Optional[str]:
        """Issuer URI of the federation server."""
        return self.properties.get("issuerUri", None)

    @property
    def metadata_exchange_uri(self) -> Optional[str]:
        """Gets the metadataExchangeUri property"""
        return self.properties.get("metadataExchangeUri", None)

    @property
    def passive_sign_in_uri(self) -> Optional[str]:
        """Gets the passiveSignInUri property"""
        return self.properties.get("passiveSignInUri", None)

    @property
    def preferred_authentication_protocol(self) -> AuthenticationProtocol:
        """Gets the preferredAuthenticationProtocol property"""
        from office365.directory.authentication.protocol import AuthenticationProtocol

        return self.properties.get("preferredAuthenticationProtocol", AuthenticationProtocol.wsFed)

    @property
    def signing_certificate(self) -> Optional[str]:
        """Gets the signingCertificate property"""
        return self.properties.get("signingCertificate", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SamlOrWsFedProvider"
