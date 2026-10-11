from enum import Enum


class GoogleCloudLocationType(Enum):
    unknown = "0"
    regional = "1"
    zonal = "2"
    global_ = "3"
    unknownFutureValue = "31"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.GoogleCloudLocationType"
