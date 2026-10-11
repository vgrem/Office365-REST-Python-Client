from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection


@dataclass
class AnalyzedEmailRecipientDetail(ClientValue):
    ccRecipients: StringCollection = field(default_factory=StringCollection)
    domainName: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AnalyzedEmailRecipientDetail"
