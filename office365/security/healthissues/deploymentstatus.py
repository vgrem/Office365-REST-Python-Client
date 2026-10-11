from enum import Enum


class DeploymentStatus(Enum):
    upToDate = "1"
    outdated = "2"
    updating = "3"
    updateFailed = "4"
    notConfigured = "5"
    unreachable = "6"
    disconnected = "7"
    startFailure = "8"
    syncing = "9"
    unknownFutureValue = "10"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.DeploymentStatus"
