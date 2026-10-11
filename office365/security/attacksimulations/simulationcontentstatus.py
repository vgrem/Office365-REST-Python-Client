from enum import Enum


class SimulationContentStatus(Enum):
    unknown = "0"
    draft = "1"
    ready = "2"
    archive = "3"
    delete = "4"
    unknownFutureValue = "5"

    @property
    def entity_type_name(self):
        return "microsoft.graph.SimulationContentStatus"
