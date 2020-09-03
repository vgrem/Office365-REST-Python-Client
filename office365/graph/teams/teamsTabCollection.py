from office365.graph.teams.teamsTab import TeamsTab
from office365.runtime.client_object_collection import ClientObjectCollection


class TeamsTabCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(TeamsTabCollection, self).__init__(context, TeamsTab, resource_path)
