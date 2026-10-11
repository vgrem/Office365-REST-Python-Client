from enum import Enum


class ExportFormat(Enum):
    pst = "0"
    msg = "1"
    eml = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.ExportFormat"
