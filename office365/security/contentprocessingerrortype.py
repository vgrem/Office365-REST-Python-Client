from enum import Enum


class ContentProcessingErrorType(Enum):
    transient = "0"
    permanent = "1"
    unknownFutureValue = "2"

    @property
    def entity_type_name(self):
        return "microsoft.graph.ContentProcessingErrorType"
