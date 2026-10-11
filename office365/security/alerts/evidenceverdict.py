from enum import Enum


class EvidenceVerdict(Enum):
    unknown = "0"
    suspicious = "1"
    malicious = "2"
    noThreatsFound = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.EvidenceVerdict"
