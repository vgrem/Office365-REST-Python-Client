from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity

if TYPE_CHECKING:
    from office365.directory.authentication.oidc_client_authentication import (
        OidcClientAuthentication,
    )
    from office365.directory.authentication.oidc_inbound_claim_mapping_override import (
        OidcInboundClaimMappingOverride,
    )
    from office365.directory.identities.providers.oidc_response_type import (
        OidcResponseType,
    )


class OidcIdentityProvider(Entity):
    @property
    def client_authentication(self) -> OidcClientAuthentication:
        """Gets the clientAuthentication property"""
        from office365.directory.authentication.oidc_client_authentication import (
            OidcClientAuthentication,
        )

        return self.properties.get("clientAuthentication", OidcClientAuthentication())

    @property
    def client_id(self) -> Optional[str]:
        """Gets the clientId property"""
        return self.properties.get("clientId", None)

    @property
    def inbound_claim_mapping(self) -> OidcInboundClaimMappingOverride:
        """Gets the inboundClaimMapping property"""
        from office365.directory.authentication.oidc_inbound_claim_mapping_override import (
            OidcInboundClaimMappingOverride,
        )

        return self.properties.get("inboundClaimMapping", OidcInboundClaimMappingOverride())

    @property
    def issuer(self) -> Optional[str]:
        """Gets the issuer property"""
        return self.properties.get("issuer", None)

    @property
    def response_type(self) -> OidcResponseType:
        """Gets the responseType property"""
        from office365.directory.identities.providers.oidc_response_type import (
            OidcResponseType,
        )

        return self.properties.get("responseType", OidcResponseType.code)

    @property
    def scope(self) -> Optional[str]:
        """Gets the scope property"""
        return self.properties.get("scope", None)

    @property
    def well_known_endpoint(self) -> Optional[str]:
        """Gets the wellKnownEndpoint property"""
        return self.properties.get("wellKnownEndpoint", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OidcIdentityProvider"
