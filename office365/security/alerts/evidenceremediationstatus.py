from enum import Enum


class EvidenceRemediationStatus(Enum):
    none = "0"
    remediated = "1"
    prevented = "2"
    blocked = "3"
    notFound = "4"
    unknownFutureValue = "5"
    active = "6"
    pendingApproval = "7"
    declined = "8"
    unremediated = "9"
    running = "10"
    partiallyRemediated = "11"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.EvidenceRemediationStatus"
