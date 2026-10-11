from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class OauthApplicationEvidence(ClientValue):
    appId: str | None = None
    displayName: str | None = None
    objectId: str | None = None
    publisher: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.OauthApplicationEvidence"
