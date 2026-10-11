from enum import Enum


class EvidenceRole(Enum):
    unknown = "0"
    contextual = "1"
    scanned = "2"
    source = "3"
    destination = "4"
    created = "5"
    added = "6"
    compromised = "7"
    edited = "8"
    attacked = "9"
    attacker = "10"
    commandAndControl = "11"
    loaded = "12"
    suspicious = "13"
    policyViolator = "14"
    unknownFutureValue = "31"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.EvidenceRole"
