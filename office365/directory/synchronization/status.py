from office365.directory.synchronization.progress import SynchronizationProgress
from office365.directory.synchronization.quarantine import SynchronizationQuarantine
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


class SynchronizationStatus(ClientValue):
    """Represents the current status of the synchronizationJob."""

    def __init__(self, progress=None, quarantine=SynchronizationQuarantine()):
        """
        :param list[SynchronizationProgress] progress: Details of the progress of a job toward completion.
        :param SynchronizationQuarantine quarantine:
        """
        self.progress = ClientValueCollection(SynchronizationProgress, progress)
        self.quarantine = quarantine
