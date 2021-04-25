from office365.entity_collection import EntityCollection
from office365.teams.participant import Participant


class ParticipantCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(ParticipantCollection, self).__init__(context, Participant, resource_path)
