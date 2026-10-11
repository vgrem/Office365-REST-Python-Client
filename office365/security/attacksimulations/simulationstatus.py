from enum import Enum


class SimulationStatus(Enum):
    unknown = "0"
    draft = "1"
    running = "2"
    scheduled = "3"
    succeeded = "4"
    failed = "5"
    cancelled = "6"
    excluded = "7"
    unknownFutureValue = "8"

    @property
    def entity_type_name(self):
        return "microsoft.graph.SimulationStatus"
