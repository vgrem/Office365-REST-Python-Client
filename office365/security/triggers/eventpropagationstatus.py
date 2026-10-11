from enum import Enum


class EventPropagationStatus(Enum):
    none = "0"
    inProcessing = "1"
    failed = "2"
    success = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.EventPropagationStatus"
