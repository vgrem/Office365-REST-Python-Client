from office365.entity_collection import EntityCollection
from office365.teams.teamsTab import TeamsTab


class TeamsTabCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(TeamsTabCollection, self).__init__(context, TeamsTab, resource_path)
