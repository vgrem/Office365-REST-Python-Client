from enum import Enum


class HealthIssueType(Enum):
    sensor = "1"
    global_ = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.HealthIssueType"
