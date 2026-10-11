from enum import Enum


class DataSourceHoldStatus(Enum):
    notApplied = "1"
    applied = "2"
    applying = "3"
    removing = "4"
    partial = "5"
    unknownFutureValue = "6"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.DataSourceHoldStatus"
