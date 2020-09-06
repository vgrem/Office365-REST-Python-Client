from office365.runtime.client_object_collection import ClientObjectCollection
from office365.teams.teamsTab import TeamsTab


class TeamsTabCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(TeamsTabCollection, self).__init__(context, TeamsTab, resource_path)
