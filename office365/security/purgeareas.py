from enum import Enum


class PurgeAreas(Enum):
    mailboxes = "1"
    teamsMessages = "2"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.PurgeAreas"
