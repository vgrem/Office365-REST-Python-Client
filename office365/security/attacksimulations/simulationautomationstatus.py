from enum import Enum


class SimulationAutomationStatus(Enum):
    unknown = "0"
    draft = "1"
    notRunning = "2"
    running = "3"
    completed = "4"
    unknownFutureValue = "5"

    @property
    def entity_type_name(self):
        return "microsoft.graph.SimulationAutomationStatus"
