from __future__ import annotations

from dataclasses import dataclass, field

from office365.directory.security.detonation_details import DetonationDetails
from office365.runtime.client_value import ClientValue


@dataclass
class AnalyzedEmailUrl(ClientValue):
    detectionMethod: str | None = None
    detonationDetails: DetonationDetails = field(default_factory=DetonationDetails)
    tenantAllowBlockListDetailInfo: str | None = None
    url: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AnalyzedEmailUrl"
