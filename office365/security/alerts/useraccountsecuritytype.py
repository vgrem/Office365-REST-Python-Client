from enum import Enum


class UserAccountSecurityType(Enum):
    unknown = "0"
    standard = "1"
    power = "2"
    administrator = "3"
    unknownFutureValue = "127"

    @property
    def entity_type_name(self):
        return "microsoft.graph.UserAccountSecurityType"
