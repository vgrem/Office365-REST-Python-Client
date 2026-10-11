from enum import Enum


class IncidentStatus(Enum):
    active = "1"
    resolved = "2"
    inProgress = "4"
    redirected = "64"
    unknownFutureValue = "127"
    awaitingAction = "128"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.IncidentStatus"
