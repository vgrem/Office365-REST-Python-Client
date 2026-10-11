from enum import Enum


class ExportLocation(Enum):
    responsiveLocations = "1"
    nonresponsiveLocations = "2"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.ExportLocation"
