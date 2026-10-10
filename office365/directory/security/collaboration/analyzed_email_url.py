from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from office365.directory.security.detonation_details import DetonationDetails
from office365.runtime.client_value import ClientValue

if TYPE_CHECKING:
    from office365.directory.security.threat_type import ThreatType


@dataclass
class AnalyzedEmailUrl(ClientValue):
    detectionMethod: str | None = None
    detonationDetails: DetonationDetails = field(default_factory=DetonationDetails)
    tenantAllowBlockListDetailInfo: str | None = None
    url: str | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AnalyzedEmailUrl"

    threatType: ThreatType = ThreatType.unknown
