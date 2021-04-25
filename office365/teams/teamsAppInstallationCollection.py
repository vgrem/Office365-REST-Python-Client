from office365.entity_collection import EntityCollection
from office365.teams.teamsAppInstallation import TeamsAppInstallation


class TeamsAppInstallationCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(TeamsAppInstallationCollection, self).__init__(context, TeamsAppInstallation, resource_path)
