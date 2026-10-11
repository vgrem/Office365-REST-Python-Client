from enum import Enum


class RegistryOperation(Enum):
    unknown = "0"
    create = "1"
    modify = "2"
    delete = "3"
    unknownFutureValue = "127"

    @property
    def entity_type_name(self):
        return "microsoft.graph.RegistryOperation"
