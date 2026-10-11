from enum import Enum


class ItemsToInclude(Enum):
    searchHits = "1"
    partiallyIndexed = "2"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.ItemsToInclude"
