from enum import Enum


class DataSourceContainerStatus(Enum):
    active = "1"
    released = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.DataSourceContainerStatus"
