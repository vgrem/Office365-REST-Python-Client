from enum import Enum


class PayloadComplexity(Enum):
    unknown = "0"
    low = "1"
    medium = "2"
    high = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.PayloadComplexity"
