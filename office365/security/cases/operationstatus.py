from enum import Enum


class CaseOperationStatus(Enum):
    notStarted = "0"
    submissionFailed = "1"
    running = "2"
    succeeded = "3"
    partiallySucceeded = "4"
    failed = "5"
    unknownFutureValue = "6"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.CaseOperationStatus"
