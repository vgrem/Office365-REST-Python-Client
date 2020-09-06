from office365.runtime.client_object_collection import ClientObjectCollection
from office365.teams.teamsAsyncOperation import TeamsAsyncOperation


class TeamsAsyncOperationCollection(ClientObjectCollection):
    """TeamsAsyncOperation's collection"""

    def __init__(self, context, resource_path=None):
        super(TeamsAsyncOperationCollection, self).__init__(context, TeamsAsyncOperation, resource_path)
