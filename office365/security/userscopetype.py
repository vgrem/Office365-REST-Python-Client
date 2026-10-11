from enum import Enum


class UserScopeType(Enum):
    user = "1"
    group = "2"
    tenant = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.UserScopeType"
