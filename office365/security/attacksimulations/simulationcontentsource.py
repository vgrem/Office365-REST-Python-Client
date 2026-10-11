from enum import Enum


class SimulationContentSource(Enum):
    unknown = "0"
    global_ = "1"
    tenant = "2"
    unknownFutureValue = "3"

    @property
    def entity_type_name(self):
        return "microsoft.graph.SimulationContentSource"
