from office365.directory.synchronization.progress import SynchronizationProgress
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


class SynchronizationStatus(ClientValue):
    """Represents the current status of the synchronizationJob."""

    def __init__(self, progress=None):
        """
        :param list[SynchronizationProgress] progress: Details of the progress of a job toward completion.
        """
        self.progress = ClientValueCollection(SynchronizationProgress, progress)
