from office365.graph.teams.teamsAsyncOperation import TeamsAsyncOperation
from office365.runtime.client_object_collection import ClientObjectCollection


class TeamsAsyncOperationCollection(ClientObjectCollection):
    """TeamsAsyncOperation's collection"""

    def __init__(self, context, resource_path=None):
        super(TeamsAsyncOperationCollection, self).__init__(context, TeamsAsyncOperation, resource_path)
