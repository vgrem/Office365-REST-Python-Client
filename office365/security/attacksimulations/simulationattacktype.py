from enum import Enum


class SimulationAttackType(Enum):
    unknown = "0"
    social = "1"
    cloud = "2"
    endpoint = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.SimulationAttackType"
