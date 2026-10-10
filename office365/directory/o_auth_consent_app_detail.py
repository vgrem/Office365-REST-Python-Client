from __future__ import annotations

from dataclasses import dataclass

from office365.directory.security.attacksimulations.oauthappscope import OAuthAppScope
from office365.runtime.client_value import ClientValue


@dataclass
class OAuthConsentAppDetail(ClientValue):
    appScope: OAuthAppScope = OAuthAppScope.unknown
    displayLogo: str | None = None
    displayName: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OAuthConsentAppDetail"
