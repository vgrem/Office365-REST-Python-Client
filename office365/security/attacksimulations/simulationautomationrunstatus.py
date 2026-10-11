from enum import Enum


class SimulationAutomationRunStatus(Enum):
    unknown = "0"
    running = "1"
    succeeded = "2"
    failed = "3"
    skipped = "4"
    unknownFutureValue = "5"

    @property
    def entity_type_name(self):
        return "microsoft.graph.SimulationAutomationRunStatus"
