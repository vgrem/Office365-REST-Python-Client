from enum import Enum


class StatisticsOptions(Enum):
    includeRefiners = "1"
    includeQueryStats = "2"
    includeUnindexedStats = "4"
    advancedIndexing = "8"
    locationsWithoutHits = "16"
    unknownFutureValue = "32"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.StatisticsOptions"
