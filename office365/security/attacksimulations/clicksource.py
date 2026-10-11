from enum import Enum


class ClickSource(Enum):
    unknown = "0"
    qrCode = "1"
    phishingUrl = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self):
        return "microsoft.graph.ClickSource"
