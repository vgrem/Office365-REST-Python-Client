from enum import Enum


class SensorType(Enum):
    adConnectIntegrated = "1"
    adcsIntegrated = "2"
    adfsIntegrated = "3"
    domainControllerIntegrated = "4"
    domainControllerStandalone = "5"
    unknownFutureValue = "6"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.SensorType"
