from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection
from office365.security.alerts.evidenceremediationstatus import EvidenceRemediationStatus
from office365.security.alerts.evidencerole import EvidenceRole
from office365.security.alerts.evidenceverdict import EvidenceVerdict


@dataclass
class AlertEvidence(ClientValue):
    """The alertEvidence base type and its derived evidence types provide a means to organize and track rich data
    about each artifact involved in an alert."""

    createdDateTime: str | None = None
    detailedRoles: StringCollection = field(default_factory=StringCollection)
    remediationStatus: EvidenceRemediationStatus = EvidenceRemediationStatus.none
    remediationStatusDetails: str | None = None
    roles: ClientValueCollection[EvidenceRole] = field(default_factory=lambda: ClientValueCollection(EvidenceRole))
    tags: StringCollection = field(default_factory=StringCollection)
    verdict: EvidenceVerdict = EvidenceVerdict.unknown

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.AlertEvidence"
