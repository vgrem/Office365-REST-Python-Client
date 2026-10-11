from enum import Enum


class SourceType(Enum):
    mailbox = "1"
    site = "2"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.SourceType"
