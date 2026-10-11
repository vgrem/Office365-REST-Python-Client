from enum import Enum


class ReviewSetSettings(Enum):
    none = "0"
    disableGrouping = "1"
    unknownFutureValue = "2"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.ReviewSetSettings"
