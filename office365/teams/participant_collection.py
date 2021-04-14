from office365.runtime.client_object_collection import ClientObjectCollection
from office365.teams.participant import Participant


class ParticipantCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(ParticipantCollection, self).__init__(context, Participant, resource_path)
