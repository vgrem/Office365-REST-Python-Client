from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class AuthenticationBehaviors(ClientValue):
    blockAzureADGraphAccess: bool | None = None
    removeUnverifiedEmailClaim: bool | None = None
    requireClientServicePrincipal: bool | None = None

    @property
    def entity_type_name(self):
        return "microsoft.graph.AuthenticationBehaviors"
