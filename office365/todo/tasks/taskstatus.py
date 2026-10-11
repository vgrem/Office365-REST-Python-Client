from enum import Enum


class TaskStatus(Enum):
    notStarted = "0"
    inProgress = "1"
    completed = "2"
    waitingOnOthers = "3"
    deferred = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.TaskStatus"
