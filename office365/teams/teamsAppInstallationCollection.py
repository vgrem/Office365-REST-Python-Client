from office365.runtime.client_object_collection import ClientObjectCollection
from office365.teams.teamsAppInstallation import TeamsAppInstallation


class TeamsAppInstallationCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super().__init__(context, TeamsAppInstallation, resource_path)
