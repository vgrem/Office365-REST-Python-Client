from enum import Enum


class HealthIssueStatus(Enum):
    open = "1"
    closed = "2"
    suppressed = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.HealthIssueStatus"
