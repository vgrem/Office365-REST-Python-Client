from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from office365.runtime.client_value import ClientValue


@dataclass
class AnalyzedEmailSenderDetail(ClientValue):
    displayName: str | None = None
    domainCreationDateTime: datetime | None = field(default_factory=lambda: datetime.min)
    domainName: str | None = None
    domainOwner: str | None = None
    fromAddress: str | None = None
    ipv4: str | None = None
    location: str | None = None
    mailFromAddress: str | None = None
    mailFromDomainName: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AnalyzedEmailSenderDetail"
