from enum import Enum


class AttackSimulationOperationType(Enum):
    createSimualation = "0"
    updateSimulation = "1"
    unknownFutureValue = "2"

    @property
    def entity_type_name(self):
        return "microsoft.graph.AttackSimulationOperationType"
