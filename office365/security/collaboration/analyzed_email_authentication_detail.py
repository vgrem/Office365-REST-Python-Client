from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class AnalyzedEmailAuthenticationDetail(ClientValue):
    compositeAuthentication: str | None = None
    dkim: str | None = None
    dmarc: str | None = None
    senderPolicyFramework: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AnalyzedEmailAuthenticationDetail"
