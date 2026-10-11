from enum import Enum


class IoTDeviceImportanceType(Enum):
    unknown = "0"
    low = "1"
    normal = "2"
    high = "3"
    unknownFutureValue = "4"

    @property
    def entity_type_name(self):
        return "microsoft.graph.security.IoTDeviceImportanceType"
