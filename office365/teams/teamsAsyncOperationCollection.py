from office365.entity_collection import EntityCollection
from office365.teams.teamsAsyncOperation import TeamsAsyncOperation


class TeamsAsyncOperationCollection(EntityCollection):
    """TeamsAsyncOperation's collection"""

    def __init__(self, context, resource_path=None):
        super(TeamsAsyncOperationCollection, self).__init__(context, TeamsAsyncOperation, resource_path)
