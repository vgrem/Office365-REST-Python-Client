from enum import Enum


class ExportFileStructure(Enum):
    none = "0"
    directory = "1"
    pst = "2"
    unknownFutureValue = "3"
    msg = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.ExportFileStructure"
