from enum import Enum


class RetentionTrigger(Enum):
    """ """

    none = "-1"
    dateLabeled = "0"
    dateCreated = "1"
    dateModified = "2"
    dateOfEvent = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.RetentionTrigger"
