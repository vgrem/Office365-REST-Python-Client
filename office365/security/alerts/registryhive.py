from enum import Enum


class RegistryHive(Enum):
    unknown = "0"
    currentConfig = "1"
    currentUser = "2"
    localMachineSam = "3"
    localMachineSecurity = "4"
    localMachineSoftware = "5"
    localMachineSystem = "6"
    usersDefault = "7"
    unknownFutureValue = "127"

    @property
    def entity_type_name(self):
        return "microsoft.graph.RegistryHive"
