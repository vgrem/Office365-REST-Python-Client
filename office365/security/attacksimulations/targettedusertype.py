from enum import Enum


class TargettedUserType(Enum):
    unknown = "0"
    clicked = "1"
    compromised = "2"
    allUsers = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.TargettedUserType"
